#include "CoreMinimal.h"
#if !UE_BUILD_SHIPPING
#include "MASK/RavenPawn.h"
#include "MASK/MaskVehicleDefinition.h"
#include "MASK/MaskVehicleModeComponent.h"
#include "MASK/MaskDynamicsComponent.h"
#include "Core/CustomGameMode.h"
#include "SilentValley/SilentValleyRoad.h"
#include "AI/VehicleBotController.h"
#include "ChaosWheeledVehicleMovementComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
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

namespace RavenSmoke
{
class FRun
{
    int32 Stage=0;double Started=FPlatformTime::Seconds(),Since=Started;
    FString Directory;FVector Start;float StartYaw=0;TWeakObjectPtr<ARavenPawn> Raven;
    TSharedRef<FJsonObject> Checks=MakeShared<FJsonObject>(),Data=MakeShared<FJsonObject>();
    void Check(const TCHAR* Name,bool Value) { Checks->SetBoolField(Name,Value); }
    void Next(int32 Value) { Stage=Value;Since=FPlatformTime::Seconds(); }
    void Key(APlayerController* PC,FKey Value,bool Down) { PC->InputKey(FInputKeyEventArgs::CreateSimulated(Value,Down?IE_Pressed:IE_Released,Down?1.f:0.f,-1,FInputDeviceId::CreateFromInternalId(0))); }
    void Shot(const TCHAR* Name) { if(!FParse::Param(FCommandLine::Get(),TEXT("NullRHI"))) { FScreenshotRequest::RequestScreenshot(Directory/Name,true,false); } }
    bool Finish(bool Timeout=false)
    {
        Check(TEXT("no_timeout"),!Timeout);bool Passed=!Timeout;for(const auto& Item:Checks->Values) { Passed &= Item.Value->AsBool(); }
        auto Report=MakeShared<FJsonObject>();Report->SetBoolField(TEXT("passed"),Passed);Report->SetObjectField(TEXT("checks"),Checks);Report->SetObjectField(TEXT("telemetry"),Data);Report->SetNumberField(TEXT("stage"),Stage);
        Report->SetStringField(TEXT("fixture"),TEXT("Actual Pinewoods map, four-vehicle fleet, explicit placement on road at800m. After transformation, explicit40m altitude/zero-velocity fixture tests acceleration under full brake, then turn and landing. Injected keyboard; not manual play."));
        FString Text;FJsonSerializer::Serialize(Report,TJsonWriterFactory<>::Create(&Text));FFileHelper::SaveStringToFile(Text,*(Directory/TEXT("raven.json")));FPlatformMisc::RequestExit(false);return false;
    }
public:
    FRun() { FParse::Value(FCommandLine::Get(),TEXT("MigrationReportDir="),Directory);if(Directory.IsEmpty()) { Directory=FPaths::ProjectSavedDir()/TEXT("Art/raven-smoke"); }IFileManager::Get().MakeDirectory(*Directory,true); }
    bool Tick(float)
    {
        if(FPlatformTime::Seconds()-Started>150.) { return Finish(true); }
        UWorld* W=nullptr;for(const auto& C:GEngine->GetWorldContexts()) { if(C.WorldType==EWorldType::Game) { W=C.World();break; } }
        auto* PC=W?W->GetFirstPlayerController():nullptr;if(!PC) { return true; }
        const double Elapsed=FPlatformTime::Seconds()-Since;
        if(Stage==0 && W->GetTimeSeconds()>5.f)
        {
            TSet<FString> Names;for(TActorIterator<AThunderhawkPawn> It(W);It;++It) { if(It->Definition) { Names.Add(It->Definition->VehicleName); }if(auto* R=Cast<ARavenPawn>(*It)) { Raven=R; } }
            Check(TEXT("pinewoods_map"),W->GetMapName().Contains(TEXT("SilentValley")));
            Check(TEXT("all_four_vehicle_families_present"),Names.Contains(TEXT("Thunderhawk")) && Names.Contains(TEXT("Rhino")) && Names.Contains(TEXT("Hurricane")) && Names.Contains(TEXT("Raven")));
            if(!Raven.IsValid()) { Check(TEXT("raven_spawned"),false);return Finish(); }
            auto* GM=Cast<ACustomGameMode>(W->GetAuthGameMode());Check(TEXT("switch_to_raven"),GM && GM->SwitchPlayerVehicleTo(PC,Raven.Get()));
            auto* Car=Raven.Get();Check(TEXT("definition_and_calhoun"),Car->Definition && Car->Definition->DriverName==TEXT("Calhoun Burns") && Car->Definition->Driver && Car->Definition->Mask);
            Check(TEXT("fixed_wing_no_hover"),Car->Definition->Dynamics.FlightModel==EMaskFlightModel::FixedWing && Car->Definition->Dynamics.MinimumAirspeedMPS>5.f);
            Check(TEXT("four_road_wheels"),Car->Definition->Wheels.Num()==4);
            for(TActorIterator<ASilentValleyRoad> It(W);It;++It) { Car->SetActorLocationAndRotation(It->RouteLocation(80000)+FVector(0,0,30),It->RouteRotation(80000),false,nullptr,ETeleportType::TeleportPhysics);break; }
            Car->GetMesh()->SetPhysicsLinearVelocity(FVector::ZeroVector);Car->GetMesh()->SetPhysicsAngularVelocityInRadians(FVector::ZeroVector);Next(1);
        }
        else if(Stage==1 && Elapsed>2.) { Start=Raven->GetActorLocation();Key(PC,EKeys::W,true);Shot(TEXT("road.png"));Next(2); }
        else if(Stage==2 && Elapsed>6.)
        {
            Check(TEXT("road_drives"),FVector::Dist2D(Start,Raven->GetActorLocation())>300.f);Data->SetNumberField(TEXT("road_distance_cm"),FVector::Dist2D(Start,Raven->GetActorLocation()));
            Key(PC,EKeys::W,false);Raven->Modes->ServerToggleMode();Next(3);
        }
        else if(Stage==3 && Raven->Modes->GetMode()==EMaskVehicleMode::Flight)
        {
            auto* Car=Raven.Get();Check(TEXT("transforms_to_flight"),true);const FRotator Level(0,Car->GetActorRotation().Yaw,0);
            Car->SetActorLocationAndRotation(Car->GetActorLocation()+FVector(0,0,4000),Level,false,nullptr,ETeleportType::TeleportPhysics);Car->GetMesh()->SetPhysicsLinearVelocity(FVector::ZeroVector);Car->GetMesh()->SetPhysicsAngularVelocityInRadians(FVector::ZeroVector);
            Key(PC,EKeys::S,true);Start=Car->GetActorLocation();Next(4);
        }
        else if(Stage==4 && Elapsed>15.)
        {
            TArray<UStaticMeshComponent*> Visuals;Raven->GetComponents(Visuals);int32 Folded=0;
            for(const auto* Part:Visuals)
            {
                if(Part->GetFName()==TEXT("SM_RV_FrontWheelFold_L") || Part->GetFName()==TEXT("SM_RV_FrontWheelFold_R"))
                {
                    const FVector Center=Raven->GetMesh()->GetComponentTransform().InverseTransformPosition(Part->Bounds.Origin);
                    Data->SetStringField(*Part->GetName(),Center.ToString());Folded+=Center.Z>65.f && FMath::Abs(Center.Y)<100.f;
                }
            }
            Check(TEXT("front_wheels_fold_above_inverted_front"),Folded==2);
            const float Command=Raven->Dynamics->GetTargetAirspeedMPS(),Speed=Raven->GetVelocity().Size2D()*.01f;
            Check(TEXT("full_brake_command_keeps_minimum_airspeed"),Command>=Raven->Definition->Dynamics.MinimumAirspeedMPS-.1f);Check(TEXT("accelerates_from_rest_despite_full_air_brake"),Speed>8.f);Check(TEXT("flight_keeps_moving"),FVector::Dist2D(Start,Raven->GetActorLocation())>3000.f);
            Data->SetNumberField(TEXT("full_brake_speed_mps"),Speed);Data->SetNumberField(TEXT("full_brake_command_mps"),Command);Shot(TEXT("flight.png"));StartYaw=Raven->GetActorRotation().Yaw;Key(PC,EKeys::D,true);Next(5);
        }
        else if(Stage==5 && Elapsed>4.)
        {
            const float Turn=FMath::Abs(FMath::FindDeltaAngleDegrees(StartYaw,Raven->GetActorRotation().Yaw));Check(TEXT("aircraft_turns"),Turn>40.f);Data->SetNumberField(TEXT("turn_degrees"),Turn);Key(PC,EKeys::D,false);Key(PC,EKeys::S,false);Raven->Modes->ServerToggleMode();Next(6);
        }
        else if(Stage==6 && Raven->Modes->GetMode()==EMaskVehicleMode::Road) { Check(TEXT("lands_and_retracts_to_road"),true);Shot(TEXT("landed.png"));Next(7); }
        else if(Stage==7 && Elapsed>1.) { return Finish(); }
        return true;
    }
};
TUniquePtr<FRun> Run;
FAutoConsoleCommand Command(TEXT("MASK.RavenSmoke"),TEXT("Pinewoods four-vehicle fleet, Raven driving/fixed-wing minimum speed and landing."),FConsoleCommandDelegate::CreateLambda([](){if(!Run) { Run=MakeUnique<FRun>();FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda([](float D){return Run->Tick(D);})); }}));
}
#endif
