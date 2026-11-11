#include "CoreMinimal.h"
#include "Tests/DynamicsSmoke.h"

#if !UE_BUILD_SHIPPING
#include "MASK/ThunderhawkPawn.h"
#include "MASK/MaskVehicleDefinition.h"
#include "MASK/MaskVehicleModeComponent.h"
#include "ChaosWheeledVehicleMovementComponent.h"
#include "Components/BoxComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Containers/Ticker.h"
#include "Dom/JsonObject.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Engine/SkeletalMesh.h"
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
#include "Actors/WeaponPickupActor.h"
#include "Actors/ProjectileActor.h"
#include "Camera/CameraComponent.h"
#include "Components/Button.h"
#include "UI/PlayerHUD.h"
#include "UI/MainMenuWidget.h"
#include "Framework/Application/SlateApplication.h"
#include "Kismet/GameplayStatics.h"
#include "UObject/UnrealType.h"

namespace MaskVehicleTest
{
TMap<FKey,float> AnalogState;
class FRun
{
public:
	FString Directory;
	int32 Phase=0;
	int32 PhaseFrames=0;
	int32 DriveFrames=0;
	float DriveDistance=0.f;
	double Started=FPlatformTime::Seconds(),PhaseStarted=Started;
	TSharedRef<FJsonObject> Checks=MakeShared<FJsonObject>();
	FVector StartPosition;
	float RoadZ=0.f;
	TWeakObjectPtr<USkeletalMeshComponent> OriginalMatt;
	TWeakObjectPtr<AActor> Blocker;
	bool bXbox=FParse::Param(FCommandLine::Get(),TEXT("MaskXbox"));
	FRotator StartView,StartCarRotation;
	int32 XboxProjectiles=0,AmmoBefore=0;
	TWeakObjectPtr<AWeaponPickupActor> XboxWeapon;
	FRun()
	{
		FParse::Value(FCommandLine::Get(),TEXT("MigrationReportDir="),Directory);
		if (Directory.IsEmpty()) { Directory=FPaths::ProjectSavedDir()/TEXT("Art/thunderhawk-smoke"); }
		IFileManager::Get().MakeDirectory(*Directory,true);
	}
	void Check(const TCHAR* Name,bool Value) { Checks->SetBoolField(Name,Value); }
	void Stage(int32 Next) { Phase=Next;PhaseFrames=0;PhaseStarted=FPlatformTime::Seconds();UE_LOG(LogTemp,Display,TEXT("MASK_TEST phase=%d"),Phase); }
	void Save(bool Complete)
	{
		bool Passed=Complete && Checks->Values.Num()>=15;
		for (const auto& Pair:Checks->Values) { Passed &= Pair.Value->AsBool(); }
		auto Result=MakeShared<FJsonObject>();Result->SetBoolField(TEXT("passed"),Passed);Result->SetBoolField(TEXT("complete"),Complete);
		Result->SetObjectField(TEXT("checks"),Checks);Result->SetNumberField(TEXT("phase"),Phase);
		Result->SetNumberField(TEXT("elapsed_seconds"),FPlatformTime::Seconds()-Started);
		Result->SetStringField(TEXT("input_method"),bXbox?TEXT("Injected UE gamepad keys/analog axes and Slate menu event; no physical controller claimed"):TEXT("Injected keyboard events"));
		Result->SetNumberField(TEXT("drive_frames"),DriveFrames);Result->SetNumberField(TEXT("drive_distance_cm"),DriveDistance);
		FString Json;FJsonSerializer::Serialize(Result,TJsonWriterFactory<>::Create(&Json));
		FFileHelper::SaveStringToFile(Json,*(Directory/TEXT("thunderhawk.json")));
	}
	bool Finish(bool Timeout=false) { Check(TEXT("no_timeout"),!Timeout);Save(true);FPlatformMisc::RequestExit(false);return false; }
	static void Key(APlayerController* PC,FKey Key,bool Down)
	{
		if (FParse::Param(FCommandLine::Get(),TEXT("MaskXbox")))
		{
			if (Key==EKeys::W) { Axis(PC,EKeys::Gamepad_RightTriggerAxis,Down?1.f:0.f);return; }
			if (Key==EKeys::S) { Axis(PC,EKeys::Gamepad_LeftTriggerAxis,Down?1.f:0.f);return; }
			if (Key==EKeys::SpaceBar) { Key=EKeys::Gamepad_LeftShoulder; }
			else if (Key==EKeys::T) { Key=EKeys::Gamepad_FaceButton_Left; }
			else if (Key==EKeys::R) { Axis(PC,EKeys::Gamepad_LeftY,Down?1.f:0.f);return; }
			else if (Key==EKeys::F) { Key=EKeys::Gamepad_FaceButton_Right; }
		}
		PC->InputKey(FInputKeyEventArgs::CreateSimulated(Key,Down?IE_Pressed:IE_Released,Down?1.f:0.f,-1,FInputDeviceId::CreateFromInternalId(0)));
	}
	static void Axis(APlayerController* PC,FKey Key,float Value)
	{
		// One absolute sample per axis per frame, like XInput polling. Sending a
		// nonzero value and neutral in the same frame accumulates both samples.
		AnalogState.Add(Key,Value);
	}
	static AWeaponPickupActor* Weapon(APawn* Pawn)
	{
		const auto* Property=FindFProperty<FObjectPropertyBase>(Pawn->GetClass(),TEXT("CurrentWeapon"));
		return Property?Cast<AWeaponPickupActor>(Property->GetObjectPropertyValue_InContainer(Pawn)):nullptr;
	}
	void Screenshot(const TCHAR* Name) { if (!FParse::Param(FCommandLine::Get(),TEXT("NullRHI"))) { FScreenshotRequest::RequestScreenshot(Directory/Name,true,false); } }
	static FRotator ActiveView(AThunderhawkPawn* Car)
	{
		TArray<UCameraComponent*> Cameras;Car->GetComponents(Cameras);
		for (const auto* Camera:Cameras) { if(Camera->IsActive()) { return Camera->GetComponentRotation(); } }
		return FRotator::ZeroRotator;
	}
	bool Tick(float)
	{
		if (FPlatformTime::Seconds()-Started>120.) { return Finish(true); }
		UWorld* World=nullptr;
		for (const auto& Context:GEngine->GetWorldContexts()) { if (Context.WorldType==EWorldType::Game) { World=Context.World();break; } }
		if (!World) { return true; }
		auto* PC=World->GetFirstPlayerController();auto* Car=PC?Cast<AThunderhawkPawn>(PC->GetPawn()):nullptr;
		if (bXbox && Phase==16 && PC)
		{
			for (TObjectIterator<UMainMenuWidget> It;It;++It)
			{
				if (It->GetWorld()!=World || !It->IsInViewport()) { continue; }
				if (auto* Solo=Cast<UButton>(It->GetWidgetFromName(TEXT("PlaySoloButton")));Solo && Solo->HasUserFocus(PC))
				{
					Check(TEXT("menu_focus_ready_without_mouse"),true);
					const FKeyEvent Event(EKeys::Gamepad_Special_Right,FModifierKeysState(),0,false,0,0);
					FSlateApplication::Get().ProcessKeyDownEvent(Event);Stage(17);return true;
				}
			}
		}
		if (!Car || !Car->Definition) { return true; }
		if (bXbox && Phase==17 && World->GetTimeSeconds()>4.f)
		{
			Check(TEXT("xbox_menu_starts_masked_thunderhawk"),Car->IsLocallyControlled() && Car->IsMaskVisible());return Finish();
		}
		auto* Move=CastChecked<UChaosWheeledVehicleMovementComponent>(Car->GetVehicleMovement());
		const double Age=FPlatformTime::Seconds()-PhaseStarted;
		++PhaseFrames;
		if (Phase==1 && (Age<2. || PhaseFrames<60)) { Key(PC,EKeys::W,true); }
		if (bXbox && Phase==1)
		{
			Axis(PC,EKeys::Gamepad_RightX,.7f);Axis(PC,EKeys::Gamepad_RightY,.35f);
			Axis(PC,EKeys::Gamepad_LeftX,-1.f);
		}
		if(Phase==0 && World->GetTimeSeconds()<5.f && World->GetTimeSeconds()>1.f && Car->GetActorLocation().Z<19000.f)
		{
			World->SpawnActor<ADynamicsTestFloor>(FVector(0,0,19950),FRotator::ZeroRotator);
			Car->SetActorLocationAndRotation(FVector(0,0,20015),FRotator::ZeroRotator,false,nullptr,ETeleportType::TeleportPhysics);
			Car->GetMesh()->SetPhysicsLinearVelocity(FVector::ZeroVector);Car->GetMesh()->SetPhysicsAngularVelocityInRadians(FVector::ZeroVector);
		}
		if (Phase==0 && World->GetTimeSeconds()>5.f)
		{
			Check(TEXT("dedicated_thunderhawk_pawn"),true);Check(TEXT("four_persistent_chaos_wheels"),Move->Wheels.Num()==4);
			Check(TEXT("new_chassis_physics_asset"),Car->GetMesh()->GetPhysicsAsset()==Car->Definition->Chassis->GetPhysicsAsset());
			Check(TEXT("chassis_simulates_physics"),Car->GetMesh()->IsSimulatingPhysics());
			const FVector FrontLeft=Car->GetMesh()->GetBoneLocation(TEXT("wheel_FL"),EBoneSpaces::ComponentSpace);
			Check(TEXT("wheel_bone_matches_source_coordinates"),FrontLeft.Equals(FVector(140,-81.8,32.8),1.f));
			int32 Contacts=0;for (int32 I=0;I<Move->Wheels.Num();++I) { Contacts+=Move->GetWheelState(I).bInContact?1:0; }
			Check(TEXT("four_ground_contacts"),Contacts==4);
			OriginalMatt=Car->Matt;Check(TEXT("same_matt_skin"),Car->Matt->GetSkeletalMeshAsset()==Car->Definition->Driver);
			Check(TEXT("mask_equipped_by_default"),Car->IsMaskVisible());
			Screenshot(TEXT("road.png"));StartPosition=Car->GetActorLocation();RoadZ=StartPosition.Z;
			StartView=ActiveView(Car);StartCarRotation=Car->GetActorRotation();
			Key(PC,EKeys::W,true);Stage(1);
		}
		else if (Phase==1 && Age>2. && PhaseFrames>=60)
		{
			DriveFrames=PhaseFrames;DriveDistance=FVector::Dist2D(StartPosition,Car->GetActorLocation());
			Key(PC,EKeys::W,false);Key(PC,EKeys::SpaceBar,true);Key(PC,EKeys::S,true);
			if (bXbox)
			{
				// Measure actual orbit relative to the vehicle: simultaneous steering
				// can cancel world yaw, and initial control yaw need not match the view.
				const float Orbit=FMath::FindDeltaAngleDegrees(StartView.Yaw-StartCarRotation.Yaw,ActiveView(Car).Yaw-Car->GetActorRotation().Yaw);
				Check(TEXT("right_stick_rotates_camera"),FMath::Abs(Orbit)>30.f);
				UE_LOG(LogTemp,Display,TEXT("MASK_TEST camera_orbit_degrees=%.2f"),Orbit);
				Check(TEXT("left_stick_steers_vehicle"),FMath::Abs(FMath::FindDeltaAngleDegrees(StartCarRotation.Yaw,Car->GetActorRotation().Yaw))>1.f);
				Axis(PC,EKeys::Gamepad_RightX,0);Axis(PC,EKeys::Gamepad_RightY,0);Axis(PC,EKeys::Gamepad_LeftX,0);
				Key(PC,EKeys::Gamepad_LeftThumbstick,true);Key(PC,EKeys::Gamepad_LeftThumbstick,false);
			}
			Check(TEXT("ground_input_moves_vehicle"),FVector::Dist2D(StartPosition,Car->GetActorLocation())>150.f);Stage(2);
		}
		else if (Phase==2 && Age>3.)
		{
			Key(PC,EKeys::S,false);if(!bXbox) { Key(PC,EKeys::M,true);Key(PC,EKeys::M,false); }Stage(3);
		}
		else if (Phase==3 && Age>1.)
		{
			if (bXbox)
			{
				TArray<UCameraComponent*> Cameras;Car->GetComponents(Cameras);bool Centered=false;
				for (const auto* Camera:Cameras) { if(Camera->IsActive()) { Centered=FMath::Abs(FMath::FindDeltaAngleDegrees(Camera->GetComponentRotation().Yaw,Car->GetActorRotation().Yaw))<2.f; }}
				Check(TEXT("l3_recenters_camera"),Centered);
			}
			Check(TEXT("same_character_mask_state"),(bXbox?Car->IsMaskVisible():!Car->IsMaskVisible()) && OriginalMatt.Get()==Car->Matt);
			if(!bXbox) { Key(PC,EKeys::M,true);Key(PC,EKeys::M,false); }
			Key(PC,EKeys::P,true);Key(PC,EKeys::P,false);Stage(4);
		}
		else if (Phase==4 && Age>1.)
		{
			Check(TEXT("standing_pose_uses_same_mesh"),OriginalMatt.Get()==Car->Matt && Car->Matt->GetRelativeLocation().Y<-100.f);
			Screenshot(TEXT("standing-mask.png"));Stage(41);
		}
		else if (Phase==41 && Age>.3)
		{
			Key(PC,EKeys::P,true);Key(PC,EKeys::P,false);
			// Real blocking geometry verifies the server clearance refusal, then is removed.
			auto* Actor=World->SpawnActor<AActor>();auto* Box=NewObject<UBoxComponent>(Actor);Actor->SetRootComponent(Box);
			Box->SetBoxExtent(FVector(80));Box->SetCollisionProfileName(TEXT("BlockAll"));Box->RegisterComponent();
			Actor->SetActorLocation(Car->GetActorTransform().TransformPosition(FVector(0,0,180)));Blocker=Actor;
			Key(PC,EKeys::T,true);Key(PC,EKeys::T,false);Stage(5);
		}
		else if (Phase==5 && Age>.5)
		{
			Check(TEXT("blocked_transformation_refused"),Car->Modes->GetMode()==EMaskVehicleMode::Road && !Car->Modes->LastRefusal.IsEmpty());
			if (Blocker.IsValid()) { Blocker->Destroy(); }Stage(51);
		}
		else if (Phase==51 && Age>.5)
		{
			Key(PC,EKeys::T,true);Key(PC,EKeys::T,false);Stage(6);
		}
		else if (Phase==6 && Age>5.)
		{
			Check(TEXT("flight_mode_reached"),Car->Modes->GetMode()==EMaskVehicleMode::Flight);
			Check(TEXT("ground_force_providers_disabled"),!Move->bMechanicalSimEnabled && !Move->bSuspensionEnabled && !Move->bWheelFrictionEnabled);
			RoadZ=Car->GetActorLocation().Z;Screenshot(TEXT("transformed.png"));Key(PC,EKeys::R,true);Stage(7);
		}
		else if (Phase==7 && Age>3.)
		{
			Key(PC,EKeys::R,false);Check(TEXT("flight_lift_input_changes_altitude"),Car->GetActorLocation().Z-RoadZ>500.f);
			Key(PC,EKeys::T,true);Key(PC,EKeys::T,false);
			Screenshot(TEXT("flight.png"));Stage(8);
		}
		else if (Phase==8)
		{
			if(Car->Modes->GetMode()==EMaskVehicleMode::Landing) { Check(TEXT("airborne_request_starts_automatic_landing"),true); }
			if(Car->Modes->GetMode()==EMaskVehicleMode::Road) { Stage(9); }
		}
		else if (Phase==9 && Age>5.)
		{
			Check(TEXT("road_mode_restored"),Car->Modes->GetMode()==EMaskVehicleMode::Road);
			Check(TEXT("chaos_ground_forces_restored"),Move->bMechanicalSimEnabled && Move->bSuspensionEnabled && Move->bWheelFrictionEnabled);
			Check(TEXT("same_four_wheels_after_roundtrip"),Move->Wheels.Num()==4);
			if (!bXbox) { return Finish(); }
			Key(PC,EKeys::Gamepad_DPad_Right,true);Key(PC,EKeys::Gamepad_DPad_Right,false);
			World->AddOnActorSpawnedHandler(FOnActorSpawned::FDelegate::CreateLambda([this](AActor* Actor){if(Actor->IsA<AProjectileActor>()) { ++XboxProjectiles; }}));Stage(10);
		}
		else if (Phase==10 && Age>.5)
		{
			XboxWeapon=Weapon(Car);AmmoBefore=XboxWeapon.IsValid()?XboxWeapon->CurrentMagazineAmmo:0;
			Key(PC,EKeys::Gamepad_RightShoulder,true);Stage(11);
		}
		else if (Phase==11 && Age>.4)
		{
			Key(PC,EKeys::Gamepad_RightShoulder,false);
			Check(TEXT("rb_fires_original_weapon"),XboxProjectiles>0 && XboxWeapon.IsValid() && XboxWeapon->CurrentMagazineAmmo<AmmoBefore);
			Key(PC,EKeys::Gamepad_FaceButton_Top,true);Key(PC,EKeys::Gamepad_FaceButton_Top,false);
			Key(PC,EKeys::Gamepad_RightThumbstick,true);Key(PC,EKeys::Gamepad_RightThumbstick,false);
			Key(PC,EKeys::Gamepad_Special_Left,true);Stage(12);
		}
		else if (Phase==12 && Age>.6)
		{
			Check(TEXT("y_cycles_weapon"),Weapon(Car) && Weapon(Car)!=XboxWeapon.Get());
			const auto* HUD=Cast<APlayerHUD>(PC->GetHUD());
			Check(TEXT("view_shows_scores"),HUD && HUD->bShowPlayerScores);
			TArray<UCameraComponent*> Cameras;Car->GetComponents(Cameras);int32 Active=0;bool Inside=false;
			for (const auto* Camera:Cameras) { if(Camera->IsActive()) { ++Active;Inside|=Camera->GetName()==TEXT("Internal Camera"); }}
			Check(TEXT("r3_selects_single_cockpit_camera"),Active==1 && Inside);Screenshot(TEXT("xbox-controls.png"));
			Key(PC,EKeys::Gamepad_Special_Left,false);Stage(121);
		}
		else if (Phase==121 && Age>.2)
		{
			Screenshot(TEXT("cockpit.png"));Stage(122);
		}
		else if (Phase==122 && Age>.3)
		{
			Key(PC,EKeys::Gamepad_Special_Right,true);Key(PC,EKeys::Gamepad_Special_Right,false);Stage(13);
		}
		else if (Phase==13 && Age>.5)
		{
			Check(TEXT("menu_pauses_solo"),Car->IsPauseMenuOpen() && UGameplayStatics::IsGamePaused(World));Screenshot(TEXT("xbox-pause.png"));
			Key(PC,EKeys::Gamepad_FaceButton_Right,true);Key(PC,EKeys::Gamepad_FaceButton_Right,false);Stage(14);
		}
		else if (Phase==14 && Age>.5)
		{
			Check(TEXT("b_resumes_game"),!Car->IsPauseMenuOpen() && !UGameplayStatics::IsGamePaused(World));
			Check(TEXT("mask_remains_equipped_with_xbox"),Car->IsMaskVisible());
			Key(PC,EKeys::Gamepad_Special_Right,true);Key(PC,EKeys::Gamepad_Special_Right,false);Stage(15);
		}
		else if (Phase==15 && Age>.3)
		{
			Key(PC,EKeys::Gamepad_FaceButton_Top,true);Key(PC,EKeys::Gamepad_FaceButton_Top,false);Stage(16);
		}
		for (const auto& Sample:AnalogState) { PC->InputKey(FInputKeyEventArgs::CreateSimulated(Sample.Key,IE_Axis,Sample.Value,1,FInputDeviceId::CreateFromInternalId(0))); }
		Save(false);return true;
	}
};
TUniquePtr<FRun> Runner;
FAutoConsoleCommand Command(TEXT("MASK.ThunderhawkSmoke"),TEXT("Opt-in actual ground, pilot, clearance, transform and flight test."),FConsoleCommandDelegate::CreateLambda([]()
{
	if (Runner) { return; }Runner=MakeUnique<FRun>();
	FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda([](float Delta) { return Runner->Tick(Delta); }));
}));
}
#endif
