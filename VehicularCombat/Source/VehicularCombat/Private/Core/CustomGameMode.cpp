// Copyright 2022 Danial Kamali. All Rights Reserved.

#include "CustomGameMode.h"
#include "AI/VehicleBotController.h"
#include "Actors/WeaponPickupActor.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
#include "TimerManager.h"
#include "Pawns/PlayerWheeledVehiclePawn.h"
#include "Components/HealthComponent.h"

void ACustomGameMode::InitGame(const FString& MapName, const FString& Options, FString& ErrorMessage)
{
	Super::InitGame(MapName, Options, ErrorMessage);
	TrainingBotCount = FMath::Clamp(UGameplayStatics::GetIntOption(Options, TEXT("Bots"), 0), 0, 6);
	const FString Choice=UGameplayStatics::ParseOption(Options,TEXT("Vehicle"));
	bMaskFleet=Choice==TEXT("Thunderhawk") || Choice==TEXT("Rhino") || Choice==TEXT("Hurricane");
	if (bMaskFleet)
	{
		const FString Path=FString::Printf(TEXT("/Game/MASK/%s/BP_%s.BP_%s_C"),*Choice,*Choice,*Choice);
		if (auto* Class=LoadClass<APawn>(nullptr,*Path)) { DefaultPawnClass=Class; }
		else { ErrorMessage=TEXT("Selected MASK vehicle assets are missing."); }
	}
}

UClass* ACustomGameMode::GetDefaultPawnClassForController_Implementation(AController* InController)
{
	if(const auto* Saved=VehicleClasses.Find(InController);Saved && *Saved) { return *Saved; }
	if(bMaskFleet)
	{
		if(const auto* Bot=Cast<AVehicleBotController>(InController))
		{
			const TCHAR* Paths[]={TEXT("/Game/MASK/Rhino/BP_Rhino.BP_Rhino_C"),TEXT("/Game/MASK/Hurricane/BP_Hurricane.BP_Hurricane_C"),TEXT("/Game/MASK/Thunderhawk/BP_Thunderhawk.BP_Thunderhawk_C")};
			const TCHAR* Path=Paths[Bot->TrainingIndex%3];
			if(auto* Class=LoadClass<APawn>(nullptr,Path)) { return Class; }
		}
	}
	return Super::GetDefaultPawnClassForController_Implementation(InController);
}

void ACustomGameMode::CyclePlayerVehicle(APlayerController* Player,int32 Direction)
{
	auto* Previous=Player?Cast<APlayerWheeledVehiclePawn>(Player->GetPawn()):nullptr;
	if(!Previous || Previous->IsPauseMenuOpen()) { return; }
	const double Now=GetWorld()->GetTimeSeconds();
	if(const double* Last=VehicleSwitchTimes.Find(Player);Last && Now-*Last<.35) { return; }
	TArray<APlayerWheeledVehiclePawn*> Fleet;
	for(TActorIterator<APlayerWheeledVehiclePawn> It(GetWorld());It;++It)
	{
		const auto* Health=It->FindComponentByClass<UHealthComponent>();
		if(!It->IsActorBeingDestroyed() && It->IsAvailableToSwitch() && Health && Health->CurrentHealth>0.f &&
			(*It==Previous || Cast<AVehicleBotController>(It->GetController()))) { Fleet.Add(*It); }
	}
	// UObject IDs are recycled after destruction/GC. Keep each Rhino beside its
	// rear module, with a predictable family order even after network respawns.
	Fleet.Sort([](const APlayerWheeledVehiclePawn& A,const APlayerWheeledVehiclePawn& B)
	{ return A.FleetSelectionGroup()==B.FleetSelectionGroup()?A.GetFName().LexicalLess(B.GetFName()):A.FleetSelectionGroup()<B.FleetSelectionGroup(); });
	if(Fleet.Num()<2) { Previous->ClientVehicleSwitchFeedback(TEXT("Aucun autre vehicule IA disponible"));return; }
	const int32 Current=Fleet.IndexOfByKey(Previous);
	auto* Next=Fleet[(Current+(Direction>0?1:Fleet.Num()-1))%Fleet.Num()];
	SwitchPlayerVehicleTo(Player,Next);
}

void ACustomGameMode::RememberPlayerVehicle(APlayerController* Player,APlayerWheeledVehiclePawn* Vehicle)
{
	if(Player && Vehicle) { VehicleClasses.Add(Player,Vehicle->GetClass()); }
}

bool ACustomGameMode::SwitchPlayerVehicleTo(APlayerController* Player,APlayerWheeledVehiclePawn* Next)
{
	auto* Previous=Player?Cast<APlayerWheeledVehiclePawn>(Player->GetPawn()):nullptr;
	if(!Previous || !Next || Previous==Next || !Next->IsAvailableToSwitch()) { return false; }
	auto* Bot=Cast<AVehicleBotController>(Next->GetController());
	if(!Bot) { return false; }
	// Snapshot each loadout through UnPossessed before changing either controller.
	// Pawn, crew, health, ammo, transform state and physical velocity stay in place.
	Player->UnPossess();Bot->UnPossess();Player->Possess(Next);Bot->Possess(Previous);
	if(Player->GetPawn()!=Next || Bot->GetPawn()!=Previous)
	{
		Player->UnPossess();Bot->UnPossess();Player->Possess(Previous);Bot->Possess(Next);
		Previous->ClientVehicleSwitchFeedback(TEXT("Changement impossible ; controle restaure"));return false;
	}
	VehicleClasses.Add(Player,Next->GetClass());VehicleClasses.Add(Bot,Previous->GetClass());VehicleSwitchTimes.Add(Player,GetWorld()->GetTimeSeconds());
	UE_LOG(LogTemp,Display,TEXT("MASK_FLEET player=%s from=%s to=%s ai=%s"),*Player->GetName(),*Previous->GetName(),*Next->GetName(),*Bot->GetName());
	return true;
}

