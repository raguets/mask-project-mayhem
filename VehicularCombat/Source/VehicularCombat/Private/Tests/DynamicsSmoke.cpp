#include "Tests/DynamicsSmoke.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "UObject/ConstructorHelpers.h"

ADynamicsTestFloor::ADynamicsTestFloor()
{
	bReplicates=true;bAlwaysRelevant=true;
	auto* Floor=CreateDefaultSubobject<UBoxComponent>(TEXT("PhysicsFloor"));SetRootComponent(Floor);
	Floor->SetBoxExtent(FVector(1000000,1000000,50));Floor->SetCollisionProfileName(TEXT("BlockAll"));
	auto* Visual=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("FloorVisual"));Visual->SetupAttachment(Floor);
	static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));Visual->SetStaticMesh(Cube.Object);
	Visual->SetRelativeScale3D(FVector(20000,20000,1));Visual->SetCollisionEnabled(ECollisionEnabled::NoCollision);
}

#if !UE_BUILD_SHIPPING
#include "MASK/ThunderhawkPawn.h"
#include "MASK/RhinoPawn.h"
#include "MASK/HurricanePawn.h"
#include "MASK/MaskDynamicsComponent.h"
#include "MASK/MaskVehicleDefinition.h"
#include "MASK/MaskVehicleModeComponent.h"
#include "AI/VehicleBotController.h"
#include "Core/CustomGameMode.h"
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

