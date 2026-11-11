#if !UE_BUILD_SHIPPING
#include "Tests/DynamicsSmoke.h"
#include "MASK/ThunderhawkPawn.h"
#include "MASK/RhinoPawn.h"
#include "MASK/HurricanePawn.h"
#include "MASK/MaskVehicleDefinition.h"
#include "ChaosWheeledVehicleMovementComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Containers/Ticker.h"
#include "Dom/JsonObject.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "HAL/FileManager.h"
#include "HAL/IConsoleManager.h"
#include "InputKeyEventArgs.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonSerializer.h"

namespace HandlingSmoke
{
class FRun
{
    FString Directory;int32 VehicleIndex=0,Phase=0;float StageTime=0,LastYaw=0,Turn=0,Span=0,Wheelbase=0;
    double Started=FPlatformTime::Seconds();FVector Start;
    TWeakObjectPtr<ADynamicsTestFloor> Floor;TWeakObjectPtr<AThunderhawkPawn> Vehicle;TWeakObjectPtr<APawn> Original;
    TSharedRef<FJsonObject> Checks=MakeShared<FJsonObject>(),Telemetry=MakeShared<FJsonObject>();
    void Axis(APlayerController* PC,FKey Key,float Value)
    { PC->InputKey(FInputKeyEventArgs::CreateSimulated(Key,IE_Axis,Value,1,FInputDeviceId::CreateFromInternalId(0))); }
    void Check(const FString& Key,bool Value) { Checks->SetBoolField(Vehicle->Definition->VehicleName+TEXT("_")+Key,Value); }
    void Save(bool Complete)
    {
        bool Passed=Complete && Checks->Values.Num()==6;for(const auto& Pair:Checks->Values) { Passed&=Pair.Value->AsBool(); }
        auto Report=MakeShared<FJsonObject>();Report->SetBoolField(TEXT("passed"),Passed);Report->SetBoolField(TEXT("complete"),Complete);
        Report->SetNumberField(TEXT("elapsed_seconds"),FPlatformTime::Seconds()-Started);Report->SetNumberField(TEXT("phase"),Phase);
        Report->SetObjectField(TEXT("checks"),Checks);Report->SetObjectField(TEXT("telemetry"),Telemetry);
        Report->SetStringField(TEXT("fixture"),TEXT("Three existing playable Blueprint Chaos vehicles on an explicit 10-degree ramp for an 8-second full-throttle hill start, then a flat 10-second full-lock turn at approximately 3m/s. Placement/reset only between scenarios; injected gamepad axes during measurements. Not manual validation."));
        FString Json;FJsonSerializer::Serialize(Report,TJsonWriterFactory<>::Create(&Json));FFileHelper::SaveStringToFile(Json,*(Directory/TEXT("solo.json")));
    }
    void Place(AThunderhawkPawn* Car,FRotator Rotation)
    {
        Car->SetActorLocationAndRotation(FVector(0,0,20020),Rotation,false,nullptr,ETeleportType::TeleportPhysics);
        Car->GetMesh()->SetPhysicsLinearVelocity(FVector::ZeroVector);Car->GetMesh()->SetPhysicsAngularVelocityInRadians(FVector::ZeroVector);
    }
public:
    FRun()
    { FParse::Value(FCommandLine::Get(),TEXT("MigrationReportDir="),Directory);if(Directory.IsEmpty()) { Directory=FPaths::ProjectSavedDir()/TEXT("Migration/handling"); }IFileManager::Get().MakeDirectory(*Directory,true); }
    bool Tick(float)
    {
        if(FPlatformTime::Seconds()-Started>180) { Save(false);FPlatformMisc::RequestExit(false);return false; }
        UWorld* World=nullptr;for(const auto& C:GEngine->GetWorldContexts()) { if(C.WorldType==EWorldType::Game) { World=C.World();break; } }
        auto* PC=World?World->GetFirstPlayerController():nullptr;if(!PC || !PC->GetPawn() || World->GetTimeSeconds()<3) { return true; }
        if(Phase==0)
        {
            if(!Floor.IsValid()) { Floor=World->SpawnActor<ADynamicsTestFloor>(FVector(0,0,19950),FRotator::ZeroRotator); }
            Floor->SetActorRotation(FRotator(10,0,0));
            if(!Original.IsValid()) { Original=PC->GetPawn(); }
            const TCHAR* Names[]={TEXT("Thunderhawk"),TEXT("Rhino"),TEXT("Hurricane")};
            const FString Path=FString::Printf(TEXT("/Game/MASK/%s/BP_%s.BP_%s_C"),Names[VehicleIndex],Names[VehicleIndex],Names[VehicleIndex]);
            auto* Class=LoadClass<AThunderhawkPawn>(nullptr,*Path);
            Vehicle=Class?World->SpawnActor<AThunderhawkPawn>(Class,FVector(0,0,20020),FRotator(10,0,0)):nullptr;
            if(!Vehicle.IsValid()) { Save(false);FPlatformMisc::RequestExit(false);return false; }
            PC->Possess(Vehicle.Get());StageTime=World->GetTimeSeconds();Phase=1;
        }
        auto* Car=Vehicle.Get();auto* Move=CastChecked<UChaosWheeledVehicleMovementComponent>(Car->GetVehicleMovement());
        const float Age=World->GetTimeSeconds()-StageTime;
        Axis(PC,EKeys::Gamepad_LeftTriggerAxis,0);Axis(PC,EKeys::Gamepad_LeftX,0);
        Axis(PC,EKeys::Gamepad_RightTriggerAxis,Phase==2?1.f:0.f);
        if(Phase==1 && Age>2)
        { Start=Car->GetActorLocation();StageTime=World->GetTimeSeconds();Phase=2; }
        else if(Phase==2 && Age>8)
        {
            const FVector Travel=Car->GetActorLocation()-Start;
            Check(TEXT("starts_up_10_degree_hill"),Travel.X>500 && Travel.Z>80 && Move->GetForwardSpeed()>100);
            Telemetry->SetStringField(Car->Definition->VehicleName+TEXT("_hill_travel_cm"),Travel.ToString());
            Telemetry->SetNumberField(Car->Definition->VehicleName+TEXT("_hill_speed_kmh"),Move->GetForwardSpeed()*.036f);
            Telemetry->SetNumberField(Car->Definition->VehicleName+TEXT("_hill_throttle"),Move->GetThrottleInput());
            Telemetry->SetNumberField(Car->Definition->VehicleName+TEXT("_hill_rpm"),Move->GetEngineRotationSpeed());
            Telemetry->SetNumberField(Car->Definition->VehicleName+TEXT("_hill_gear"),Move->GetCurrentGear());
            Axis(PC,EKeys::Gamepad_RightTriggerAxis,0);Floor->SetActorRotation(FRotator::ZeroRotator);Place(Car,FRotator::ZeroRotator);
            float Front=-BIG_NUMBER,Rear=BIG_NUMBER;for(const auto& Wheel:Car->Definition->Wheels) { Front=FMath::Max(Front,static_cast<float>(Wheel.Center.X));Rear=FMath::Min(Rear,static_cast<float>(Wheel.Center.X)); }
            Wheelbase=Front>Rear?Front-Rear:300.f;StageTime=World->GetTimeSeconds();Phase=3;Save(false);
        }
        else if(Phase==3 && Age>2)
        { Start=Car->GetActorLocation();LastYaw=Car->GetActorRotation().Yaw;Turn=Span=0;StageTime=World->GetTimeSeconds();Phase=4; }
        else if(Phase==4)
        {
            Axis(PC,EKeys::Gamepad_LeftX,1);
            Axis(PC,EKeys::Gamepad_RightTriggerAxis,FMath::Clamp((300.f-Move->GetForwardSpeed())/400.f,0.f,.6f));
            Turn+=FMath::FindDeltaAngleDegrees(LastYaw,Car->GetActorRotation().Yaw);LastYaw=Car->GetActorRotation().Yaw;
            Span=FMath::Max(Span,static_cast<float>(FVector::Dist2D(Start,Car->GetActorLocation())));
            if(Age>10)
            {
                Check(TEXT("low_speed_half_turn_in_10_seconds"),Turn>150 && Span<3*Wheelbase+400);
                Telemetry->SetNumberField(Car->Definition->VehicleName+TEXT("_turn_degrees"),Turn);
                Telemetry->SetNumberField(Car->Definition->VehicleName+TEXT("_turn_span_m"),Span/100);
                Axis(PC,EKeys::Gamepad_RightTriggerAxis,0);Axis(PC,EKeys::Gamepad_LeftX,0);PC->Possess(Original.Get());Car->Destroy();
                if(++VehicleIndex==3) { Save(true);FPlatformMisc::RequestExit(false);return false; }Phase=0;Save(false);
            }
        }
        return true;
    }
};
TUniquePtr<FRun> Runner;
FAutoConsoleCommand Command(TEXT("MASK.HandlingSmoke"),TEXT("Three-vehicle hill starts and low-speed U-turn measurements."),FConsoleCommandDelegate::CreateLambda([]()
{ if(!Runner) { Runner=MakeUnique<FRun>();FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda([](float D){return Runner->Tick(D);})); } }));
}
#endif
