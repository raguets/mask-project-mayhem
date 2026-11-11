#include "CoreMinimal.h"
#if !UE_BUILD_SHIPPING
#include "MASK/RhinoPawn.h"
#include "MASK/MaskVehicleDefinition.h"
#include "MASK/MaskVehicleModeComponent.h"
#include "AI/VehicleBotController.h"
#include "Core/CustomGameMode.h"
#include "Core/CustomPlayerState.h"
#include "Actors/WeaponPickupActor.h"
#include "Actors/ProjectileActor.h"
#include "Components/HealthComponent.h"
#include "Components/BoxComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "ChaosWheeledVehicleMovementComponent.h"
#include "Containers/Ticker.h"
#include "Dom/JsonObject.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "HAL/FileManager.h"
#include "HAL/IConsoleManager.h"
#include "InputKeyEventArgs.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonSerializer.h"
#include "UnrealClient.h"
#include "Kismet/GameplayStatics.h"

namespace FleetSmoke
{
class FRun
{
	FString Directory;
	int32 Phase=0,Frames=0,DriveFrames=0;
	double Started=FPlatformTime::Seconds(),PhaseStarted=Started,TransformStarted=0;
	TSharedRef<FJsonObject> Checks=MakeShared<FJsonObject>();
	TMap<FKey,float> Analog;
	TWeakObjectPtr<AThunderhawkPawn> Original;
	TWeakObjectPtr<ARhinoPawn> Rhino;
	TWeakObjectPtr<ARhinoRearModule> Module;
	TWeakObjectPtr<AVehicleBotController> Bot;
	TWeakObjectPtr<AWeaponPickupActor> OriginalPrimary,RhinoPrimary;
	float OriginalAmmo=0,OriginalHealth=0;
	FVector DriveStart,FormerStart,ModuleStart;
	int32 ModuleProjectiles=0;
	TSharedRef<FJsonObject> Telemetry=MakeShared<FJsonObject>();
	void Snapshot(AThunderhawkPawn* Car,const TCHAR* Name)
	{
		auto* Move=CastChecked<UChaosWheeledVehicleMovementComponent>(Car->GetVehicleMovement());auto Data=MakeShared<FJsonObject>();
		Data->SetStringField(TEXT("position"),*Car->GetActorLocation().ToString());Data->SetStringField(TEXT("rotation"),*Car->GetActorRotation().ToString());
		Data->SetStringField(TEXT("velocity"),*Car->GetVelocity().ToString());Data->SetStringField(TEXT("com_actor_space"),*Car->GetActorTransform().InverseTransformPosition(Car->GetMesh()->GetCenterOfMass()).ToString());
		Data->SetNumberField(TEXT("throttle"),Move->GetThrottleInput());Data->SetNumberField(TEXT("brake"),Move->GetBrakeInput());Data->SetBoolField(TEXT("handbrake"),Move->GetHandbrakeInput());
		Data->SetNumberField(TEXT("engine_rpm"),Move->GetEngineRotationSpeed());Data->SetNumberField(TEXT("gear"),Move->GetCurrentGear());Data->SetBoolField(TEXT("mechanical"),Move->bMechanicalSimEnabled);
		Data->SetNumberField(TEXT("health"),Car->FindComponentByClass<UHealthComponent>()->CurrentHealth);
		int32 Contacts=0;for(int32 I=0;I<Move->Wheels.Num();++I) { Contacts+=Move->GetWheelState(I).bInContact?1:0; }Data->SetNumberField(TEXT("contacts"),Contacts);
		Telemetry->SetObjectField(Name,Data);
	}
	void Check(const TCHAR* Key,bool Value) { Checks->SetBoolField(Key,Value); }
	void Stage(int32 Value) { Phase=Value;Frames=0;PhaseStarted=FPlatformTime::Seconds();UE_LOG(LogTemp,Display,TEXT("MASK_FLEET_TEST phase=%d"),Phase); }
	void Key(APlayerController* PC,FKey Value,bool Down)
	{
		PC->InputKey(FInputKeyEventArgs::CreateSimulated(Value,Down?IE_Pressed:IE_Released,Down?1.f:0.f,-1,FInputDeviceId::CreateFromInternalId(0)));
	}
	void Button(APlayerController* PC,FKey Value) { Key(PC,Value,true);Key(PC,Value,false); }
	void Shot(const TCHAR* Name) { if(!FParse::Param(FCommandLine::Get(),TEXT("NullRHI"))) { FScreenshotRequest::RequestScreenshot(Directory/Name,true,false); } }
	static int32 Weapons(AActor* Owner)
	{
		int32 Count=0;for(TActorIterator<AWeaponPickupActor> It(Owner->GetWorld());It;++It) { Count+=It->GetOwner()==Owner?1:0; }return Count;
	}
	bool ClearOtherVehicle(UWorld* World,AThunderhawkPawn* Main)
	{
		FCollisionQueryParams Query(SCENE_QUERY_STAT(FleetOtherFixture),false);
		for(TActorIterator<APawn> It(World);It;++It) { Query.AddIgnoredActor(*It); }
		for(TActorIterator<AWeaponPickupActor> It(World);It;++It) { Query.AddIgnoredActor(*It); }
		for(int32 I=0;I<16;++I)
		{
			const float Angle=I*2.f*PI/16;FVector P=Main->GetActorLocation()+FVector(FMath::Cos(Angle),FMath::Sin(Angle),0)*3200.f;
			FHitResult Hit;
			if(!World->LineTraceSingleByChannel(Hit,P+FVector(0,0,500),P-FVector(0,0,1000),ECC_Visibility,Query) || Hit.ImpactNormal.Z<.99f) { continue; }
			P.Z=Hit.ImpactPoint.Z+15.f;Original->SetActorLocation(P,false,nullptr,ETeleportType::TeleportPhysics);
			Original->GetMesh()->SetPhysicsLinearVelocity(FVector::ZeroVector);Original->GetMesh()->SetPhysicsAngularVelocityInDegrees(FVector::ZeroVector);FormerStart=P;return true;
		}
		return false;
	}
	bool Save(bool Complete)
	{
		bool Passed=Complete;for(const auto& Pair:Checks->Values) { Passed&=Pair.Value->AsBool(); }
		auto Report=MakeShared<FJsonObject>();Report->SetBoolField(TEXT("passed"),Passed);Report->SetBoolField(TEXT("complete"),Complete);Report->SetObjectField(TEXT("checks"),Checks);
		Report->SetNumberField(TEXT("phase"),Phase);Report->SetNumberField(TEXT("elapsed_seconds"),FPlatformTime::Seconds()-Started);Report->SetNumberField(TEXT("drive_frames"),DriveFrames);
		Report->SetStringField(TEXT("input_method"),TEXT("Real game, injected UE Xbox keys/axes; same pawn instances. Explicit damage fixture; no physical controller claimed."));
		Report->SetStringField(TEXT("docking_fixture"),TEXT("After independently measuring driving and AI escort, the stopped rear vehicle is placed at the authored dock to isolate reattachment."));
		Report->SetNumberField(TEXT("module_projectiles"),ModuleProjectiles);
		Report->SetObjectField(TEXT("telemetry"),Telemetry);
		FString Json;FJsonSerializer::Serialize(Report,TJsonWriterFactory<>::Create(&Json));FFileHelper::SaveStringToFile(Json,*(Directory/TEXT("fleet.json")));return Passed;
	}
	bool Finish(bool Timeout=false) { Check(TEXT("no_timeout"),!Timeout);Save(true);FPlatformMisc::RequestExit(false);return false; }
public:
	FRun()
	{
		FParse::Value(FCommandLine::Get(),TEXT("MigrationReportDir="),Directory);if(Directory.IsEmpty()) { Directory=FPaths::ProjectSavedDir()/TEXT("Art/fleet-smoke"); }
		IFileManager::Get().MakeDirectory(*Directory,true);
	}
	bool Tick(float)
	{
		if(FPlatformTime::Seconds()-Started>150.) { return Finish(true); }
		UWorld* World=nullptr;for(const auto& Context:GEngine->GetWorldContexts()) { if(Context.WorldType==EWorldType::Game) { World=Context.World();break; } }
		if(!World) { return true; }
		auto* PC=World->GetFirstPlayerController();auto* Car=PC?Cast<AThunderhawkPawn>(PC->GetPawn()):nullptr;
		if(!Car || !Car->Definition) { return true; }
		const double Age=FPlatformTime::Seconds()-PhaseStarted;++Frames;
		if(Phase==0 && World->GetTimeSeconds()>5.f)
		{
			Original=Car;Check(TEXT("thunderhawk_starts_masked"),Car->IsMaskVisible());Check(TEXT("physics_proxy_excluded_from_depth"),!Car->GetMesh()->bRenderInDepthPass);
			Check(TEXT("thunderhawk_transform_twice_as_fast"),FMath::IsNearlyEqual(Car->Modes->Duration,2.f));
			Button(PC,EKeys::Gamepad_LeftShoulder);Key(PC,EKeys::Gamepad_LeftShoulder,true);
			Analog.Add(EKeys::Gamepad_RightX,.5f);Analog.Add(EKeys::Gamepad_RightY,-.2f);Stage(1);
		}
		else if(Phase==1 && Frames>45)
		{
			Analog.Add(EKeys::Gamepad_RightX,0);Analog.Add(EKeys::Gamepad_RightY,0);Car->GetMesh()->SetRenderInDepthPass(true);Stage(2);
		}
		else if(Phase==2 && Age>.5) { Shot(TEXT("proxy-depth-before.png"));Stage(3); }
		else if(Phase==3 && Age>.4) { Car->GetMesh()->SetRenderInDepthPass(false);Stage(4); }
		else if(Phase==4 && Age>.5) { Shot(TEXT("proxy-depth-after.png"));Stage(5); }
		else if(Phase==5 && Age>.5)
		{
			auto* GM=Cast<ACustomGameMode>(World->GetAuthGameMode());auto* AI=World->SpawnActor<AVehicleBotController>();Bot=AI;AI->TrainingIndex=0;GM->RestartPlayer(AI);Rhino=Cast<ARhinoPawn>(AI->GetPawn());Stage(6);
		}
		else if(Phase==6 && Age>2.)
		{
			Check(TEXT("rhino_spawned_for_ai"),Rhino.IsValid() && Rhino->GetController()==Bot.Get());
			if(!Rhino.IsValid()) { return Finish(); }
			Module=Rhino->RearModule;Check(TEXT("persistent_rear_module_spawned"),Module.IsValid());
			Check(TEXT("two_distinct_masked_crew"),Module.IsValid() && Rhino->IsMaskVisible() && Module->IsMaskVisible() && Rhino->Matt->GetSkeletalMeshAsset()!=Module->Matt->GetSkeletalMeshAsset() && !Rhino->Passenger->GetSkeletalMeshAsset());
			Check(TEXT("ten_persistent_tires"),Rhino->Definition->Wheels.Num()==4 && Module.IsValid() && Module->Definition->Wheels.Num()==6);
			Check(TEXT("mounted_module_not_selectable"),Module.IsValid() && !Module->IsAvailableToSwitch());
			World->AddOnActorSpawnedHandler(FOnActorSpawned::FDelegate::CreateLambda([this](AActor* Actor){if(Actor->IsA<AProjectileActor>() && Actor->GetOwner()==Module.Get()) { ++ModuleProjectiles; }}));
			Check(TEXT("loadout_two_weapons_each"),Weapons(Original.Get())==2 && Weapons(Rhino.Get())==2);
			OriginalPrimary=Cast<ACustomPlayerState>(PC->PlayerState)->PrimaryWeapon;OriginalAmmo=OriginalPrimary->CurrentAmmo+OriginalPrimary->CurrentMagazineAmmo;
			RhinoPrimary=Cast<ACustomPlayerState>(Bot->PlayerState)->PrimaryWeapon;
			UGameplayStatics::ApplyDamage(Original.Get(),73.f,nullptr,nullptr,nullptr);OriginalHealth=Original->FindComponentByClass<UHealthComponent>()->CurrentHealth;FormerStart=Original->GetActorLocation();
			Button(PC,EKeys::Gamepad_DPad_Up);Stage(7);
		}
		else if(Phase==7 && Age>.7)
		{
			Check(TEXT("initial_damage_preserved_on_ai_handoff"),Original->FindComponentByClass<UHealthComponent>()->CurrentHealth<=OriginalHealth);
			Check(TEXT("dpad_up_possesses_same_rhino"),Car==Rhino.Get());Check(TEXT("ai_takes_same_thunderhawk"),Original->GetController()==Bot.Get() && Bot->GetPawn()==Original.Get());
			Check(TEXT("driver_changed_to_alex"),Car->Definition->DriverName==TEXT("Alex Sector"));
			Check(TEXT("rhino_inventory_transferred_not_respawned"),Cast<ACustomPlayerState>(PC->PlayerState)->PrimaryWeapon==RhinoPrimary.Get() && Weapons(Car)==2 && Weapons(Original.Get())==2);
			Check(TEXT("rhino_transform_twice_as_fast"),FMath::IsNearlyEqual(Car->Modes->Duration,2.5f));
			DriveStart=Car->GetActorLocation();Analog.Add(EKeys::Gamepad_RightTriggerAxis,1.f);Key(PC,EKeys::Gamepad_LeftShoulder,false);Stage(8);
		}
		else if(Phase==8 && Frames>=60)
		{
			DriveFrames=Frames;Check(TEXT("rhino_drives_with_xbox_rt"),FVector::Dist2D(DriveStart,Car->GetActorLocation())>150.f);
			Analog.Add(EKeys::Gamepad_RightTriggerAxis,0);Analog.Add(EKeys::Gamepad_LeftTriggerAxis,1.f);Key(PC,EKeys::Gamepad_LeftShoulder,true);Stage(9);
		}
		else if(Phase==9 && Age>2. && Car->GetVelocity().Size()<35.f)
		{
			const auto* Move=CastChecked<UChaosWheeledVehicleMovementComponent>(Car->GetVehicleMovement());int32 Contacts=0;for(int32 I=0;I<4;++I) { Contacts+=Move->GetWheelState(I).bInContact?1:0; }
			Check(TEXT("rhino_four_truck_contacts"),Contacts==4);Check(TEXT("other_vehicle_placed_outside_transformation_sweep"),ClearOtherVehicle(World,Car));
			Analog.Add(EKeys::Gamepad_LeftTriggerAxis,0);Button(PC,EKeys::Gamepad_LeftThumbstick);Shot(TEXT("rhino-road.png"));Stage(10);
		}
		else if(Phase==10 && Age>.5) { Button(PC,EKeys::Gamepad_FaceButton_Left);TransformStarted=FPlatformTime::Seconds();Stage(11); }
		else if(Phase==11 && Car->Modes->GetMode()==EMaskVehicleMode::Combat && Module.IsValid() && Module->bDetached)
		{
			Check(TEXT("rhino_combat_mode_reached_without_flight"),!Car->Definition->bSupportsFlight && FPlatformTime::Seconds()-TransformStarted<3.2);
			Check(TEXT("rear_module_is_same_actor_detached"),Rhino->RearModule==Module.Get() && Module->bDetached && !Module->GetAttachParentActor());
			Check(TEXT("rear_module_simulates_independently"),Module->GetMesh()->IsSimulatingPhysics());Shot(TEXT("rhino-combat.png"));Stage(12);
		}
		else if(Phase==12 && Age>2.)
		{
			ModuleStart=Module->GetActorLocation();DriveStart=Car->GetActorLocation();Analog.Add(EKeys::Gamepad_RightTriggerAxis,1.f);Key(PC,EKeys::Gamepad_LeftShoulder,false);Stage(110);
		}
		else if(Phase==110 && Frames>=60)
		{
			Check(TEXT("rhino_still_drives_in_ground_combat"),FVector::Dist2D(DriveStart,Car->GetActorLocation())>150.f);
			Analog.Add(EKeys::Gamepad_RightTriggerAxis,0);Analog.Add(EKeys::Gamepad_LeftTriggerAxis,1.f);Key(PC,EKeys::Gamepad_LeftShoulder,true);Stage(111);
		}
		else if(Phase==111 && Age>3. && Car->GetVelocity().Size()<35.f)
		{
			Snapshot(Car,TEXT("main_before_module_takeover"));Snapshot(Module.Get(),TEXT("module_after_ai_escort"));
			Check(TEXT("allied_module_ai_follows_moving_rhino"),FVector::Dist2D(ModuleStart,Module->GetActorLocation())>30.f && Cast<AVehicleBotController>(Module->GetController()));
			Analog.Add(EKeys::Gamepad_LeftTriggerAxis,0);Button(PC,EKeys::Gamepad_DPad_Up);Stage(120);
		}
		else if(Phase==120 && Age>.7)
		{
			Check(TEXT("switch_to_same_rear_vehicle"),Car==Module.Get());Check(TEXT("bruce_controls_module_with_lifter"),Car->Definition->DriverName==TEXT("Bruce Sato") && Car->IsMaskVisible());
			Check(TEXT("truck_and_module_are_allies"),Car->IsAlliedWith(Rhino.Get()));
			const float Health=Car->FindComponentByClass<UHealthComponent>()->CurrentHealth;
			UGameplayStatics::ApplyDamage(Car,50.f,Rhino->GetController(),Rhino.Get(),nullptr);
			Check(TEXT("friendly_damage_filtered"),Car->FindComponentByClass<UHealthComponent>()->CurrentHealth==Health);
			DriveStart=Car->GetActorLocation();Analog.Add(EKeys::Gamepad_RightTriggerAxis,1.f);Key(PC,EKeys::Gamepad_LeftShoulder,false);Stage(121);
		}
		else if(Phase==121 && Frames>=60)
		{
			Snapshot(Car,TEXT("module_at_end_of_player_drive"));
			Check(TEXT("rear_vehicle_drives_independently"),FVector::Dist2D(DriveStart,Car->GetActorLocation())>100.f);
			Analog.Add(EKeys::Gamepad_RightTriggerAxis,0);Analog.Add(EKeys::Gamepad_LeftTriggerAxis,1.f);Key(PC,EKeys::Gamepad_LeftShoulder,true);Stage(122);
		}
		else if(Phase==122 && Age>2. && Car->GetVelocity().Size()<35.f)
		{
			Check(TEXT("rear_vehicle_has_six_chaos_wheels"),CastChecked<UChaosWheeledVehicleMovementComponent>(Car->GetVehicleMovement())->GetNumWheels()==6);Shot(TEXT("rear-driving.png"));Button(PC,EKeys::Gamepad_DPad_Down);Stage(123);
		}
		else if(Phase==123 && Age>.7)
		{
			Check(TEXT("switch_back_to_same_main_rhino"),Car==Rhino.Get());Check(TEXT("rear_ai_resumes_companion_role"),Cast<AVehicleBotController>(Module->GetController()) && Cast<AVehicleBotController>(Module->GetController())->bCompanion);
			Analog.Add(EKeys::Gamepad_LeftTriggerAxis,1.f);Key(PC,EKeys::Gamepad_LeftShoulder,true);Stage(124);
		}
		else if(Phase==124 && Age>2. && Car->GetVelocity().Size()<35.f)
		{
			Snapshot(Car,TEXT("main_before_docking_fixture"));
			// Isolate the docking mechanism after actual independent drive/follow checks.
			FTransform Dock=Rhino->Definition->RearModuleTrack.Last();Dock.SetTranslation(Dock.TransformPosition(Rhino->Definition->RearModuleOrigin));Dock=Dock*Rhino->GetActorTransform();
			Module->SetActorTransform(Dock,false,nullptr,ETeleportType::TeleportPhysics);Module->GetMesh()->SetPhysicsLinearVelocity(FVector::ZeroVector);Module->GetMesh()->SetPhysicsAngularVelocityInDegrees(FVector::ZeroVector);
			Analog.Add(EKeys::Gamepad_LeftTriggerAxis,0);Stage(125);
		}
		else if(Phase==125 && Age>.6) { Button(PC,EKeys::Gamepad_FaceButton_Left);Stage(13); }
		else if(Phase==13 && Car->Modes->GetMode()==EMaskVehicleMode::Road)
		{
			Check(TEXT("same_module_reattaches_on_return"),Rhino->RearModule==Module.Get() && !Module->bDetached && Module->GetAttachParentActor()==Rhino.Get());
			Button(PC,EKeys::Gamepad_Special_Right);Stage(14);
		}
		else if(Phase==14 && Age>.5)
		{
			Check(TEXT("controls_live_in_pause_menu"),Car->IsPauseMenuOpen() && UGameplayStatics::IsGamePaused(World));Shot(TEXT("pause-controls.png"));Button(PC,EKeys::Gamepad_FaceButton_Right);Stage(15);
		}
		else if(Phase==15 && Age>.5)
		{
			// AI may legitimately collect health pickups while driving. Compare the
			// health immediately across this handoff, not across the whole combat run.
			OriginalHealth=Original->FindComponentByClass<UHealthComponent>()->CurrentHealth;
			Snapshot(Original.Get(),TEXT("thunderhawk_before_return_handoff"));Button(PC,EKeys::Gamepad_DPad_Down);Stage(16);
		}
		else if(Phase==16 && Age>.7)
		{
			Check(TEXT("dpad_down_returns_same_thunderhawk"),Car==Original.Get());Check(TEXT("ai_resumes_same_rhino"),Bot->GetPawn()==Rhino.Get());
			Check(TEXT("former_vehicle_ai_was_active"),FVector::Dist2D(FormerStart,Original->GetActorLocation())>30.f);
			Check(TEXT("damage_preserved_no_free_repair"),Car->FindComponentByClass<UHealthComponent>()->CurrentHealth<=OriginalHealth);
			Snapshot(Car,TEXT("thunderhawk_after_return_handoff"));Check(TEXT("companion_fires_on_opponents"),ModuleProjectiles>0);
			Check(TEXT("weapons_and_ammo_preserved"),Cast<ACustomPlayerState>(PC->PlayerState)->PrimaryWeapon==OriginalPrimary.Get() && OriginalPrimary->CurrentAmmo+OriginalPrimary->CurrentMagazineAmmo<=OriginalAmmo && Weapons(Car)==2 && Weapons(Rhino.Get())==2);
			Check(TEXT("same_matt_still_masked"),Car->IsMaskVisible());return Finish();
		}
		for(const auto& Axis:Analog) { PC->InputKey(FInputKeyEventArgs::CreateSimulated(Axis.Key,IE_Axis,Axis.Value,1,FInputDeviceId::CreateFromInternalId(0))); }
		Save(false);return true;
	}
};
TUniquePtr<FRun> Runner;
FAutoConsoleCommand Command(TEXT("MASK.FleetSmoke"),TEXT("Opt-in Rhino, Xbox possession swap and proxy depth A/B validation."),FConsoleCommandDelegate::CreateLambda([]()
{
	if(Runner) { return; }Runner=MakeUnique<FRun>();FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda([](float Delta){return Runner->Tick(Delta);}));
}));
}
#endif