namespace DynamicsSmoke
{
constexpr float FloorZ=20000.f;
class FRun
{
	FString Directory,Role;bool Host=false,Network=false,Initialized=false,HighAltitudeFixture=false;
	int32 Phase=0,Frames=0;double Started=FPlatformTime::Seconds(),StageTime=Started;
	float PriorSpeed=0,PriorYaw=0,PriorHeight=0,Brake10=0,Energy10=0,MaxBank=0,MaxPitch=0;
	FVector Start;TMap<FKey,float> Axes;
	TSharedRef<FJsonObject> Checks=MakeShared<FJsonObject>(),Telemetry=MakeShared<FJsonObject>();
	TWeakObjectPtr<AThunderhawkPawn> Original;
	TWeakObjectPtr<ARhinoPawn> Rhino;TWeakObjectPtr<ARhinoRearModule> Module;
	TWeakObjectPtr<AHurricanePawn> Hurricane;
	void Check(const TCHAR* Name,bool Value) { Checks->SetBoolField(Name,Value); }
	void Stage(int32 Value) { Phase=Value;Frames=0;StageTime=FPlatformTime::Seconds();UE_LOG(LogTemp,Display,TEXT("MASK_DYNAMICS_TEST %s phase=%d"),*Role,Phase); }
	FString Path(const TCHAR* Name) const { return Directory/Name; }
	bool Has(const TCHAR* Name) const { return IFileManager::Get().FileExists(*Path(Name)); }
	void Signal(const TCHAR* Name) const { FFileHelper::SaveStringToFile(TEXT("ready"),*Path(Name)); }
	void Key(APlayerController* PC,FKey Value,bool Down) { PC->InputKey(FInputKeyEventArgs::CreateSimulated(Value,Down?IE_Pressed:IE_Released,Down?1.f:0.f,-1,FInputDeviceId::CreateFromInternalId(0))); }
	void Button(APlayerController* PC,FKey Value) { Key(PC,Value,true);Key(PC,Value,false); }
	void Shot(const TCHAR* Name) { if(!FParse::Param(FCommandLine::Get(),TEXT("NullRHI"))) { FScreenshotRequest::RequestScreenshot(Path(Name),true,false); } }
	void Snapshot(AThunderhawkPawn* Car,const TCHAR* Name)
	{
		auto R=MakeShared<FJsonObject>();R->SetStringField(TEXT("position"),Car->GetActorLocation().ToString());R->SetStringField(TEXT("rotation"),Car->GetActorRotation().ToString());
		R->SetStringField(TEXT("velocity"),Car->GetVelocity().ToString());R->SetNumberField(TEXT("energy_kj"),Car->Dynamics->KineticEnergyKJ());
		R->SetNumberField(TEXT("airspeed_command_mps"),Car->Dynamics->GetTargetAirspeedMPS());R->SetNumberField(TEXT("ground_clearance_cm"),Car->Dynamics->GroundClearanceCM);
		R->SetNumberField(TEXT("mode"),static_cast<int32>(Car->Modes->GetMode()));Telemetry->SetObjectField(Name,R);
		if(Network && !Host && (FCString::Strcmp(Name,TEXT("minimum_speed"))==0 || FCString::Strcmp(Name,TEXT("maximum_speed"))==0 || FCString::Strcmp(Name,TEXT("minimum_after_full_speed"))==0))
		{ Signal(*(FString(TEXT("sample."))+Name)); }
	}
	void Save(bool Complete)
	{
		bool Passed=Complete;for(const auto& Pair:Checks->Values) { Passed&=Pair.Value->AsBool(); }
		auto R=MakeShared<FJsonObject>();R->SetStringField(TEXT("role"),Role);R->SetBoolField(TEXT("passed"),Passed);R->SetBoolField(TEXT("complete"),Complete);
		R->SetNumberField(TEXT("phase"),Phase);R->SetNumberField(TEXT("elapsed_seconds"),FPlatformTime::Seconds()-Started);R->SetObjectField(TEXT("checks"),Checks);R->SetObjectField(TEXT("telemetry"),Telemetry);
		R->SetStringField(TEXT("fixture"),TEXT("Opt-in replicated flat platform at 200m, existing playable pawns, injected Xbox inputs. Brake comparisons use explicit initial velocities. No manual docking fixture. Rotorcraft uses a transient Thunderhawk definition as a physics proxy; no helicopter art claimed."));
		FString Json;FJsonSerializer::Serialize(R,TJsonWriterFactory<>::Create(&Json));FFileHelper::SaveStringToFile(Json,*(Directory/(Role+TEXT(".json"))));
	}
	bool Finish(bool Timeout=false) { Check(TEXT("no_timeout"),!Timeout);Save(true);Signal(Host?TEXT("host.done"):TEXT("client.done"));FPlatformMisc::RequestExit(false);return false; }
	void Place(AThunderhawkPawn* Car,FVector Location)
	{
		Car->SetActorLocationAndRotation(Location,FRotator::ZeroRotator,false,nullptr,ETeleportType::TeleportPhysics);
		Car->GetMesh()->SetPhysicsLinearVelocity(FVector::ZeroVector);Car->GetMesh()->SetPhysicsAngularVelocityInRadians(FVector::ZeroVector);
	}
public:
	explicit FRun(FString InRole):Role(InRole),Host(InRole==TEXT("host")),Network(InRole!=TEXT("solo"))
	{
		FParse::Value(FCommandLine::Get(),TEXT("MigrationReportDir="),Directory);if(Directory.IsEmpty()) { Directory=FPaths::ProjectSavedDir()/TEXT("Migration/dynamics-smoke"); }
		IFileManager::Get().MakeDirectory(*Directory,true);
	}
	bool Tick(float)
	{
		if(FPlatformTime::Seconds()-Started>240.) { return Finish(true); }
		UWorld* World=nullptr;for(const auto& C:GEngine->GetWorldContexts()) { if(C.WorldType==EWorldType::Game) { World=C.World();break; } }
		if(!World) { return true; }auto* PC=World->GetFirstPlayerController();auto* Car=PC?Cast<AThunderhawkPawn>(PC->GetPawn()):nullptr;
		if(!Car || !Car->Definition) { return true; }
		if(!Initialized)
		{
			if(World->GetTimeSeconds()<3.f) { return true; }
			Original=Car;Initialized=true;
			if(!Network || Host)
			{
				World->SpawnActor<ADynamicsTestFloor>(FVector(0,0,FloorZ-50),FRotator::ZeroRotator);
				Place(Car,FVector(0,Host?15000:0,FloorZ+15));
				if(Host) { Signal(TEXT("host.ready")); }else { Stage(1); }
			}
		}
		if(Host)
		{
			AThunderhawkPawn* Remote=nullptr;
			for(FConstPlayerControllerIterator It=World->GetPlayerControllerIterator();It;++It) { if(It->Get()!=PC) { Remote=Cast<AThunderhawkPawn>(It->Get()->GetPawn());break; } }
			if(Phase==0 && Remote)
			{
				Place(Remote,FVector(0,0,FloorZ+15));Signal(TEXT("drive.ready"));Stage(1);
			}
			if(Remote)
			{
				if(Has(TEXT("spawn.rhino")) && !Has(TEXT("rhino.spawned")))
				{
					auto* AI=World->SpawnActor<AVehicleBotController>();AI->TrainingIndex=0;
					CastChecked<ACustomGameMode>(World->GetAuthGameMode())->RestartPlayerAtTransform(AI,FTransform(FRotator::ZeroRotator,Remote->GetActorLocation()+FVector(0,1500,0)));AI->SetActorTickEnabled(false);Signal(TEXT("rhino.spawned"));
				}
				if(Remote->Modes->GetMode()==EMaskVehicleMode::Deploying && Remote->GetVelocity().Size()>300.f) { Check(TEXT("moving_transform_received_on_server"),true); }
				if(Remote->Modes->GetMode()==EMaskVehicleMode::Flight)
				{
					Check(TEXT("automatic_takeoff_on_server"),Remote->GetActorLocation().Z>FloorZ+100.f);
					if(FMath::Abs(Remote->GetActorRotation().Roll)>10.f) { Check(TEXT("physical_bank_on_server"),true); }
				}
				if(Remote->Modes->GetMode()==EMaskVehicleMode::Landing) { Check(TEXT("automatic_landing_requested_on_server"),true); }
				if(Remote->IsA<ARhinoRearModule>()) { Check(TEXT("player_controls_ejected_module_on_server"),true); }
				if(auto* Main=Cast<ARhinoPawn>(Remote);Main && Main->RearModule && Main->RearModule->GetAttachParentActor()==Main && Main->Modes->GetMode()==EMaskVehicleMode::Retracting)
				{ Check(TEXT("player_returns_to_truck_and_same_module_attaches_on_server"),true); }
				Snapshot(Remote,TEXT("latest_remote"));
				for(const TCHAR* Point:{TEXT("minimum_speed"),TEXT("maximum_speed"),TEXT("minimum_after_full_speed")})
				{
					const FString Field=FString(TEXT("authority_"))+Point;
					if(Has(*(FString(TEXT("sample."))+Point)) && !Telemetry->HasField(Field))
					{
						Snapshot(Remote,*Field);
						const bool Maximum=FCString::Strcmp(Point,TEXT("maximum_speed"))==0;
						Check(*Field,FMath::IsNearlyEqual(static_cast<float>(Remote->GetMesh()->GetPhysicsLinearVelocity().Size2D())*.036f,Maximum?300.f:50.f,Maximum?1.f:.5f));
					}
				}
			}
			if(Has(TEXT("client.done")))
			{
				for(const TCHAR* Name:{TEXT("moving_transform_received_on_server"),TEXT("automatic_takeoff_on_server"),TEXT("physical_bank_on_server"),TEXT("automatic_landing_requested_on_server"),TEXT("player_controls_ejected_module_on_server"),TEXT("player_returns_to_truck_and_same_module_attaches_on_server"),TEXT("authority_minimum_speed"),TEXT("authority_maximum_speed"),TEXT("authority_minimum_after_full_speed")})
				{ if(!Checks->HasField(Name)) { Check(Name,false); } }
				return Finish();
			}
			Save(false);return true;
		}
		if(Phase==0)
		{
			if(!Has(TEXT("drive.ready"))) { Save(false);return true; }
			// The owning client initializes its prediction body too; authority-only
			// placement is overwritten by pre-fixture client ground replication.
			Place(Car,FVector(0,0,FloorZ+15));Stage(1);
		}
		const double Age=FPlatformTime::Seconds()-StageTime;++Frames;
		if(Phase==1 && Age>1.) { Start=Car->GetActorLocation();Axes.Add(EKeys::Gamepad_RightTriggerAxis,1.f);Stage(2); }
		else if(Phase==2 && Age>2. && Frames>=60)
		{
			PriorSpeed=Car->GetVelocity().Size();Check(TEXT("accelerates_on_road"),PriorSpeed>300.f);Snapshot(Car,TEXT("road_before_transform"));
			Button(PC,EKeys::Gamepad_FaceButton_Left);Start=Car->GetActorLocation();Stage(3);
		}
		else if(Phase==3 && Age>.6)
		{
			Check(TEXT("transforms_while_accelerating"),Car->Modes->GetMode()==EMaskVehicleMode::Deploying && Car->GetVelocity().Size()>PriorSpeed*.8f && FVector::Dist2D(Start,Car->GetActorLocation())>100.f);
			Stage(4);
		}
		else if(Phase==4 && Car->Modes->GetMode()==EMaskVehicleMode::Flight && Age>3.)
		{
			Check(TEXT("automatic_small_takeoff"),Car->GetActorLocation().Z>FloorZ+100.f);Check(TEXT("same_masked_driver_after_takeoff"),Car==Original.Get() && Car->IsMaskVisible());
			Snapshot(Car,TEXT("takeoff"));Axes.Add(EKeys::Gamepad_RightTriggerAxis,0);Axes.Add(EKeys::Gamepad_LeftX,.65f);Axes.Add(EKeys::Gamepad_LeftY,.5f);PriorYaw=Car->GetActorRotation().Yaw;Stage(5);
		}
		else if(Phase==5 && Age>2.)
		{
			Check(TEXT("banks_right_when_turning_right"),Car->GetActorRightVector().Z<-.1f);Check(TEXT("pitches_up_when_climbing"),Car->GetActorRotation().Pitch>4.f);
			Check(TEXT("coordinated_turn_changes_heading"),FMath::Abs(FMath::FindDeltaAngleDegrees(PriorYaw,Car->GetActorRotation().Yaw))>20.f);
			Snapshot(Car,TEXT("bank_and_climb"));Shot(TEXT("bank-and-climb.png"));Axes.Add(EKeys::Gamepad_LeftX,0);Axes.Add(EKeys::Gamepad_LeftY,0);Axes.Add(EKeys::Gamepad_LeftTriggerAxis,1.f);Stage(6);
		}
		else if(Phase==6 && Age>10.)
		{
			Check(TEXT("plane_brake_keeps_minimum_speed_command"),FMath::IsNearlyEqual(Car->Dynamics->GetTargetAirspeedMPS()*3.6f,50.f,.1f));
			Check(TEXT("plane_cannot_hover_with_brake_held"),Car->GetVelocity().Size2D()>Car->Definition->Dynamics.MinimumAirspeedMPS*75.f);
			Check(TEXT("plane_reaches_50_kmh_under_braking"),FMath::IsNearlyEqual(static_cast<float>(Car->GetVelocity().Size2D())*.036f,50.f,Network?2.5f:.5f));
			PriorSpeed=Car->GetVelocity().Size2D();
			Snapshot(Car,TEXT("minimum_speed"));Axes.Add(EKeys::Gamepad_LeftTriggerAxis,0);Axes.Add(EKeys::Gamepad_RightTriggerAxis,1.f);Stage(60);
		}
		else if(Phase==60)
		{
			const float Maximum=Car->Definition->Dynamics.MaximumAirspeedMPS;
			if(Age>.5 && Age<1.5)
			{
				Check(TEXT("acceleration_to_300_is_progressive"),Car->Dynamics->GetTargetAirspeedMPS()<Maximum-1.f && Car->GetVelocity().Size2D()>PriorSpeed && Car->GetVelocity().Size2D()<PriorSpeed+1500.f);
				Snapshot(Car,TEXT("acceleration_ramp"));
			}
			if(Age>30.)
			{
				Check(TEXT("maximum_airspeed_command_is_300_kmh"),FMath::IsNearlyEqual(Maximum*3.6f,300.f,.1f) && FMath::IsNearlyEqual(Car->Dynamics->GetTargetAirspeedMPS(),Maximum,.1f));
				Check(TEXT("level_flight_reaches_300_kmh"),FMath::IsNearlyEqual(static_cast<float>(Car->GetVelocity().Size2D())*.036f,300.f,Network?6.f:1.f));
				Snapshot(Car,TEXT("maximum_speed"));PriorYaw=Car->GetActorRotation().Yaw;Axes.Add(EKeys::Gamepad_RightTriggerAxis,0);Axes.Add(EKeys::Gamepad_LeftX,1.f);Stage(600);
			}
		}
		else if(Phase==600 && Age>3.)
		{
			const float Turn=FMath::FindDeltaAngleDegrees(PriorYaw,Car->GetActorRotation().Yaw);
			Check(TEXT("high_speed_turn_exceeds_60_degrees_in_3_seconds"),Turn>60.f);
			Check(TEXT("high_speed_trajectory_follows_heading"),FMath::Abs(FMath::FindDeltaAngleDegrees(Car->GetActorRotation().Yaw,Car->GetVelocity().Rotation().Yaw))<25.f);
			Snapshot(Car,TEXT("high_speed_turn"));Axes.Add(EKeys::Gamepad_LeftX,0);PriorSpeed=Car->GetVelocity().Size2D();Axes.Add(EKeys::Gamepad_LeftTriggerAxis,1.f);Stage(61);
		}
		else if(Phase==61)
		{
			if(Age>.5 && Age<1.5)
			{
				Check(TEXT("braking_from_300_is_progressive"),Car->Dynamics->GetTargetAirspeedMPS()>Car->Definition->Dynamics.MinimumAirspeedMPS+1.f && Car->GetVelocity().Size2D()<PriorSpeed && Car->GetVelocity().Size2D()>PriorSpeed-1500.f);
				Snapshot(Car,TEXT("braking_ramp"));
			}
			if(Age>25.)
			{
				Check(TEXT("braking_from_300_returns_to_50_kmh"),FMath::IsNearlyEqual(Car->Dynamics->GetTargetAirspeedMPS()*3.6f,50.f,.1f) && FMath::IsNearlyEqual(static_cast<float>(Car->GetVelocity().Size2D())*.036f,50.f,Network?2.5f:.5f));
				Snapshot(Car,TEXT("minimum_after_full_speed"));Axes.Add(EKeys::Gamepad_LeftTriggerAxis,0);Axes.Add(EKeys::Gamepad_RightTriggerAxis,1.f);Button(PC,EKeys::Gamepad_FaceButton_Left);Stage(7);
				if(!Network) { Car->SetActorLocation(Car->GetActorLocation()+FVector(0,0,60000),false,nullptr,ETeleportType::TeleportPhysics);HighAltitudeFixture=true; }
			}
		}
		else if(Phase==7)
		{
			if(HighAltitudeFixture && Age>3.)
			{
				Check(TEXT("automatic_descent_without_ground_in_probe_range"),Car->GetVelocity().Z<-100.f && Car->Dynamics->GroundClearanceCM>=49999.f);
				Snapshot(Car,TEXT("high_altitude_descent"));
				// Separate near-ground fixture bounds test duration. No claim that a
				// complete 600m approach was flown; both branches use real forces.
				FVector P=Car->GetActorLocation();P.Z=FloorZ+1000.f;Car->SetActorLocation(P,false,nullptr,ETeleportType::TeleportPhysics);HighAltitudeFixture=false;
			}
			if(Car->Modes->GetMode()==EMaskVehicleMode::Landing) { Check(TEXT("x_starts_automatic_descent_from_altitude"),true); }
			if(Car->Modes->GetMode()==EMaskVehicleMode::Retracting)
			{ Check(TEXT("folding_starts_only_near_ground"),Car->GetActorLocation().Z-FloorZ<80.f); }
			if(Car->Modes->GetMode()==EMaskVehicleMode::Road)
			{
				Check(TEXT("automatically_returns_to_road_without_manual_descent"),true);Check(TEXT("landing_preserves_forward_motion"),Car->GetVelocity().Size2D()>500.f);
				Check(TEXT("ground_powertrain_restored"),CastChecked<UChaosWheeledVehicleMovementComponent>(Car->GetVehicleMovement())->bMechanicalSimEnabled);
				Snapshot(Car,TEXT("landed"));Shot(TEXT("landed.png"));Axes.Add(EKeys::Gamepad_RightTriggerAxis,0);Axes.Add(EKeys::Gamepad_LeftTriggerAxis,1.f);Stage(Network?11:8);
			}
		}
		else if(Phase==8 && Age>4.)
		{
			Place(Car,FVector(0,0,FloorZ+10));Car->GetMesh()->SetPhysicsLinearVelocity(FVector(1000,0,0));Start=Car->GetActorLocation();Energy10=Car->Dynamics->KineticEnergyKJ();Stage(9);
		}
		else if(Phase==9 && Car->GetVelocity().Size2D()<50.f)
		{
			Brake10=FVector::Dist2D(Start,Car->GetActorLocation());Telemetry->SetNumberField(TEXT("braking_10mps_cm"),Brake10);
			Place(Car,FVector(0,0,FloorZ+10));Car->GetMesh()->SetPhysicsLinearVelocity(FVector(2000,0,0));Start=Car->GetActorLocation();
			Check(TEXT("doubling_speed_quadruples_kinetic_energy"),FMath::IsNearlyEqual(Car->Dynamics->KineticEnergyKJ()/Energy10,4.f,.1f));Stage(10);
		}
		else if(Phase==10 && Car->GetVelocity().Size2D()<50.f)
		{
			const float D=FVector::Dist2D(Start,Car->GetActorLocation());Telemetry->SetNumberField(TEXT("braking_20mps_cm"),D);Check(TEXT("higher_speed_requires_longer_braking_distance"),D>Brake10*2.f);Stage(11);
		}
		else if(Phase==11 && Age>.8)
		{
			if(Network) { Signal(TEXT("spawn.rhino")); }
			else
			{
				auto* AI=World->SpawnActor<AVehicleBotController>();AI->TrainingIndex=0;CastChecked<ACustomGameMode>(World->GetAuthGameMode())->RestartPlayerAtTransform(AI,FTransform(FRotator::ZeroRotator,Car->GetActorLocation()+FVector(0,1500,0)));AI->SetActorTickEnabled(false);
			}
			Stage(12);
		}
		else if(Phase==12 && Age>1.)
		{
			for(TActorIterator<ARhinoPawn> It(World);It;++It) { Rhino=*It;break; }
			if(Rhino.IsValid()) { Module=Rhino->RearModule;Button(PC,EKeys::Gamepad_DPad_Up);Axes.Add(EKeys::Gamepad_LeftTriggerAxis,0);Axes.Add(EKeys::Gamepad_RightTriggerAxis,1.f);Stage(13); }
		}
		else if(Phase==13 && Car==Rhino.Get() && Age>2.)
		{
			PriorSpeed=Car->GetVelocity().Size();Check(TEXT("rhino_drives_before_deployment"),PriorSpeed>200.f);Button(PC,EKeys::Gamepad_FaceButton_Left);Stage(14);
		}
		else if(Phase==14 && Module.IsValid() && Module->bDetached)
		{
			Check(TEXT("same_module_ejects_immediately_while_truck_moves"),Age<1.f && Car->GetVelocity().Size()>PriorSpeed*.7f);
			Check(TEXT("module_inherits_velocity_with_rearward_kick"),FVector::DotProduct(Module->GetVelocity()-Car->GetVelocity(),Car->GetActorForwardVector())<-300.f);
			Snapshot(Car,TEXT("rhino_ejection"));Stage(15);
		}
		else if(Phase==15 && Car->Modes->GetMode()==EMaskVehicleMode::Combat && Age>1.) { Button(PC,EKeys::Gamepad_DPad_Up);Stage(16); }
		else if(Phase==16 && Car==Module.Get() && Age>1.)
		{
			Check(TEXT("player_drives_same_ejected_module"),Car->IsMaskVisible());Button(PC,EKeys::Gamepad_FaceButton_Left);Stage(17);
		}
		else if(Phase==17 && Car==Rhino.Get() && Age>.5)
		{
			Check(TEXT("recall_returns_player_to_same_truck"),true);Check(TEXT("same_module_teleports_and_attaches_without_docking"),Module->GetAttachParentActor()==Car && !Module->bDetached);
			Snapshot(Car,TEXT("rhino_recalled"));Shot(TEXT("rhino-recalled.png"));Stage(18);
		}
		else if(Phase==18 && Car->Modes->GetMode()==EMaskVehicleMode::Road)
		{ Button(PC,EKeys::Gamepad_FaceButton_Left);Stage(180); }
		else if(Phase==180 && Car->Modes->GetMode()==EMaskVehicleMode::Combat && Car->GetVelocity().Size()>300.f)
		{ PriorSpeed=Car->GetVelocity().Size();Button(PC,EKeys::Gamepad_FaceButton_Left);Stage(181); }
		else if(Phase==181 && Age>.4)
		{
			Snapshot(Car,TEXT("moving_truck_recall"));
			Check(TEXT("moving_truck_keeps_momentum_during_quick_recall"),Car->GetVelocity().Size()>PriorSpeed*.8f && !Module->bDetached && Module->GetAttachParentActor()==Car);Stage(182);
		}
		else if(Phase==182 && Car->Modes->GetMode()==EMaskVehicleMode::Road)
		{
			if(Network) { return Finish(); }
			Axes.Add(EKeys::Gamepad_RightTriggerAxis,0);Axes.Add(EKeys::Gamepad_LeftTriggerAxis,0);
			CastChecked<ACustomGameMode>(World->GetAuthGameMode())->SwitchPlayerVehicleTo(PC,Original.Get());Stage(19);
		}
		else if(Phase==19 && Car==Original.Get() && Age>.7)
		{
			for(TActorIterator<AVehicleBotController> It(World);It;++It) { It->SetActorTickEnabled(false); }
			auto* Proxy=DuplicateObject<UMaskVehicleDefinition>(Car->Definition,Car);Proxy->Dynamics.FlightModel=EMaskFlightModel::Rotorcraft;Car->Definition=Proxy;
			Place(Car,FVector(0,10000,FloorZ+10));Stage(20);
		}
		else if(Phase==20 && Age>1.) { Button(PC,EKeys::Gamepad_FaceButton_Left);Stage(21); }
		else if(Phase==21 && Car->Modes->GetMode()==EMaskVehicleMode::Flight && Age>7.)
		{
			Check(TEXT("rotorcraft_can_hover"),Car->GetVelocity().Size()<100.f && Car->GetActorLocation().Z>FloorZ+100.f);Snapshot(Car,TEXT("rotorcraft_hover"));
			Axes.Add(EKeys::Gamepad_RightTriggerAxis,1.f);Stage(22);
		}
		else if(Phase==22 && Age>2.)
		{
			Snapshot(Car,TEXT("rotorcraft_accelerating"));Check(TEXT("rotorcraft_tilts_forward_under_acceleration"),Car->GetActorRotation().Pitch<-4.f && Car->GetVelocity().Size2D()>100.f);Axes.Add(EKeys::Gamepad_RightTriggerAxis,0);Axes.Add(EKeys::Gamepad_LeftTriggerAxis,1.f);Stage(23);
		}
		else if(Phase==23 && Age>5.)
		{
			Snapshot(Car,TEXT("rotorcraft_braked_to_hover"));Check(TEXT("rotorcraft_returns_to_hover_after_braking"),Car->GetVelocity().Size2D()<100.f);
			Axes.Add(EKeys::Gamepad_LeftTriggerAxis,0);Button(PC,EKeys::Gamepad_FaceButton_Left);Stage(24);
		}
		else if(Phase==24 && Car->Modes->GetMode()==EMaskVehicleMode::Road)
		{ Check(TEXT("rotorcraft_lands_and_returns_to_road"),Car->GetActorLocation().Z<FloorZ+80.f);Snapshot(Car,TEXT("rotorcraft_landed"));return Finish(); }
		for(const auto& A:Axes) { PC->InputKey(FInputKeyEventArgs::CreateSimulated(A.Key,IE_Axis,A.Value,1,FInputDeviceId::CreateFromInternalId(0))); }
		Save(false);return true;
	}
};
TUniquePtr<FRun> Runner;
FAutoConsoleCommand Command(TEXT("MASK.DynamicsSmoke"),TEXT("Moving transformation, force-based flight, recall and rotorcraft probe."),FConsoleCommandWithArgsDelegate::CreateLambda([](const TArray<FString>& Args)
{
	if(Runner) { return; }Runner=MakeUnique<FRun>(Args.IsEmpty()?TEXT("solo"):Args[0]);
	FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda([](float Delta){return Runner->Tick(Delta);}));
}));
}
#endif