void ACustomGameMode::BeginPlay()
{
	Super::BeginPlay();
	if (TrainingBotCount > 0)
	{
		FTimerHandle Handle;
		GetWorldTimerManager().SetTimer(Handle, this, &ACustomGameMode::SpawnTrainingBots, 2.f, false);
	}
}

void ACustomGameMode::SpawnTrainingBots()
{
	for (int32 Index = 0; Index < TrainingBotCount; ++Index)
	{
		auto* Bot = GetWorld()->SpawnActor<AVehicleBotController>();
		if (Bot) { Bot->TrainingIndex = Index; RestartPlayer(Bot); }
	}
	UE_LOG(LogTemp, Display, TEXT("VC_TRAINING started bots=%d"), TrainingBotCount);
}

void ACustomGameMode::RestartPlayer(AController* NewPlayer)
{
	auto* Bot = Cast<AVehicleBotController>(NewPlayer);
	APawn* Human = GetWorld()->GetFirstPlayerController() ? GetWorld()->GetFirstPlayerController()->GetPawn() : nullptr;
	if (!Bot || !Human) { Super::RestartPlayer(NewPlayer); return; }
	FCollisionQueryParams Query(SCENE_QUERY_STAT(TrainingSpawn), false);
	for (TActorIterator<APawn> It(GetWorld()); It; ++It) { Query.AddIgnoredActor(*It); }
	for (TActorIterator<AWeaponPickupActor> It(GetWorld()); It; ++It) { Query.AddIgnoredActor(*It); }
	const FVector Center = Human->GetActorLocation();
	for (int32 Attempt = 0; Attempt < 32; ++Attempt)
	{
		const float Angle = 2.f * PI * (static_cast<float>(Bot->TrainingIndex) / FMath::Max(1, TrainingBotCount) + Attempt / 16.f);
		FVector Position = Center + FVector(FMath::Cos(Angle), FMath::Sin(Angle), 0) * (Attempt < 16 ? 2400.f : 3400.f);
		float Low = BIG_NUMBER, High = -BIG_NUMBER;
		bool bClear = true;
		for (const FVector Offset : {FVector::ZeroVector, FVector(250,150,0), FVector(250,-150,0), FVector(-250,150,0), FVector(-250,-150,0)})
		{
			FHitResult Hit;
			if (!GetWorld()->LineTraceSingleByChannel(Hit, Position + Offset + FVector(0,0,500), Position + Offset - FVector(0,0,1000), ECC_Visibility, Query)
				|| Hit.ImpactNormal.Z < 0.97f || FMath::Abs(Hit.ImpactPoint.Z - Center.Z) > 250.f) { bClear = false; break; }
			Low = FMath::Min(Low, static_cast<float>(Hit.ImpactPoint.Z)); High = FMath::Max(High, static_cast<float>(Hit.ImpactPoint.Z));
		}
		if (!bClear || High - Low > 30.f) { continue; }
		Position.Z = High + 100.f;
		bool bOccupied = false;
		for (TActorIterator<APawn> It(GetWorld()); It; ++It) { bOccupied |= FVector::Dist2D(It->GetActorLocation(), Position) < 700.f; }
		if (bOccupied) { continue; }
		RestartPlayerAtTransform(Bot, FTransform(FRotator(0,(Center - Position).Rotation().Yaw,0), Position));
		if (Bot->GetPawn()) { return; }
	}
	UE_LOG(LogTemp, Warning, TEXT("Training bot could not find a clear ground spawn; using normal PlayerStarts"));
	Super::RestartPlayer(NewPlayer);
}

void ACustomGameMode::ServerStartRespawn_Implementation(AController* Controller)
{
	if (IsValid(Controller) && !GetWorld()->bIsTearingDown && !ExitedControllers.Contains(Controller))
	{
		ControllersToRespawn.AddUnique(Controller);

		FTimerDelegate TimerDelegate;
		TimerDelegate.BindUObject(this, &ACustomGameMode::ServerRespawn);
		GetWorld()->GetTimerManager().SetTimerForNextTick(TimerDelegate);
	}
}

void ACustomGameMode::ServerRespawn_Implementation()
{
	if (GetWorld()->bIsTearingDown) { return; }
	// Consume a snapshot: removing array elements while incrementing an index
	// skipped players and could dereference a missing start or exited controller.
	const TArray<AController*> Pending = MoveTemp(ControllersToRespawn);
	ControllersToRespawn.Reset();
	for (AController* Controller : Pending)
	{
		if (IsValid(Controller) && !ExitedControllers.Contains(Controller))
		{
			RestartPlayer(Controller);
		}
	}
}

void ACustomGameMode::Logout(AController* Exiting)
{
	ControllersToRespawn.Remove(Exiting);
	ExitedControllers.AddUnique(Exiting);
	Super::Logout(Exiting);
}
