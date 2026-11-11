// Opt-in integration probe. No automatic execution in normal games or Shipping.
#include "CoreMinimal.h"

#if !UE_BUILD_SHIPPING
#include "Actors/ProjectileActor.h"
#include "Actors/WeaponPickupActor.h"
#include "Blueprint/UserWidget.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Button.h"
#include "Components/CheckBox.h"
#include "MASK/ThunderhawkPawn.h"
#include "MASK/RhinoPawn.h"
#include "MASK/HurricanePawn.h"
#include "MASK/MaskVehicleDefinition.h"
#include "AI/VehicleBotController.h"
#include "Core/CustomGameMode.h"
#include "MASK/MaskVehicleModeComponent.h"
#include "Components/TextBlock.h"
#include "UI/MainMenuWidget.h"
#include "ChaosWheeledVehicleMovementComponent.h"
#include "Components/HealthComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Containers/Ticker.h"
#include "Core/OnlineGameInstance.h"
#include "Dom/JsonObject.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "EngineUtils.h"
#include "GameFramework/GameStateBase.h"
#include "GameFramework/PlayerController.h"
#include "HAL/FileManager.h"
#include "HAL/IConsoleManager.h"
#include "InputKeyEventArgs.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Pawns/PlayerWheeledVehiclePawn.h"
#include "Serialization/JsonSerializer.h"
#include "UnrealClient.h"
#include "UObject/UnrealType.h"

namespace VCMigration
{
class FSmoke
{
public:
	bool bHost;
	bool bMenuButtons = false;
	bool bMaskVehicle = false;
	bool bFleet = false;
	bool bHurricane = false;
	bool bDockFixture = false;
	TWeakObjectPtr<AHurricanePawn> FleetHurricane;
	TWeakObjectPtr<ARhinoPawn> FleetRhino;
	TWeakObjectPtr<APlayerWheeledVehiclePawn> FleetOriginal;
	FVector FleetRearStart = FVector::ZeroVector;
	float MaskFlightStartZ=0.f;
	int32 MenuStep = 0;
	FString Directory;
	TSharedRef<FJsonObject> Report = MakeShared<FJsonObject>();
	TSharedRef<FJsonObject> Checks = MakeShared<FJsonObject>();
	double Started = FPlatformTime::Seconds(), PhaseStarted = Started, NextSearch = 0;
	int32 Phase = 0, MaxProjectiles = 0, InitialAmmo = -1, SpawnedProjectiles = 0, RocketProjectiles = 0;
	bool bStartedSession = false, bRocketTested = false;
	TWeakObjectPtr<APlayerWheeledVehiclePawn> OriginalPawn, Victim;
	FVector LocalStart = FVector::ZeroVector, RemoteStart = FVector::ZeroVector;
	float LocalDistance = 0, RemoteDistance = 0, RemoteHealthBefore = 0, MinLocalHealth = BIG_NUMBER;
	float MaxLocalSpeed = 0, MaxRemoteSpeed = 0;
	int32 MaxGrounded = 0;
	int32 MinAmmo = MAX_int32;
	float MinVictimHealth = BIG_NUMBER;

