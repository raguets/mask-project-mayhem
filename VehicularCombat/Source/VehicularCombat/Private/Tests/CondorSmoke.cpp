#include "CoreMinimal.h"
#if !UE_BUILD_SHIPPING
#include "MASK/CondorPawn.h"
#include "MASK/MaskVehicleDefinition.h"
#include "MASK/MaskVehicleModeComponent.h"
#include "MASK/MaskDynamicsComponent.h"
#include "Core/CustomGameMode.h"
#include "SilentValley/SilentValleyRoad.h"
#include "AI/VehicleBotController.h"
#include "ChaosWheeledVehicleMovementComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Components/HealthComponent.h"
#include "Containers/Ticker.h"
#include "Dom/JsonObject.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "HAL/IConsoleManager.h"
#include "HAL/FileManager.h"
#include "InputKeyEventArgs.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonSerializer.h"
#include "UnrealClient.h"

namespace CondorSmoke
{
class FRun
{
    int32 Stage=0;double Started=FPlatformTime::Seconds(),Since=Started,LastSnapshot=0;
    FString Directory;FVector Start;float StartYaw=0,FlightHeight=0,PitchDuringAcceleration=0,PeakRoadRoll=0,MinimumSupportClearance=100000;
    int32 SteeringPhase=0;
    TWeakObjectPtr<ACondorPawn> Condor;
    TSharedRef<FJsonObject> Checks=MakeShared<FJsonObject>(),Data=MakeShared<FJsonObject>();
    void Check(const TCHAR* Name,bool Value) { Checks->SetBoolField(Name,Value); }
    void Next(int32 Value) { Stage=Value;Since=FPlatformTime::Seconds();UE_LOG(LogTemp,Display,TEXT("CONDOR_TEST stage=%d"),Stage); }
    void Key(APlayerController* PC,FKey Value,bool Down) { PC->InputKey(FInputKeyEventArgs::CreateSimulated(Value,Down?IE_Pressed:IE_Released,Down?1.f:0.f,-1,FInputDeviceId::CreateFromInternalId(0))); }
    void Shot(const TCHAR* Name) { if(!FParse::Param(FCommandLine::Get(),TEXT("NullRHI"))) { FScreenshotRequest::RequestScreenshot(Directory/Name,true,false); } }
    bool Finish(bool Timeout=false)
    {
        Check(TEXT("no_timeout"),!Timeout);bool Passed=!Timeout;for(const auto& Item:Checks->Values) { Passed &= Item.Value->AsBool(); }
        auto Report=MakeShared<FJsonObject>();Report->SetBoolField(TEXT("passed"),Passed);Report->SetObjectField(TEXT("checks"),Checks);Report->SetObjectField(TEXT("telemetry"),Data);Report->SetNumberField(TEXT("stage"),Stage);
        Report->SetStringField(TEXT("fixture"),TEXT("Actual Pinewoods five-family fleet. Initial road placement at200m on the valley approach and initial zero velocity only. Alternating road turns, forward leg, brake to hover, turn IN PLACE, climb then land. The former800m mountain fixture left the road and landed on an unsuitable steep slope. All subsequent motion through actual pilot input/dynamics. No airborne teleport or velocity reset."));
        FString Text;FJsonSerializer::Serialize(Report,TJsonWriterFactory<>::Create(&Text));FFileHelper::SaveStringToFile(Text,*(Directory/TEXT("condor.json")));FPlatformMisc::RequestExit(false);return false;
    }
public:
    FRun() { FParse::Value(FCommandLine::Get(),TEXT("MigrationReportDir="),Directory);if(Directory.IsEmpty()) { Directory=FPaths::ProjectSavedDir()/TEXT("Art/condor-smoke"); }IFileManager::Get().MakeDirectory(*Directory,true); }
    bool Tick(float)
    {
        if(FPlatformTime::Seconds()-Started>160.) { return Finish(true); }
        UWorld* W=nullptr;for(const auto& C:GEngine->GetWorldContexts()) { if(C.WorldType==EWorldType::Game) { W=C.World();break; } }
        auto* PC=W?W->GetFirstPlayerController():nullptr;if(!PC) { return true; }
        const double Elapsed=FPlatformTime::Seconds()-Since;
        if(Condor.IsValid() && FPlatformTime::Seconds()-LastSnapshot>2.)
        {
            LastSnapshot=FPlatformTime::Seconds();auto Snapshot=MakeShared<FJsonObject>();auto* Car=Condor.Get();
            Snapshot->SetNumberField(TEXT("stage"),Stage);Snapshot->SetNumberField(TEXT("mode"),static_cast<int32>(Car->Modes->GetMode()));
            Snapshot->SetStringField(TEXT("position"),Car->GetActorLocation().ToString());Snapshot->SetStringField(TEXT("rotation"),Car->GetActorRotation().ToString());Snapshot->SetStringField(TEXT("velocity"),Car->GetVelocity().ToString());
            Snapshot->SetNumberField(TEXT("ground_clearance_cm"),Car->Dynamics->GroundClearanceCM);Snapshot->SetNumberField(TEXT("target_speed_mps"),Car->Dynamics->GetTargetAirspeedMPS());
            if(auto* Health=Car->FindComponentByClass<UHealthComponent>()) { Snapshot->SetNumberField(TEXT("health"),Health->CurrentHealth); }
            Snapshot->SetStringField(TEXT("mode_refusal"),Car->Modes->LastRefusal);Data->SetObjectField(TEXT("last_snapshot"),Snapshot);
            FString Text;FJsonSerializer::Serialize(Snapshot,TJsonWriterFactory<>::Create(&Text));FFileHelper::SaveStringToFile(Text,*(Directory/TEXT("progress.json")));
        }
        if(Stage==0 && W->GetTimeSeconds()>5.f)
        {
            TSet<FString> Names;for(TActorIterator<AThunderhawkPawn> It(W);It;++It) { if(It->Definition) { Names.Add(It->Definition->VehicleName); }if(auto* C=Cast<ACondorPawn>(*It)) { Condor=C; } }
            Check(TEXT("pinewoods_map"),W->GetMapName().Contains(TEXT("SilentValley")));
            Check(TEXT("all_five_families"),Names.Contains(TEXT("Thunderhawk")) && Names.Contains(TEXT("Rhino")) && Names.Contains(TEXT("Hurricane")) && Names.Contains(TEXT("Raven")) && Names.Contains(TEXT("Condor")));
            if(!Condor.IsValid()) { Check(TEXT("condor_spawned"),false);return Finish(); }
            auto* GM=Cast<ACustomGameMode>(W->GetAuthGameMode());Check(TEXT("switch_to_condor"),GM && GM->SwitchPlayerVehicleTo(PC,Condor.Get()));
            auto* Car=Condor.Get();auto* Def=Car->Definition.Get();
            Check(TEXT("brad_and_hocus_pocus"),Def && Def->DriverName==TEXT("Brad Turner") && Def->Driver && Def->Mask && Def->MaskName==TEXT("Hocus Pocus"));
            Check(TEXT("rotorcraft_zero_minimum"),Def && Def->bSupportsFlight && Def->Dynamics.FlightModel==EMaskFlightModel::Rotorcraft && Def->Dynamics.MinimumAirspeedMPS==0.f);
            Check(TEXT("exactly_two_wheels"),Def && Def->Wheels.Num()==2);
            Check(TEXT("own_locomotion"),Def && Def->DriverLocomotion && Def->DriverJump);
            int32 RotorParts=0;for(const auto& Part:Def->Parts) { RotorParts+=Part.RotorSpeedDegrees>0.f; }
            Check(TEXT("both_rotors_animated"),RotorParts>=3);
            for(TActorIterator<AVehicleBotController> It(W);It;++It) { It->SetActorTickEnabled(false); }
            for(TActorIterator<ASilentValleyRoad> It(W);It;++It) { Car->SetActorLocationAndRotation(It->RouteLocation(20000)+FVector(0,0,30),It->RouteRotation(20000),false,nullptr,ETeleportType::TeleportPhysics);break; }
            Car->GetMesh()->SetPhysicsLinearVelocity(FVector::ZeroVector);Car->GetMesh()->SetPhysicsAngularVelocityInRadians(FVector::ZeroVector);Next(1);
        }
        else if(Stage==1 && Elapsed>2.) { Start=Condor->GetActorLocation();Key(PC,EKeys::W,true);Next(2); }
        else if(Stage==2)
        {
            PeakRoadRoll=FMath::Max(PeakRoadRoll,FMath::Abs(Condor->GetActorRotation().Roll));
            if(SteeringPhase==0 && Elapsed>1.) { Key(PC,EKeys::D,true);SteeringPhase=1; }
            if(SteeringPhase==1 && Elapsed>2.) { Key(PC,EKeys::D,false);Key(PC,EKeys::A,true);SteeringPhase=2; }
            if(SteeringPhase==2 && Elapsed>3.) { Key(PC,EKeys::A,false);SteeringPhase=3; }
            TArray<UStaticMeshComponent*> Meshes;Condor->GetComponents(Meshes);
            FCollisionQueryParams Query(SCENE_QUERY_STAT(CondorSupportRoad),false,Condor.Get());
            TArray<AActor*> Attached;Condor->GetAttachedActors(Attached,true,true);Query.AddIgnoredActors(Attached);
            for(auto* Component:Meshes)
            {
                if(!Component->GetStaticMesh() || !Component->GetStaticMesh()->GetName().Contains(TEXT("RotorSupport"))) { continue; }
                const FBox Box=Component->GetStaticMesh()->GetBoundingBox();
                for(int32 Corner=0;Corner<4;++Corner)
                {
                    const FVector Point=Component->GetComponentTransform().TransformPosition(FVector(Corner&1?Box.Max.X:Box.Min.X,Corner&2?Box.Max.Y:Box.Min.Y,Box.Min.Z));
                    FHitResult Hit;if(W->LineTraceSingleByChannel(Hit,Point+FVector(0,0,300),Point-FVector(0,0,500),ECC_Vehicle,Query))
                    { MinimumSupportClearance=FMath::Min(MinimumSupportClearance,static_cast<float>(Point.Z-Hit.ImpactPoint.Z)); }
                }
            }
            if(Elapsed<=5.) { return true; }
            const float Distance=FVector::Dist2D(Start,Condor->GetActorLocation());Check(TEXT("road_drives"),Distance>300.f);Check(TEXT("road_stays_upright"),FMath::Abs(Condor->GetActorRotation().Roll)<25.f);
            Check(TEXT("alternating_turns_stay_balanced"),PeakRoadRoll<18.f);
            Check(TEXT("folded_support_clears_road"),MinimumSupportClearance>3.f && MinimumSupportClearance<100000.f);
            Data->SetNumberField(TEXT("peak_road_roll_degrees"),PeakRoadRoll);Data->SetNumberField(TEXT("minimum_support_bbox_clearance_cm"),MinimumSupportClearance);
            Data->SetNumberField(TEXT("road_distance_cm"),Distance);Shot(TEXT("road.png"));
            Check(TEXT("transform_requested_while_moving"),Condor->GetVelocity().Size2D()>200.f);
            Condor->Modes->ServerToggleMode();Check(TEXT("moving_transform_accepted"),Condor->Modes->GetMode()==EMaskVehicleMode::Deploying);Next(3);
        }
        else if(Stage==3 && Condor->Modes->GetMode()==EMaskVehicleMode::Flight) { Key(PC,EKeys::W,false);Key(PC,EKeys::S,true);Next(4); }
        else if(Stage==4 && Elapsed>15.)
        {
            Check(TEXT("automatic_takeoff"),Condor->Dynamics->GroundClearanceCM>140.f);
            Check(TEXT("full_brake_commands_hover"),Condor->Dynamics->GetTargetAirspeedMPS()<.05f);
            Check(TEXT("stationary_hover_speed"),Condor->GetVelocity().Size2D()<100.f && FMath::Abs(Condor->GetVelocity().Z)<60.f);
            Data->SetNumberField(TEXT("hover_speed_mps"),Condor->GetVelocity().Size()*.01);Data->SetNumberField(TEXT("takeoff_clearance_cm"),Condor->Dynamics->GroundClearanceCM);
            Start=Condor->GetActorLocation();Shot(TEXT("hover.png"));Next(5);
        }
        else if(Stage==5 && Elapsed>3.)
        {
            Check(TEXT("hover_position_holds"),FVector::Dist2D(Start,Condor->GetActorLocation())<150.f && FMath::Abs(Start.Z-Condor->GetActorLocation().Z)<100.f);
            Key(PC,EKeys::S,false);Key(PC,EKeys::W,true);Start=Condor->GetActorLocation();Next(6);
        }
        else if(Stage==6)
        {
            PitchDuringAcceleration=FMath::Min(PitchDuringAcceleration,Condor->GetActorRotation().Pitch);
            if(Elapsed>5.)
            {
                Check(TEXT("forward_flight_accelerates"),Condor->GetVelocity().Size2D()>400.f && FVector::Dist2D(Start,Condor->GetActorLocation())>1000.f);
                Check(TEXT("nose_down_in_forward_flight"),PitchDuringAcceleration< -2.f && Condor->GetActorRotation().Pitch<-.5f);
                Data->SetNumberField(TEXT("forward_pitch_degrees"),Condor->GetActorRotation().Pitch);Data->SetNumberField(TEXT("peak_nose_down_degrees"),PitchDuringAcceleration);Data->SetNumberField(TEXT("forward_speed_mps"),Condor->GetVelocity().Size2D()*.01);
                Shot(TEXT("forward.png"));Key(PC,EKeys::W,false);Key(PC,EKeys::S,true);Next(7);
            }
        }
        else if(Stage==7 && Elapsed>12.)
        {
            Check(TEXT("brakes_back_to_stationary_hover"),Condor->Dynamics->GetTargetAirspeedMPS()<.05f && Condor->GetVelocity().Size2D()<100.f);
            Key(PC,EKeys::S,false);Start=Condor->GetActorLocation();StartYaw=Condor->GetActorRotation().Yaw;Key(PC,EKeys::D,true);Next(8);
        }
        else if(Stage==8 && Elapsed>3.)
        {
            Check(TEXT("rotorcraft_turns_while_hovering"),FMath::Abs(FMath::FindDeltaAngleDegrees(StartYaw,Condor->GetActorRotation().Yaw))>40.f && FVector::Dist2D(Start,Condor->GetActorLocation())<150.f);
            Key(PC,EKeys::D,false);Start=Condor->GetActorLocation();Key(PC,EKeys::R,true);Next(9);
        }
        else if(Stage==9 && Elapsed>3.)
        {
            Check(TEXT("rotorcraft_climbs_from_hover"),Condor->GetActorLocation().Z>Start.Z+200.f);Key(PC,EKeys::R,false);Key(PC,EKeys::S,false);Condor->Modes->ServerToggleMode();Next(10);
        }
        else if(Stage==10 && Condor->Modes->GetMode()==EMaskVehicleMode::Road) { Check(TEXT("lands_and_retracts"),true);Data->SetNumberField(TEXT("landing_and_retraction_seconds"),Elapsed);Check(TEXT("direct_landing_under_12_seconds"),Elapsed<12.);Shot(TEXT("landed.png"));Next(11); }
        else if(Stage==11 && Elapsed>2.) { Check(TEXT("landed_upright"),FMath::Abs(Condor->GetActorRotation().Roll)<25.f);return Finish(); }
        return true;
    }
};
TUniquePtr<FRun> Run;
FAutoConsoleCommand Command(TEXT("MASK.CondorSmoke"),TEXT("Actual Condor on Pinewoods: two-wheel road, hover, tilt, braking, climb, landing."),FConsoleCommandDelegate::CreateLambda([](){if(!Run) { Run=MakeUnique<FRun>();FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda([](float D){return Run->Tick(D);})); }}));
}
#endif
