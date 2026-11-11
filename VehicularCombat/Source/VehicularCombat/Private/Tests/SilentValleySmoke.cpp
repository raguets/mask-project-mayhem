#if !UE_BUILD_SHIPPING
#include "SilentValley/SilentValleyRoad.h"
#include "MASK/ThunderhawkPawn.h"
#include "MASK/MaskVehicleDefinition.h"
#include "MASK/MaskVehicleModeComponent.h"
#include "Components/SplineComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Materials/MaterialInterface.h"
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

namespace SilentValleySmoke
{
class FRun
{
    FString Directory,Vehicle;double Started=FPlatformTime::Seconds();bool Initialized=false;
    float Progress=0,LastProgress=0,StuckSeconds=0,SimulationSeconds=0,NoContactSeconds=0,LongestNoContact=0,MaxCrossTrack=0,MaxSpeed=0,Wheelbase=300,LastSave=0;
    int32 NextPOI=0,DiagnosticFrame=0;TWeakObjectPtr<ASilentValleyRoad> Road;
    TSharedRef<FJsonObject> Checks=MakeShared<FJsonObject>(),Stats=MakeShared<FJsonObject>();
    const TArray<FVector> POIs={FVector(-133300,-108350,8000),FVector(-75000,-78000,9000),FVector(70000,25000,15500),FVector(65000,95000,10000),FVector(-55000,125000,16000)};
    TArray<float> POIDistances;
    void Check(const TCHAR* Name,bool Value) { Checks->SetBoolField(Name,Value); }
    void Save(bool Complete)
    {
        bool Passed=Complete;for(const auto& Check:Checks->Values) { Passed&=Check.Value->AsBool(); }
        auto Report=MakeShared<FJsonObject>();Report->SetBoolField(TEXT("passed"),Passed);Report->SetBoolField(TEXT("complete"),Complete);Report->SetStringField(TEXT("vehicle"),Vehicle);
        Report->SetNumberField(TEXT("wall_seconds"),FPlatformTime::Seconds()-Started);Report->SetNumberField(TEXT("simulated_seconds"),SimulationSeconds);
        Report->SetNumberField(TEXT("progress_m"),Progress/100);Report->SetNumberField(TEXT("max_cross_track_m"),MaxCrossTrack/100);Report->SetNumberField(TEXT("max_speed_kmh"),MaxSpeed*.036);
        Report->SetNumberField(TEXT("longest_wheel_contact_loss_s"),LongestNoContact);Report->SetObjectField(TEXT("checks"),Checks);Report->SetObjectField(TEXT("telemetry"),Stats);
        Report->SetStringField(TEXT("method"),TEXT("Actual Chaos pawn, pure-pursuit controller injecting Xbox steering/throttle/brake. No teleportation or kinematic route following. Collision probe is separate from driving. Screenshots are real game frames."));
        FString Json;FJsonSerializer::Serialize(Report,TJsonWriterFactory<>::Create(&Json));FFileHelper::SaveStringToFile(Json,*(Directory/TEXT("drive.json")));
    }
    bool Finish(APlayerController* PC,bool Complete)
    { Check(TEXT("route_completed_without_recovery"),Complete);Save(Complete);PC->ConsoleCommand(TEXT("quit"));return false; }
    void Axis(APlayerController* PC,FKey Key,float Value) { PC->InputKey(FInputKeyEventArgs::CreateSimulated(Key,IE_Axis,Value,1,FInputDeviceId::CreateFromInternalId(0))); }
public:
    explicit FRun(FString Name):Vehicle(Name)
    { FParse::Value(FCommandLine::Get(),TEXT("MigrationReportDir="),Directory);if(Directory.IsEmpty()) { Directory=FPaths::ProjectSavedDir()/TEXT("SilentValley/drive"); }IFileManager::Get().MakeDirectory(*Directory,true); }
    bool Tick(float Delta)
    {
        UWorld* World=nullptr;for(const auto& Context:GEngine->GetWorldContexts()) { if(Context.WorldType==EWorldType::Game) { World=Context.World();break; } }
        if(!World) { return true; }auto* PC=World->GetFirstPlayerController();auto* Car=PC?Cast<AThunderhawkPawn>(PC->GetPawn()):nullptr;
        if(!Car || !Car->Definition) { if(PC && World->GetTimeSeconds()>15) { Check(TEXT("vehicle_spawned"),false);return Finish(PC,false); }return true; }
        if(!Initialized)
        {
            if(World->GetTimeSeconds()<4) { return true; }
            for(TActorIterator<ASilentValleyRoad> It(World);It;++It) { Road=*It;break; }if(!Road.IsValid()) { Check(TEXT("road_loaded"),false);return Finish(PC,false); }
            Initialized=true;Check(TEXT("new_map_loaded"),World->GetMapName().Contains(TEXT("SilentValley")));Check(TEXT("existing_requested_vehicle"),Car->Definition->VehicleName==Vehicle);
            Check(TEXT("starts_inside_existing_base"),FVector::Dist2D(Car->GetActorLocation(),Road->RouteLocation(0))<300);
            float Front=-BIG_NUMBER,Rear=BIG_NUMBER;for(const auto& W:Car->Definition->Wheels) { Front=FMath::Max(Front,static_cast<float>(W.Center.X));Rear=FMath::Min(Rear,static_cast<float>(W.Center.X)); }if(Front>Rear) { Wheelbase=Front-Rear; }
            for(const auto& P:POIs) { POIDistances.Add(Road->ClosestDistance(P)); }
            // Three parallel downward wheel-lane probes, including every seam.
            int32 Missing=0,Probes=0;float MaxGrade=0,MaxStep=0;
            FCollisionQueryParams Query(SCENE_QUERY_STAT(SilentValleyRoadProbe),false,Car);TArray<AActor*> Attached;Car->GetAttachedActors(Attached,true,true);Query.AddIgnoredActors(Attached);
            for(float D=0;D<Road->RouteLengthCM();D+=1000)
            {
                const FVector P=Road->RouteLocation(D),Q=Road->RouteLocation(FMath::Min(D+100.f,Road->RouteLengthCM()));MaxGrade=FMath::Max(MaxGrade,static_cast<float>(FMath::Abs(Q.Z-P.Z)/FMath::Max(1.,FVector::Dist2D(P,Q))));
                const FVector Right=Road->RouteRotation(D).RotateVector(FVector::RightVector);
                for(float Lateral:{-1.f,0.f,1.f})
                {
                    const FVector Sample=P+Right*Lateral*(D<4500?140.f:440.f);FHitResult Hit;++Probes;
                    if(!World->LineTraceSingleByChannel(Hit,Sample+FVector(0,0,35),Sample-FVector(0,0,300),ECC_Visibility,Query)) { ++Missing; }
                    else { MaxStep=FMath::Max(MaxStep,static_cast<float>(FMath::Abs(Hit.ImpactPoint.Z-Sample.Z))); }
                }
            }
            Stats->SetNumberField(TEXT("probe_count"),Probes);Stats->SetNumberField(TEXT("missing_ground_probes"),Missing);Stats->SetNumberField(TEXT("max_road_grade_percent"),MaxGrade*100);Stats->SetNumberField(TEXT("max_probe_surface_offset_cm"),MaxStep);
            Check(TEXT("continuous_ground_probes"),Missing==0);Check(TEXT("road_grade_below_10_percent"),MaxGrade<.1f);
            UE_LOG(LogTemp,Display,TEXT("SV_DRIVE_START vehicle=%s length_m=%.1f probes=%d missing=%d grade=%.2f"),*Vehicle,Road->RouteLengthCM()/100,Probes,Missing,MaxGrade*100);
        }
        const float Dt=World->GetDeltaSeconds();SimulationSeconds+=Dt;
        if(FPlatformTime::Seconds()-Started>900 || SimulationSeconds>1800) { Check(TEXT("timeout"),false);return Finish(PC,false); }
        auto* Move=CastChecked<UChaosWheeledVehicleMovementComponent>(Car->GetVehicleMovement());const FVector Position=Car->GetActorLocation();const float Speed=FMath::Abs(Move->GetForwardSpeed());
        float Best=BIG_NUMBER,Closest=Progress;
        for(float D=FMath::Max(0.f,Progress-500);D<=FMath::Min(Progress+3500,Road->RouteLengthCM());D+=100)
        { const float Dist=FVector::DistSquared2D(Position,Road->RouteLocation(D));if(Dist<Best) { Best=Dist;Closest=D; } }
        Progress=FMath::Max(Progress,Closest);MaxCrossTrack=FMath::Max(MaxCrossTrack,FMath::Sqrt(Best));MaxSpeed=FMath::Max(MaxSpeed,Speed);
        const float Look=FMath::Clamp(350+Speed*.35f,450.f,800.f);const FVector Target=Road->RouteLocation(FMath::Min(Progress+Look,Road->RouteLengthCM()));
        const float Angle=FMath::DegreesToRadians(FMath::FindDeltaAngleDegrees(Car->GetActorRotation().Yaw,(Target-Position).Rotation().Yaw));
        const float Steering=FMath::Clamp(FMath::RadiansToDegrees(FMath::Atan(2*Wheelbase*FMath::Sin(Angle)/Look))/45.f,-1.f,1.f);
        const float Bend=FMath::Abs(FMath::FindDeltaAngleDegrees(Road->RouteRotation(Progress+1000).Yaw,Road->RouteRotation(Progress+4000).Yaw));
        const float Desired=Progress<5000?300.f:FMath::Clamp(1000-Bend*18,300.f,1000.f);
        // Legacy Xbox input remaps a 25% dead zone. Encode the desired physical
        // steering through that existing mapping rather than silently understeering.
        const float Stick=FMath::IsNearlyZero(Steering,.001f)?0.f:FMath::Sign(Steering)*(.25f+.75f*FMath::Abs(Steering));
        Axis(PC,EKeys::Gamepad_LeftX,Stick);Axis(PC,EKeys::Gamepad_RightTriggerAxis,FMath::Clamp((Desired-Speed)/450.f,0.f,.8f));Axis(PC,EKeys::Gamepad_LeftTriggerAxis,Speed>Desired+100?FMath::Clamp((Speed-Desired)/500.f,0.f,1.f):0.f);
        int32 Contacts=0;for(int32 I=0;I<Move->Wheels.Num();++I) { Contacts+=Move->GetWheelState(I).bInContact?1:0; }
        NoContactSeconds=Contacts==0?NoContactSeconds+Dt:0;LongestNoContact=FMath::Max(LongestNoContact,NoContactSeconds);
        if(Progress<LastProgress+100) { StuckSeconds+=Dt; }else { LastProgress=Progress;StuckSeconds=0; }
        if(NextPOI<POIs.Num() && Progress>=POIDistances[NextPOI]-1000)
        {
            Check(*FString::Printf(TEXT("reached_zone_%d"),NextPOI),true);UE_LOG(LogTemp,Display,TEXT("SV_DRIVE_POI vehicle=%s zone=%d progress=%.1fm"),*Vehicle,NextPOI,Progress/100);
            if(!FParse::Param(FCommandLine::Get(),TEXT("NullRHI"))) { FScreenshotRequest::RequestScreenshot(Directory/FString::Printf(TEXT("zone-%d.png"),NextPOI),true,false); }++NextPOI;
        }
        if(StuckSeconds>18 || MaxCrossTrack>320 || Position.Z<0)
        {
            FCollisionQueryParams Query(SCENE_QUERY_STAT(SilentValleyBlockage),true,Car);Query.bReturnFaceIndex=true;TArray<AActor*> Attached;Car->GetAttachedActors(Attached,true,true);Query.AddIgnoredActors(Attached);
            const auto Bounds=Car->Definition->Chassis->GetImportedBounds();const FVector Center=Car->GetActorTransform().TransformPosition(Bounds.Origin);FHitResult Hit;
            if(World->SweepSingleByChannel(Hit,Center,Center+Car->GetActorForwardVector()*150,Car->GetActorQuat(),ECC_Visibility,FCollisionShape::MakeBox(Bounds.BoxExtent),Query))
            { Stats->SetStringField(TEXT("blocking_actor"),GetNameSafe(Hit.GetActor()));Stats->SetStringField(TEXT("blocking_location"),Hit.ImpactPoint.ToString());int32 Section=0;Stats->SetStringField(TEXT("blocking_material"),Hit.GetComponent()?GetNameSafe(Hit.GetComponent()->GetMaterialFromCollisionFaceIndex(Hit.FaceIndex,Section)):TEXT("none")); }
            Stats->SetStringField(TEXT("failure_position"),Position.ToString());Stats->SetStringField(TEXT("failure_rotation"),Car->GetActorRotation().ToString());Stats->SetNumberField(TEXT("failure_speed_cm_s"),Speed);Stats->SetNumberField(TEXT("failure_contacts"),Contacts);Check(TEXT("no_stuck_or_departure"),false);return Finish(PC,false);
        }
        const bool FullRoute=FParse::Param(FCommandLine::Get(),TEXT("SVFullRoute"));
        if(NextPOI==POIs.Num() && Progress>(FullRoute?Road->RouteLengthCM()-300.f:POIDistances.Last()+2000))
        { Check(TEXT("no_stuck_or_departure"),true);Check(TEXT("wheels_remain_supported"),LongestNoContact<.7);Check(TEXT("no_unwanted_transformation"),Car->Modes->GetMode()==EMaskVehicleMode::Road);return Finish(PC,true); }
        if(DiagnosticFrame<3 && SimulationSeconds>1+DiagnosticFrame*7 && !FParse::Param(FCommandLine::Get(),TEXT("NullRHI"))) { FScreenshotRequest::RequestScreenshot(Directory/FString::Printf(TEXT("departure-%d.png"),DiagnosticFrame),true,false);++DiagnosticFrame; }
        if(SimulationSeconds-LastSave>2) { LastSave=SimulationSeconds;Stats->SetStringField(TEXT("latest_position"),Position.ToString());Stats->SetStringField(TEXT("rotation"),Car->GetActorRotation().ToString());Stats->SetNumberField(TEXT("requested_steer"),Steering);Stats->SetNumberField(TEXT("steering_input"),Move->GetSteeringInput());Stats->SetNumberField(TEXT("throttle"),Move->GetThrottleInput());Stats->SetNumberField(TEXT("brake"),Move->GetBrakeInput());Stats->SetNumberField(TEXT("contacts"),Contacts);Stats->SetNumberField(TEXT("speed_cm_s"),Speed);Save(false); }
        return true;
    }
};
TUniquePtr<FRun> Runner;
FAutoConsoleCommand Command(TEXT("MASK.SilentValleyDrive"),TEXT("Drive the real vehicle from the base to the five Silent Valley POIs."),FConsoleCommandWithArgsDelegate::CreateLambda([](const TArray<FString>& Args)
{ if(!Runner) { Runner=MakeUnique<FRun>(Args.IsEmpty()?TEXT("Thunderhawk"):Args[0]);FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda([](float D){return Runner->Tick(D);})); } }));
}
#endif