	explicit FSmoke(bool Host) : bHost(Host)
	{
		FParse::Value(FCommandLine::Get(), TEXT("MigrationReportDir="), Directory);
		if (Directory.IsEmpty()) { Directory = FPaths::ProjectSavedDir() / TEXT("Migration/smoke"); }
		IFileManager::Get().MakeDirectory(*Directory, true);
		Report->SetStringField(TEXT("role"), Host ? TEXT("Host") : TEXT("Client"));
		Report->SetStringField(TEXT("method"), TEXT("Two real game processes; public session API, injected PlayerController key events, evaluated Chaos/replicated actors. Flag files synchronize test phases only, never gameplay state."));
		Report->SetObjectField(TEXT("checks"), Checks);
		Report->SetStringField(TEXT("started_utc"), FDateTime::UtcNow().ToIso8601());
		bMenuButtons = FParse::Param(FCommandLine::Get(), TEXT("MigrationMenuButtons"));
		bMaskVehicle=FParse::Param(FCommandLine::Get(),TEXT("MaskThunderhawk"));
		bFleet=FParse::Param(FCommandLine::Get(),TEXT("MaskFleet"));
		bHurricane=FParse::Param(FCommandLine::Get(),TEXT("MaskHurricane"));
		bDockFixture=FParse::Param(FCommandLine::Get(),TEXT("FleetDockFixture"));
		Report->SetStringField(TEXT("docking_validation"),bDockFixture?TEXT("After replicated player driving, the authority parks the stopped rear at the authored dock to isolate reattachment. Autonomous parking is NOT validated."):TEXT("Autonomous companion approach without a docking placement fixture."));
		Report->SetStringField(TEXT("session_entry"), bMenuButtons ? TEXT("Original Host/Create Session and Join/server-row UMG button delegates") : TEXT("GameInstance session API"));
		if (bMenuButtons) { Check(TEXT("menu_buttons_start_or_join_session"), false); }
	}
	FString Path(const TCHAR* Name) const { return Directory / Name; }
	bool Has(const TCHAR* Name) const { return IFileManager::Get().FileExists(*Path(Name)); }
	void Signal(const TCHAR* Name) const { FFileHelper::SaveStringToFile(TEXT("ready"), *Path(Name)); }
	void Check(const TCHAR* Name, bool Value) { Checks->SetBoolField(Name, Value); }
	void Stage(int32 Value) { Phase = Value; PhaseStarted = FPlatformTime::Seconds(); UE_LOG(LogTemp, Display, TEXT("VC_SMOKE %s phase=%d"), bHost ? TEXT("Host") : TEXT("Client"), Phase); }
	void Save(bool Complete)
	{
		Report->SetNumberField(TEXT("phase"), Phase);
		Report->SetBoolField(TEXT("complete"), Complete);
		Report->SetNumberField(TEXT("elapsed_seconds"), FPlatformTime::Seconds() - Started);
		bool Passed = Complete && Checks->Values.Num() > 0;
		for (const auto& Pair : Checks->Values) { Passed &= Pair.Value->AsBool(); }
		Report->SetBoolField(TEXT("passed"), Passed);
		Report->SetNumberField(TEXT("local_distance_cm"), LocalDistance);
		Report->SetNumberField(TEXT("remote_distance_cm"), RemoteDistance);
		Report->SetNumberField(TEXT("max_local_speed_cm_s"), MaxLocalSpeed);
		Report->SetNumberField(TEXT("max_remote_speed_cm_s"), MaxRemoteSpeed);
		Report->SetNumberField(TEXT("max_grounded_wheels"), MaxGrounded);
		Report->SetNumberField(TEXT("max_projectiles_seen"), MaxProjectiles);
		Report->SetNumberField(TEXT("projectiles_spawned"), SpawnedProjectiles);
		Report->SetNumberField(TEXT("rocket_projectiles_spawned"), RocketProjectiles);
		if(FleetRhino.IsValid() && FleetRhino->RearModule && FleetRhino->Definition && !FleetRhino->Definition->RearModuleTrack.IsEmpty())
		{
			const auto* Pod=FleetRhino->RearModule.Get();const FVector Dock=FleetRhino->GetActorTransform().TransformPosition(FleetRhino->Definition->RearModuleTrack.Last().TransformPosition(FleetRhino->Definition->RearModuleOrigin));
			Report->SetNumberField(TEXT("dock_distance_cm"),FVector::Dist(Dock,Pod->GetActorLocation()));Report->SetNumberField(TEXT("main_speed_cm_s"),FleetRhino->GetVelocity().Size());Report->SetNumberField(TEXT("rear_speed_cm_s"),Pod->GetVelocity().Size());
			Report->SetStringField(TEXT("main_position"),FleetRhino->GetActorLocation().ToString());Report->SetStringField(TEXT("rear_position"),Pod->GetActorLocation().ToString());
		}
		FString Json; const auto Writer = TJsonWriterFactory<>::Create(&Json); FJsonSerializer::Serialize(Report, Writer);
		FFileHelper::SaveStringToFile(Json, *Path(bHost ? TEXT("host.json") : TEXT("client.json")));
	}
	bool Finish(bool Timeout = false)
	{
		Check(TEXT("launcher_projectile_spawned"), RocketProjectiles > 0);
		Check(TEXT("completed_without_timeout"), !Timeout); Save(true);
		Signal(bHost ? TEXT("host.done") : TEXT("client.done"));
		UE_LOG(LogTemp, Display, TEXT("VC_SMOKE_FINISHED %s passed=%d"), bHost ? TEXT("Host") : TEXT("Client"), Report->GetBoolField(TEXT("passed")));
		FPlatformMisc::RequestExit(false); return false;
	}
	static AWeaponPickupActor* Weapon(APlayerWheeledVehiclePawn* Pawn)
	{
		const FObjectPropertyBase* Property = FindFProperty<FObjectPropertyBase>(Pawn->GetClass(), TEXT("CurrentWeapon"));
		return Property ? Cast<AWeaponPickupActor>(Property->GetObjectPropertyValue_InContainer(Pawn)) : nullptr;
	}
	static void Key(APlayerController* PC, const FKey& Value, bool Down)
	{
		PC->InputKey(FInputKeyEventArgs::CreateSimulated(Value,Down?IE_Pressed:IE_Released,Down?1.f:0.f,-1,FInputDeviceId::CreateFromInternalId(0)));
	}
	static UButton* MenuButton(UWorld* World, const TCHAR* Label, bool bServerRow = false)
	{
		UButton* Found = nullptr;
		for (TObjectIterator<UMainMenuWidget> It; It; ++It)
		{
			if (It->GetWorld() != World || !It->IsInViewport() || !It->WidgetTree) { continue; }
			It->WidgetTree->ForEachWidgetAndDescendants([&](UWidget* Widget)
			{
				if (Found) { return; }
				if (auto* Button = Cast<UButton>(Widget))
				{
					if (bServerRow)
					{
						const auto* OwnerWidget = Button->GetTypedOuter<UUserWidget>();
						if (OwnerWidget && OwnerWidget->GetClass()->GetName().Contains(TEXT("ServerSlot"))) { Found = Button; }
					}
					else if (auto* Text = Cast<UTextBlock>(Button->GetChildAt(0)); Text && Text->GetText().ToString() == Label) { Found = Button; }
				}
			});
		}
		return Found;
	}
	void Screenshot(const TCHAR* Name)
	{
		if (!FParse::Param(FCommandLine::Get(), TEXT("NullRHI"))) { FScreenshotRequest::RequestScreenshot(Path(Name), true, false); }
	}
	static bool PlaceImpactFixture(UWorld* World, APlayerWheeledVehiclePawn* Local, APlayerWheeledVehiclePawn* Remote)
	{
		// A fixed offset can put the car inside the test map's elevated ramp.
		// Find a nearly level, unobstructed footprint at the target's elevation.
		FCollisionQueryParams Query(SCENE_QUERY_STAT(MigrationFixture), false);
		for (TActorIterator<APawn> It(World); It; ++It) { Query.AddIgnoredActor(*It); }
		for (TActorIterator<AWeaponPickupActor> It(World); It; ++It) { Query.AddIgnoredActor(*It); }
		const FVector Target = Remote->GetActorLocation();
		const auto Bounds = Local->GetMesh()->Bounds;
		const float BottomOffset = FMath::Clamp(Local->GetActorLocation().Z - (Bounds.Origin.Z - Bounds.BoxExtent.Z), 40.f, 200.f);
		for (int32 Candidate = 0; Candidate < 32; ++Candidate)
		{
			const float Angle = (Candidate % 16) * 2.f * PI / 16.f;
			FVector Position = Target + FVector(FMath::Cos(Angle), FMath::Sin(Angle), 0) * (Candidate < 16 ? 1000.f : 1500.f);
			float Lowest = BIG_NUMBER, Highest = -BIG_NUMBER;
			bool Valid = true;
			for (const FVector Offset : { FVector::ZeroVector, FVector(250, 150, 0), FVector(250, -150, 0), FVector(-250, 150, 0), FVector(-250, -150, 0) })
			{
				FHitResult Hit;
				if (!World->LineTraceSingleByChannel(Hit, Position + Offset + FVector(0, 0, 500), Position + Offset - FVector(0, 0, 1000), ECC_Visibility, Query)
					|| Hit.ImpactNormal.Z < 0.98f || FMath::Abs(Hit.ImpactPoint.Z - Target.Z) > 250.f) { Valid = false; break; }
				Lowest = FMath::Min(Lowest, static_cast<float>(Hit.ImpactPoint.Z)); Highest = FMath::Max(Highest, static_cast<float>(Hit.ImpactPoint.Z));
			}
			if (!Valid || Highest - Lowest > 25.f) { continue; }
			Position.Z = Highest + BottomOffset + 15.f;
			const FRotator Rotation(0, (Target - Position).Rotation().Yaw, 0);
			if (const auto* MaskCar=Cast<AThunderhawkPawn>(Local))
			{
				const FVector CheckCenter=FTransform(Rotation,Position).TransformPosition(MaskCar->Modes->ClearanceCenter);
				if (World->OverlapBlockingTestByChannel(CheckCenter,Rotation.Quaternion(),ECC_Vehicle,FCollisionShape::MakeBox(MaskCar->Modes->ClearanceExtent),Query)) { continue; }
			}
			Local->SetActorLocationAndRotation(Position, Rotation, false, nullptr, ETeleportType::TeleportPhysics);
			Local->GetMesh()->SetPhysicsLinearVelocity(FVector::ZeroVector); Local->GetMesh()->SetPhysicsAngularVelocityInDegrees(FVector::ZeroVector);
			return true;
		}
		return false;
	}
	bool SpawnFleetFixture(UWorld* World,APlayerWheeledVehiclePawn* Host,bool Hurricane=false)
	{
		FCollisionQueryParams Query(SCENE_QUERY_STAT(FleetNetworkSpawn),false);
		for(TActorIterator<APawn> It(World);It;++It) { Query.AddIgnoredActor(*It); }
		for(TActorIterator<AWeaponPickupActor> It(World);It;++It) { Query.AddIgnoredActor(*It); }
		for(int32 I=0;I<32;++I)
		{
			const float Angle=I*2.f*PI/32;FVector P=Host->GetActorLocation()+FVector(FMath::Cos(Angle),FMath::Sin(Angle),0)*5000.f;
			FHitResult Hit;
			if(!World->LineTraceSingleByChannel(Hit,P+FVector(0,0,500),P-FVector(0,0,1000),ECC_Visibility,Query) || Hit.ImpactNormal.Z<.99f) { continue; }
			P.Z=Hit.ImpactPoint.Z+15.f;bool Clear=true;
			for(TActorIterator<APawn> It(World);It;++It) { if(FVector::Dist2D(P,It->GetActorLocation())<2800.f) { Clear=false; } }
			if(!Clear || World->OverlapBlockingTestByChannel(P+FVector(0,0,240),FQuat::Identity,ECC_Vehicle,FCollisionShape::MakeBox(FVector(1400,1400,170)),Query)) { continue; }
			auto* AI=World->SpawnActor<AVehicleBotController>();AI->TrainingIndex=Hurricane?1:0;
			CastChecked<ACustomGameMode>(World->GetAuthGameMode())->RestartPlayerAtTransform(AI,FTransform(FRotator::ZeroRotator,P));
			// Park this fixture until possession. Its brain resumes on the old pawn
			// after the swap; real escort driving is covered by FleetSmoke.
			AI->SetActorTickEnabled(false);
			if(Hurricane) { FleetHurricane=Cast<AHurricanePawn>(AI->GetPawn());return FleetHurricane.IsValid(); }
			FleetRhino=Cast<ARhinoPawn>(AI->GetPawn());return FleetRhino.IsValid();
		}
		return false;
	}
	bool Tick(float)
	{
		// The original menu Blueprint applies saved graphics settings after travel,
		// including an unlimited frame rate. Keep this test's two processes at 30 Hz.
		static IConsoleVariable* FPS = IConsoleManager::Get().FindConsoleVariable(TEXT("t.MaxFPS"));
		if (FPS)
		{
			if (FPS->GetFloat() != 30.f) { FPS->Set(30.f, ECVF_SetByConsole); }
		}
		const double Now = FPlatformTime::Seconds();
		if (Now - Started > (bFleet?240:150)) { return Finish(true); }
		UWorld* World = nullptr;
		for (const FWorldContext& Context : GEngine->GetWorldContexts())
		{
			if (Context.WorldType == EWorldType::Game) { World = Context.World(); break; }
		}
		if (!World) { return true; }
		UOnlineGameInstance* GI = Cast<UOnlineGameInstance>(World->GetGameInstance());
		if (!GI) { Check(TEXT("original_game_instance"), false); return Finish(); }
		if (Phase == 0)
		{
			if (bHost && !bStartedSession)
			{
				if (bMenuButtons)
				{
					for (TObjectIterator<UMainMenuWidget> It;It;++It)
					{
						if (It->GetWorld()!=World || !It->IsInViewport()) { continue; }
						if (auto* Choice=Cast<UCheckBox>(It->GetWidgetFromName(TEXT("ThunderhawkSelection"))))
						{
							Choice->SetIsChecked(bMaskVehicle);Choice->OnCheckStateChanged.Broadcast(bMaskVehicle);if(bMaskVehicle) { Check(TEXT("host_selected_thunderhawk_in_menu"),true); }
						}
					}
				}
				else { GI->bThunderhawkSelected=bMaskVehicle; }
			}
			if (bMenuButtons && !bStartedSession && Now - Started > 2)
			{
				if (bHost)
				{
					if (MenuStep == 0)
					{
						if (auto* HostButton = MenuButton(World, TEXT("Host"))) { HostButton->OnClicked.Broadcast(); MenuStep = 1; NextSearch = Now + 0.5; }
					}
					else if (Now > NextSearch)
					{
						if (auto* Create = MenuButton(World, TEXT("Create Session")))
						{
							Create->OnClicked.Broadcast(); bStartedSession = true; Check(TEXT("menu_buttons_start_or_join_session"), true);
						}
					}
				}
				else if (World->GetNetMode() != NM_Client)
				{
					if (MenuStep == 0)
					{
						if (auto* Join = MenuButton(World, TEXT("Join"))) { Join->OnClicked.Broadcast(); MenuStep = 1; NextSearch = Now + 8; }
					}
					else if (auto* Row = MenuButton(World, TEXT(""), true))
					{
						Row->OnClicked.Broadcast(); bStartedSession = true; Check(TEXT("menu_buttons_start_or_join_session"), true);
					}
					else if (Now > NextSearch)
					{
						if (auto* Refresh = MenuButton(World, TEXT("Refresh"))) { Refresh->OnClicked.Broadcast(); }
						NextSearch = Now + 8;
					}
				}
			}
			if (!bMenuButtons && bHost && !bStartedSession && Now - Started > 2)
			{
				FCreateServerInfo Info; Info.ServerName = TEXT("Migration-Smoke"); Info.MaxPlayers = 2; Info.bIsLAN = true;
				GI->CreateSession(Info); bStartedSession = true;
			}
			if (!bMenuButtons && !bHost && World->GetNetMode() != NM_Client && Now > NextSearch)
			{
				if (bStartedSession) { GI->TryJoinSession(NAME_GameSession, 0); }
				GI->FindSessions(); bStartedSession = true; NextSearch = Now + 7;
			}
			APlayerController* PC = World->GetFirstPlayerController();
			APlayerWheeledVehiclePawn* Pawn = PC ? Cast<APlayerWheeledVehiclePawn>(PC->GetPawn()) : nullptr;
			if (!Pawn || !World->GetGameState() || World->GetGameState()->PlayerArray.Num() != 2) { Save(false); return true; }
			if (bHost ? World->GetNetMode() != NM_ListenServer : World->GetNetMode() != NM_Client) { return true; }
			Check(TEXT("original_game_instance"), true); Check(TEXT("two_players_connected"), true); Check(TEXT("session_create_or_discovery_join"), true);
			Check(TEXT("original_vehicle_possessed"), Pawn->IsLocallyControlled());
			Report->SetStringField(TEXT("map"), World->GetOutermost()->GetName()); Report->SetStringField(TEXT("pawn_class"), Pawn->GetClass()->GetPathName());
			Stage(1); return true;
		}
		APlayerController* PC = World->GetFirstPlayerController();
		APlayerWheeledVehiclePawn* Local = PC ? Cast<APlayerWheeledVehiclePawn>(PC->GetPawn()) : nullptr;
		APlayerWheeledVehiclePawn* Remote = nullptr;
		for (TActorIterator<APlayerWheeledVehiclePawn> It(World); It; ++It) { if (*It != Local && It->GetPlayerState()) { Remote = *It; break; } }
		if (!Local) { return true; }
		if (Phase == 1 && Now - PhaseStarted > 4 && Remote)
		{
			World->AddOnActorSpawnedHandler(FOnActorSpawned::FDelegate::CreateLambda([this](AActor* Actor)
			{
				if (Actor->IsA<AProjectileActor>())
				{
					++SpawnedProjectiles;
					if (Actor->GetClass()->GetName().Contains(TEXT("Rocket")))
					{
						++RocketProjectiles;
						const FBoolProperty* Explosive = FindFProperty<FBoolProperty>(Actor->GetClass(), TEXT("bIsExplosive"));
						Check(TEXT("launcher_explosive_data_configured"), Explosive && Explosive->GetPropertyValue_InContainer(Actor));
					}
				}
			}));
			OriginalPawn = Local; LocalStart = Local->GetActorLocation(); RemoteStart = Remote->GetActorLocation();
			UChaosWheeledVehicleMovementComponent* Move = Cast<UChaosWheeledVehicleMovementComponent>(Local->GetVehicleMovementComponent());
			Check(TEXT("four_chaos_wheels"), Move && Move->GetNumWheels() == 4);
			Check(TEXT("vehicle_simulates_physics"), Local->GetMesh()->IsSimulatingPhysics());
			Check(TEXT("original_hud_exists"), PC->GetHUD() != nullptr);
			int32 WidgetCount = 0;
			for (TObjectIterator<UUserWidget> It; It; ++It) { if (It->GetWorld() == World && It->IsInViewport()) { ++WidgetCount; } }
			Check(TEXT("viewport_ui_exists"), WidgetCount > 0);
			PC->SetIgnoreMoveInput(false); PC->SetInputMode(FInputModeGameOnly());
			Key(PC, EKeys::Two, true); Key(PC, EKeys::Two, false);
			if (bHost) { Signal(TEXT("drive_host")); Key(PC, EKeys::W, true); }
			Stage(2); Screenshot(bHost ? TEXT("host-ready.png") : TEXT("client-ready.png"));
		}
		if (Phase >= 2 && Phase <= 5)
		{
			LocalDistance = FMath::Max(LocalDistance, static_cast<float>(FVector::Dist2D(Local->GetActorLocation(), LocalStart)));
			MaxLocalSpeed = FMath::Max(MaxLocalSpeed, static_cast<float>(Local->GetVelocity().Size()));
			if (Remote) { RemoteDistance = FMath::Max(RemoteDistance, static_cast<float>(FVector::Dist2D(Remote->GetActorLocation(), RemoteStart))); MaxRemoteSpeed = FMath::Max(MaxRemoteSpeed, static_cast<float>(Remote->GetVelocity().Size())); }
			if (const auto* Move = Cast<UChaosWheeledVehicleMovementComponent>(Local->GetVehicleMovementComponent()))
			{
				int32 Grounded = 0; for (int32 I = 0; I < Move->GetNumWheels(); ++I) { Grounded += Move->GetWheelState(I).bInContact ? 1 : 0; } MaxGrounded = FMath::Max(MaxGrounded, Grounded);
			}
			int32 Projectiles = 0; for (TActorIterator<AProjectileActor> It(World); It; ++It) { ++Projectiles; } MaxProjectiles = FMath::Max(MaxProjectiles, Projectiles);
			if (auto* Health = Local->FindComponentByClass<UHealthComponent>()) { MinLocalHealth = FMath::Min(MinLocalHealth, Health->CurrentHealth); }
		}
		const auto Age = [this]() { return FPlatformTime::Seconds() - PhaseStarted; };
		// A rendered viewport can flush pressed keys when focus/capture changes.
		// Sustain the held drive key throughout its phase, as OS key-repeat does.
		if ((bHost && Phase==2 && Age()<4) || (!bHost && Phase==3 && Age()<4)) { Key(PC,EKeys::W,true); }
		if (Phase == 4)
		{
			if (const auto* Current = Weapon(Local)) { MinAmmo = FMath::Min(MinAmmo, Current->CurrentAmmo + Current->CurrentMagazineAmmo); }
			if (bHost && Victim.IsValid()) { if (const auto* Health = Victim->FindComponentByClass<UHealthComponent>()) { MinVictimHealth = FMath::Min(MinVictimHealth, Health->CurrentHealth); } }
		}
		if (bHost)
		{
			if (Phase == 2 && Age() > 3 && Age() < 4) { Key(PC, EKeys::D, true); }
			if (Phase == 2 && Age() > 4)
			{
				Key(PC, EKeys::W, false); Key(PC, EKeys::D, false); Key(PC, EKeys::SpaceBar, true);
				Check(TEXT("local_input_drives_vehicle"), LocalDistance > 100 && MaxLocalSpeed > 50); Check(TEXT("wheel_ground_contact"), MaxGrounded >= 3);
				Report->SetNumberField(TEXT("host_distance_during_drive_cm"),LocalDistance);
				Report->SetNumberField(TEXT("host_speed_during_drive_cm_s"),MaxLocalSpeed);
				Signal(TEXT("drive_client")); Stage(3);
			}
			if (Phase == 3 && Has(TEXT("client_drive_done")) && Remote)
			{
				Check(TEXT("client_movement_received_on_server"), RemoteDistance > 100 && MaxRemoteSpeed > 50);
				Check(TEXT("client_fire_received_on_server"), SpawnedProjectiles > 0);
				AWeaponPickupActor* Current = Weapon(Local);
				USkeletalMeshComponent* Mesh = Current ? Current->FindComponentByClass<USkeletalMeshComponent>() : nullptr;
				if (!Current || !Mesh) { Check(TEXT("original_weapon_equipped"), false); return Finish(); }
				Check(TEXT("original_weapon_equipped"), true); InitialAmmo = Current->CurrentAmmo + Current->CurrentMagazineAmmo;
				MinAmmo = InitialAmmo;
				Report->SetStringField(TEXT("host_weapon_class"), Current->GetClass()->GetPathName());
				Report->SetNumberField(TEXT("host_initial_magazine"), Current->CurrentMagazineAmmo);
				// Arrange only the authoritative listen-host car. Teleporting an
				// autonomous client's car causes prediction corrections, not a stable
				// collision fixture. Both cars' driving was checked before this step.
				const bool Placed = PlaceImpactFixture(World, Local, Remote);
				Check(TEXT("impact_fixture_clear_ground"), Placed);
				if (!Placed) { return Finish(); }
				for (int32 Aim = 0; Aim < 3; ++Aim)
				{
					const FTransform Muzzle = Mesh->GetSocketTransform(TEXT("MuzzleSocket"));
					const FQuat SocketRelative = Current->GetActorQuat().Inverse() * Muzzle.GetRotation();
					const FQuat Desired = (Remote->GetMesh()->Bounds.Origin - Muzzle.GetLocation()).ToOrientationQuat();
					Current->SetActorRotation(Desired * SocketRelative.Inverse());
				}
				Report->SetStringField(TEXT("impact_fixture"), TEXT("Listen host moved near stationary client; controlled muzzle aim; original server fire RPC, projectile collision and damage path. Manual reticle aim is a separate visual check."));
				Victim = Remote;
				if (auto* Health = Remote->FindComponentByClass<UHealthComponent>()) { RemoteHealthBefore = Health->CurrentHealth; }
				Signal(TEXT("host_fire"));
				Local->ProcessEvent(Local->FindFunctionChecked(TEXT("ServerStartFireWeapon")), nullptr);
				Stage(4);
			}
			if (Phase == 4 && Age() > 1)
			{
				Key(PC, EKeys::LeftMouseButton, false);
				const auto* Movement = Cast<UChaosWheeledVehicleMovementComponent>(Local->GetVehicleMovementComponent());
				int32 Grounded = 0;
				if (Movement) { for (int32 I = 0; I < Movement->GetNumWheels(); ++I) { Grounded += Movement->GetWheelState(I).bInContact ? 1 : 0; } }
				Check(TEXT("impact_fixture_stays_grounded"), Grounded >= 3);
				Check(TEXT("impact_fixture_stays_upright"), Local->GetActorUpVector().Z > 0.85f);
				Check(TEXT("host_weapon_consumes_ammo"), MinAmmo < InitialAmmo);
				const UHealthComponent* Health = Victim.IsValid() ? Victim->FindComponentByClass<UHealthComponent>() : nullptr;
				Check(TEXT("weapon_projectile_causes_damage"), MinVictimHealth < RemoteHealthBefore);
				Report->SetNumberField(TEXT("target_min_health_during_fire"), MinVictimHealth);
				if (Health) { Report->SetNumberField(TEXT("target_health_before_fire"), RemoteHealthBefore); Report->SetNumberField(TEXT("target_health_after_fire"), Health->CurrentHealth); }
				Signal(TEXT("damage_done")); Stage(5); Screenshot(TEXT("host-after-fire.png"));
			}
			if (Phase == 5 && Age() > 0.3 && !bRocketTested)
			{
				struct FSwitchParameters { EWeaponToDo NewWeapon = EWeaponToDo::Primary; } Parameters;
				Local->ProcessEvent(Local->FindFunctionChecked(TEXT("ServerSwitchWeapon")), &Parameters);
				if (AWeaponPickupActor* Launcher = Weapon(Local))
				{
					if (USkeletalMeshComponent* Mesh = Launcher->FindComponentByClass<USkeletalMeshComponent>())
					{
						const FTransform Muzzle = Mesh->GetSocketTransform(TEXT("MuzzleSocket"));
						const FQuat Relative = Launcher->GetActorQuat().Inverse() * Muzzle.GetRotation();
						Launcher->SetActorRotation(FVector::UpVector.ToOrientationQuat() * Relative.Inverse());
						const int32 Before = Launcher->CurrentAmmo + Launcher->CurrentMagazineAmmo;
						Local->ProcessEvent(Local->FindFunctionChecked(TEXT("ServerStartFireWeapon")), nullptr);
						Check(TEXT("launcher_consumes_ammo"), Launcher->CurrentAmmo + Launcher->CurrentMagazineAmmo < Before);
					}
				}
				bRocketTested = true;
			}
			if (Phase == 5 && Age() > 3)
			{
				// Separate deterministic death-path test, explicitly damage injection.
				if (Victim.IsValid()) { UGameplayStatics::ApplyDamage(Victim.Get(), 100000, PC, Local, UDamageType::StaticClass()); }
				Signal(TEXT("death_injected")); Stage(6);
			}
			if (Phase == 6)
			{
				if (Remote && Remote != Victim.Get()) { Check(TEXT("server_destroyed_and_respawned_vehicle"), !Victim.IsValid()); }
				if (bMaskVehicle && Checks->HasField(TEXT("server_destroyed_and_respawned_vehicle")) && Has(TEXT("mask_client_ready")))
				{
					Check(TEXT("both_players_use_thunderhawk"),Cast<AThunderhawkPawn>(Local) && Cast<AThunderhawkPawn>(Remote));
					Signal(TEXT("mask_deploy_client"));Stage(20);
				}
				if (Checks->HasField(TEXT("server_destroyed_and_respawned_vehicle")) && Has(TEXT("client.done"))) { return Finish(); }
			}
		}
		else
		{
			if (Phase == 2 && Has(TEXT("drive_client"))) { Check(TEXT("host_movement_replicated_to_client"), RemoteDistance > 100 && MaxRemoteSpeed > 50); Key(PC, EKeys::W, true); Stage(3); }
			if (Phase == 3 && Age() > 3 && Age() < 4) { Key(PC, EKeys::D, true); }
			if (Phase == 3 && Age() > 4)
			{
				Key(PC, EKeys::W, false); Key(PC, EKeys::D, false); Key(PC, EKeys::SpaceBar, true);
				Check(TEXT("local_input_drives_vehicle"), LocalDistance > 100 && MaxLocalSpeed > 50); Check(TEXT("wheel_ground_contact"), MaxGrounded >= 3);
				if (auto* Current = Weapon(Local)) { InitialAmmo = Current->CurrentAmmo + Current->CurrentMagazineAmmo; Report->SetNumberField(TEXT("client_initial_magazine"), Current->CurrentMagazineAmmo); }
				MinAmmo = InitialAmmo;
				Key(PC, EKeys::LeftMouseButton, true); Stage(4);
			}
			if (Phase == 4 && Age() > 2)
			{
				Key(PC, EKeys::LeftMouseButton, false); const auto* Current = Weapon(Local);
				Check(TEXT("client_fire_ammo_authoritatively_replicated"), Current && MinAmmo < InitialAmmo); Signal(TEXT("client_drive_done")); Stage(5);
			}
			if (Phase == 5 && Has(TEXT("damage_done")))
			{
				const auto* Health = Local->FindComponentByClass<UHealthComponent>();
				Check(TEXT("damage_replicated_to_victim"), Health && MinLocalHealth < Health->MaxHealth);
				Check(TEXT("host_projectiles_seen_on_client"), SpawnedProjectiles > 0); Stage(6);
			}
			if (Phase == 6 && Local != OriginalPawn.Get())
			{
				Check(TEXT("destruction_and_respawn_replicated"), !OriginalPawn.IsValid());
				Stage(7);
			}
			if (Phase == 7 && Age() > 1)
			{
				const auto* Health = Local->FindComponentByClass<UHealthComponent>();
				if (Health && Health->MaxHealth > 0 && Health->CurrentHealth == Health->MaxHealth)
				{
					Check(TEXT("respawn_restores_health"),true);
					if (bMaskVehicle) { Signal(TEXT("mask_client_ready"));Stage(20); } else { return Finish(); }
				}
				if (Age() > 5) { Check(TEXT("respawn_restores_health"), false); return Finish(); }
			}
		}
		if (bMaskVehicle && Phase>=20)
		{
			auto* Mine=Cast<AThunderhawkPawn>(Local);auto* Other=Cast<AThunderhawkPawn>(Remote);
			if (!Mine || !Other) { Check(TEXT("network_mask_pawns_present"),false);return Finish(); }
			if (bHost)
			{
				if (Phase==20 && Other->Modes->GetMode()==EMaskVehicleMode::Flight)
				{
					Check(TEXT("client_mode_request_executed_on_server"),true);Check(TEXT("client_mask_hidden_replicated_to_server"),!Other->IsMaskVisible());
					MaskFlightStartZ=Other->GetActorLocation().Z;Signal(TEXT("mask_lift_client"));Stage(21);
				}
				if (Phase==21 && Age()>3.5)
				{
					Check(TEXT("client_mask_restored_on_server"),Other->IsMaskVisible());
					Check(TEXT("client_flight_input_changes_server_altitude"),Other->GetActorLocation().Z-MaskFlightStartZ>500.f);
					Signal(TEXT("mask_land_client"));Stage(22);
				}
				if (Phase==22 && Has(TEXT("mask_client_returned")))
				{
					Check(TEXT("client_road_return_received_on_server"),Other->Modes->GetMode()==EMaskVehicleMode::Road);
					Mine->Modes->ServerToggleMode();Stage(23);
				}
				if (Phase==23 && Mine->Modes->GetMode()==EMaskVehicleMode::Flight) { Signal(TEXT("mask_host_transformed"));Stage(24); }
				if(Phase==24 && bFleet)
				{
					FleetOriginal=Remote;Check(TEXT("network_fleet_spawned_on_clear_ground"),SpawnFleetFixture(World,Local));
					Signal(TEXT("fleet_ready"));Stage(30);
				}
				else if (Phase==24 && Has(TEXT("client.done"))) { return Finish(); }
			}
			else
			{
				if (Phase==20 && Has(TEXT("mask_deploy_client")))
				{
					Key(PC,EKeys::M,true);Key(PC,EKeys::M,false);Key(PC,EKeys::T,true);Key(PC,EKeys::T,false);Stage(21);
				}
				if (Phase==21 && Has(TEXT("mask_lift_client")))
				{
					Check(TEXT("server_authorized_mode_replicated_to_owner"),Mine->Modes->GetMode()==EMaskVehicleMode::Flight);
					Key(PC,EKeys::M,true);Key(PC,EKeys::M,false);
					MaskFlightStartZ=Mine->GetActorLocation().Z;Key(PC,EKeys::R,true);Key(PC,EKeys::W,true);Key(PC,EKeys::A,true);Stage(22);
				}
				if (Phase==22 && Age()>1.) { Key(PC,EKeys::A,false); }
				if (Phase==22 && Has(TEXT("mask_land_client")))
				{
					Key(PC,EKeys::R,false);Key(PC,EKeys::W,false);Key(PC,EKeys::A,false);Check(TEXT("flight_altitude_replicated_to_owner"),Mine->GetActorLocation().Z-MaskFlightStartZ>450.f);
					Key(PC,EKeys::T,true);Key(PC,EKeys::T,false);Stage(24);
				}
				if (Phase==24 && Mine->Modes->GetMode()==EMaskVehicleMode::Road)
				{
					Check(TEXT("road_mode_replicated_back_to_owner"),true);Signal(TEXT("mask_client_returned"));Stage(25);
				}
				if (Phase==25 && Has(TEXT("mask_host_transformed")))
				{
					Check(TEXT("host_mode_replicated_to_remote_client"),Other->Modes->GetMode()==EMaskVehicleMode::Flight);
					Check(TEXT("host_mask_replicated_to_remote_client"),Other->IsMaskVisible());Screenshot(TEXT("client-mask-network.png"));
					if(bFleet) { FleetOriginal=Local;Stage(30); } else { return Finish(); }
				}
			}
		}
		if(bFleet && Phase>=30)
		{
			if(!FleetRhino.IsValid()) { for(TActorIterator<ARhinoPawn> It(World);It;++It) { FleetRhino=*It;break; } }
			if(bHost)
			{
				APlayerController* ClientPC=nullptr;
				for(FConstPlayerControllerIterator It=World->GetPlayerControllerIterator();It;++It) { if(It->Get()!=PC) { ClientPC=It->Get();break; } }
				auto* Controlled=ClientPC?Cast<APlayerWheeledVehiclePawn>(ClientPC->GetPawn()):nullptr;
				if(Phase==30 && FleetRhino.IsValid() && Controlled==FleetRhino.Get())
				{
					Check(TEXT("client_possession_of_ai_rhino_on_server"),true);Check(TEXT("previous_client_vehicle_now_ai"),Cast<AVehicleBotController>(FleetOriginal->GetController())!=nullptr);
					Check(TEXT("other_human_vehicle_not_stolen"),PC->GetPawn()==OriginalPawn.Get());Signal(TEXT("fleet_main_seen"));Stage(31);
				}
				if(Phase==31 && FleetRhino.IsValid() && Controlled==FleetRhino->RearModule)
				{
					Check(TEXT("client_possession_of_six_wheel_module_on_server"),true);Check(TEXT("main_rhino_now_ai_ally"),Cast<AVehicleBotController>(FleetRhino->GetController()) && Controlled->IsAlliedWith(FleetRhino.Get()));
					FleetRearStart=Controlled->GetActorLocation();Signal(TEXT("fleet_rear_seen"));Stage(32);
				}
				if(Phase==32 && Has(TEXT("fleet_rear_drive_done")))
				{
					Check(TEXT("client_module_drive_reaches_server"),FVector::Dist2D(FleetRearStart,FleetRhino->RearModule->GetActorLocation())>100.f);Signal(TEXT("fleet_drive_seen"));Stage(33);
				}
				if(Phase==33 && bDockFixture && Has(TEXT("fleet_docking_ready")) && !Has(TEXT("fleet_docking_placed")) && FleetRhino.IsValid() && Controlled==FleetRhino.Get() && FleetRhino->GetVelocity().Size()<50.f)
				{
					auto* Pod=FleetRhino->RearModule.Get();const auto* Main=FleetRhino.Get();
					const FTransform End=Main->Definition->RearModuleTrack.Last();
					const FVector Dock=Main->GetActorTransform().TransformPosition(End.TransformPosition(Main->Definition->RearModuleOrigin));
					Pod->SetActorLocationAndRotation(Dock,Main->GetActorRotation(),false,nullptr,ETeleportType::TeleportPhysics);
					Pod->GetMesh()->SetPhysicsLinearVelocity(FVector::ZeroVector);Pod->GetMesh()->SetPhysicsAngularVelocityInDegrees(FVector::ZeroVector);
					Pod->ForceNetUpdate();Signal(TEXT("fleet_docking_placed"));Report->SetBoolField(TEXT("explicit_manual_parking_fixture_used"),true);
				}
				if(Phase==33 && !bHurricane && Has(TEXT("client.done"))) { Check(TEXT("host_kept_own_vehicle_during_swaps"),PC->GetPawn()==OriginalPawn.Get());return Finish(); }
				if(Phase==33 && bHurricane && Has(TEXT("fleet_rhino_done")))
				{
					Check(TEXT("hurricane_spawned_on_clear_ground"),SpawnFleetFixture(World,Local,true));Signal(TEXT("hurricane_ready"));Stage(34);
				}
				if(Phase==34 && FleetHurricane.IsValid() && Controlled==FleetHurricane.Get()) { Check(TEXT("client_hurricane_possession_on_server"),true);Signal(TEXT("hurricane_owned"));Stage(35); }
				if(Phase==35 && FleetHurricane.IsValid() && FleetHurricane->Modes->GetMode()==EMaskVehicleMode::Combat && FleetHurricane->SpareWheel && FleetHurricane->SpareWheel->bEjected)
				{
					Check(TEXT("hurricane_six_wheels_gunner_mask_on_server"),CastChecked<UChaosWheeledVehicleMovementComponent>(FleetHurricane->GetVehicleMovement())->Wheels.Num()==6 && FleetHurricane->Matt->GetRelativeLocation().Z>140.f && FleetHurricane->IsMaskVisible());
					Check(TEXT("hurricane_spare_ejection_on_server"),!FleetHurricane->SpareWheel->GetAttachParentActor());Signal(TEXT("hurricane_ejection_seen"));Stage(36);
				}
				if(Phase==36 && Has(TEXT("client.done"))) { Check(TEXT("host_kept_own_vehicle_during_swaps"),PC->GetPawn()==OriginalPawn.Get());return Finish(); }
			}
			else
			{
				auto* Main=FleetRhino.Get();auto* Pod=Main?Main->RearModule.Get():nullptr;
				if(Phase==30 && Has(TEXT("fleet_ready")) && Main && Pod)
				{
					Key(PC,EKeys::Gamepad_DPad_Up,true);Key(PC,EKeys::Gamepad_DPad_Up,false);Stage(31);
				}
				if(Phase==31 && Local==Main && Has(TEXT("fleet_main_seen")))
				{
					Check(TEXT("client_camera_and_alex_after_swap"),Local->IsLocallyControlled() && Main->Definition->DriverName==TEXT("Alex Sector") && Main->IsMaskVisible());Key(PC,EKeys::SpaceBar,true);Stage(311);
				}
				if(Phase==311 && Age()>1. && Main->GetVelocity().Size()<35.f) { Key(PC,EKeys::Gamepad_FaceButton_Left,true);Key(PC,EKeys::Gamepad_FaceButton_Left,false);Stage(32); }
				if(Phase==32 && Main->Modes->GetMode()==EMaskVehicleMode::Combat && Pod && Pod->bDetached)
				{
					Check(TEXT("rhino_ground_combat_and_detachment_replicated"),!Main->Definition->bSupportsFlight && !Pod->Definition->bSupportsFlight);
					Key(PC,EKeys::Gamepad_DPad_Up,true);Key(PC,EKeys::Gamepad_DPad_Up,false);Stage(33);
				}
				if(Phase==33 && Local==Pod && Has(TEXT("fleet_rear_seen")))
				{
					Check(TEXT("client_bruce_masked_in_same_rear_vehicle"),Pod->IsMaskVisible() && Pod->Definition->DriverName==TEXT("Bruce Sato"));
					Key(PC,EKeys::SpaceBar,false);Key(PC,EKeys::W,true);Stage(34);
				}
				if(Phase==34 && Age()<3.) { Key(PC,EKeys::W,true); }
				if(Phase==34 && Age()>3.)
				{
					Key(PC,EKeys::W,false);Key(PC,EKeys::SpaceBar,true);Signal(TEXT("fleet_rear_drive_done"));Stage(35);
				}
				if(Phase==35 && Has(TEXT("fleet_drive_seen"))) { Key(PC,EKeys::Gamepad_DPad_Down,true);Key(PC,EKeys::Gamepad_DPad_Down,false);Stage(36); }
				if(Phase==36 && Local==Main)
				{
					Key(PC,EKeys::SpaceBar,true);
					Signal(TEXT("fleet_docking_ready"));
					const FVector Dock=Main->GetActorTransform().TransformPosition(Main->Definition->RearModuleTrack.Last().TransformPosition(Main->Definition->RearModuleOrigin));
					if(Main->GetVelocity().Size()<50.f && FVector::Dist(Dock,Pod->GetActorLocation())<200.f && Pod->GetVelocity().Size()<80.f)
					{ Key(PC,EKeys::Gamepad_FaceButton_Left,true);Key(PC,EKeys::Gamepad_FaceButton_Left,false);Stage(37); }
				}
				if(Phase==37 && Main->Modes->GetMode()==EMaskVehicleMode::Road && !Pod->bDetached)
				{
					Check(TEXT("same_rear_vehicle_redocks_over_network"),Pod==Main->RearModule.Get());Screenshot(TEXT("fleet-client-redocked.png"));
					Key(PC,EKeys::Gamepad_DPad_Down,true);Key(PC,EKeys::Gamepad_DPad_Down,false);Stage(38);
				}
				if(Phase==38 && Local==FleetOriginal.Get())
				{
					Check(TEXT("client_returns_to_original_thunderhawk_without_respawn"),true);
					if(!bHurricane) { return Finish(); }Signal(TEXT("fleet_rhino_done"));Stage(39);
				}
				if(Phase==39 && Has(TEXT("hurricane_ready")))
				{
					if(!FleetHurricane.IsValid()) { for(TActorIterator<AHurricanePawn> It(World);It;++It) { FleetHurricane=*It;break; } }
					if(Local==FleetHurricane.Get()) { Key(PC,EKeys::Gamepad_LeftShoulder,true);Stage(40); }
					else if(Age()>.8) { Key(PC,EKeys::Gamepad_DPad_Up,true);Key(PC,EKeys::Gamepad_DPad_Up,false);PhaseStarted=FPlatformTime::Seconds(); }
				}
				if(Phase==40 && Has(TEXT("hurricane_owned")) && Age()>1. && Local->GetVelocity().Size()<100.f)
				{ Key(PC,EKeys::Gamepad_FaceButton_Left,true);Key(PC,EKeys::Gamepad_FaceButton_Left,false);Stage(41); }
				if(Phase==41 && FleetHurricane->Modes->GetMode()==EMaskVehicleMode::Combat)
				{
					Check(TEXT("hurricane_gunner_and_six_wheels_replicated_to_client"),FleetHurricane->Matt->GetRelativeLocation().Z>140.f && FleetHurricane->IsMaskVisible() && CastChecked<UChaosWheeledVehicleMovementComponent>(Local->GetVehicleMovement())->Wheels.Num()==6);
					Key(PC,EKeys::Gamepad_FaceButton_Top,true);Key(PC,EKeys::Gamepad_FaceButton_Top,false);Stage(42);
				}
				if(Phase==42 && Age()>1.5 && Has(TEXT("hurricane_ejection_seen")))
				{
					Check(TEXT("same_spare_actor_detaches_on_client"),FleetHurricane->SpareWheel && FleetHurricane->SpareWheel->bEjected && !FleetHurricane->SpareWheel->GetAttachParentActor());Screenshot(TEXT("hurricane-client-combat.png"));return Finish();
				}
			}
		}
		Save(false); return true;
	}
};

TUniquePtr<FSmoke> Runner;
FAutoConsoleCommand Command(TEXT("VC.MigrationSmoke"), TEXT("Opt-in Host/Client integration probe. Use a unique -MigrationReportDir for each run."),
	FConsoleCommandWithArgsDelegate::CreateLambda([](const TArray<FString>& Args)
	{
		if (Runner || Args.Num() != 1 || (Args[0] != TEXT("Host") && Args[0] != TEXT("Client"))) { return; }
		Runner = MakeUnique<FSmoke>(Args[0] == TEXT("Host"));
		FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda([](float Delta) { return Runner->Tick(Delta); }));
	}));
}
#endif
