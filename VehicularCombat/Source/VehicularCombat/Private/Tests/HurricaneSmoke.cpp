#include "CoreMinimal.h"
#if !UE_BUILD_SHIPPING
#include "Tests/DynamicsSmoke.h"
#include "MASK/HurricanePawn.h"
#include "MASK/MaskVehicleDefinition.h"
#include "MASK/MaskVehicleModeComponent.h"
#include "AI/VehicleBotController.h"
#include "Core/CustomGameMode.h"
#include "Actors/ProjectileActor.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/SpringArmComponent.h"
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

namespace HurricaneSmoke
{
class FRun
{
    FString Directory;int32 Phase=0,Frames=0,DriveFrames=0,Projectiles=0;
    double Started=FPlatformTime::Seconds(),PhaseStarted=Started;
    TSharedRef<FJsonObject> Checks=MakeShared<FJsonObject>();
    TMap<FKey,float> Analog;TWeakObjectPtr<AHurricanePawn> Hurricane;
    TWeakObjectPtr<AHurricaneSpareWheel> Spare;TWeakObjectPtr<USkeletalMeshComponent> Hondo;
    TWeakObjectPtr<AVehicleBotController> Bot;FVector DriveStart,SpareStart;FVector LaunchForward;
    void Check(const TCHAR* Key,bool Value) { Checks->SetBoolField(Key,Value); }
    void Stage(int32 Value) { Phase=Value;Frames=0;PhaseStarted=FPlatformTime::Seconds();UE_LOG(LogTemp,Display,TEXT("MASK_HURRICANE_TEST phase=%d"),Phase); }
    void Key(APlayerController* PC,FKey Value,bool Down) { PC->InputKey(FInputKeyEventArgs::CreateSimulated(Value,Down?IE_Pressed:IE_Released,Down?1.f:0.f,-1,FInputDeviceId::CreateFromInternalId(0))); }
    void Button(APlayerController* PC,FKey Value) { Key(PC,Value,true);Key(PC,Value,false); }
    void Shot(const TCHAR* Name) { if(!FParse::Param(FCommandLine::Get(),TEXT("NullRHI"))) { FScreenshotRequest::RequestScreenshot(Directory/Name,true,false); } }
    void Save(bool Complete)
    {
        bool Passed=Complete;for(const auto& Pair:Checks->Values) { Passed&=Pair.Value->AsBool(); }
        auto R=MakeShared<FJsonObject>();R->SetBoolField(TEXT("passed"),Passed);R->SetBoolField(TEXT("complete"),Complete);R->SetObjectField(TEXT("checks"),Checks);
        R->SetNumberField(TEXT("phase"),Phase);R->SetNumberField(TEXT("elapsed_seconds"),FPlatformTime::Seconds()-Started);R->SetNumberField(TEXT("drive_frames"),DriveFrames);R->SetNumberField(TEXT("projectiles"),Projectiles);
        R->SetStringField(TEXT("input_method"),TEXT("Real game with injected Xbox keys/axes; no physical controller test claimed."));
        FString Json;FJsonSerializer::Serialize(R,TJsonWriterFactory<>::Create(&Json));FFileHelper::SaveStringToFile(Json,*(Directory/TEXT("hurricane.json")));
    }
    bool Finish(bool Timeout=false) { Check(TEXT("no_timeout"),!Timeout);Save(true);FPlatformMisc::RequestExit(false);return false; }
public:
    FRun()
    {
        FParse::Value(FCommandLine::Get(),TEXT("MigrationReportDir="),Directory);if(Directory.IsEmpty()) { Directory=FPaths::ProjectSavedDir()/TEXT("Art/hurricane-smoke"); }
        IFileManager::Get().MakeDirectory(*Directory,true);
    }
    bool Tick(float)
    {
        if(FPlatformTime::Seconds()-Started>120.) { return Finish(true); }
        UWorld* World=nullptr;for(const auto& Context:GEngine->GetWorldContexts()) { if(Context.WorldType==EWorldType::Game) { World=Context.World();break; } }
        if(!World) { return true; }auto* PC=World->GetFirstPlayerController();auto* Car=PC?Cast<AThunderhawkPawn>(PC->GetPawn()):nullptr;if(!Car) { return true; }
        const double Age=FPlatformTime::Seconds()-PhaseStarted;++Frames;
        if(Hurricane.IsValid()) { for(TActorIterator<AProjectileActor> It(World);It;++It) { if(It->GetOwner()==Hurricane.Get()) { ++Projectiles;break; } } }
        if(Phase==0 && World->GetTimeSeconds()>5.)
        {
            Hurricane=Cast<AHurricanePawn>(Car);if(!Hurricane.IsValid()) { Check(TEXT("hurricane_spawned"),false);return Finish(); }
            Hondo=Car->Matt;Spare=Hurricane->SpareWheel;auto* Move=CastChecked<UChaosWheeledVehicleMovementComponent>(Car->GetVehicleMovement());
            Check(TEXT("hondo_with_blaster_mask"),Car->IsMaskVisible() && Car->Spectrum->GetSkeletalMeshAsset() && Car->Definition->DriverName==TEXT("Hondo MacLean"));
            bool MaterialsAssigned=true;
            for(auto* CrewMesh:{Car->Matt.Get(),Car->Spectrum.Get()})
            { for(int32 I=0;I<CrewMesh->GetNumMaterials();++I) { MaterialsAssigned&=CrewMesh->GetMaterial(I)!=nullptr; } }
            Check(TEXT("hondo_and_mask_atlas_materials_assigned"),MaterialsAssigned);
            Check(TEXT("four_road_supports_middle_pair_inactive"),Move->Wheels.Num()==6 && !Move->GetWheelState(4).bInContact && !Move->GetWheelState(5).bInContact);Check(TEXT("six_persistent_tire_parts"),Car->Definition->Wheels.Num()==6);
            Check(TEXT("no_flight_or_jump"),!Car->Definition->bSupportsFlight && !Car->CanVehicleJump());Check(TEXT("no_proxy_depth_blocks"),!Car->GetMesh()->bRenderInDepthPass);
            Check(TEXT("transform_twice_as_fast"),FMath::IsNearlyEqual(Car->Modes->Duration,2.5f));Check(TEXT("one_spare_initially_mounted"),Spare.IsValid() && Spare->GetAttachParentActor()==Car);
            Shot(TEXT("road.png"));DriveStart=Car->GetActorLocation();Analog.Add(EKeys::Gamepad_RightTriggerAxis,1.f);Stage(1);
        }
        else if(Phase==1)
        {
            if(Frames>=60) { DriveFrames=Frames;Check(TEXT("xbox_road_driving"),FVector::Dist2D(DriveStart,Car->GetActorLocation())>100.f);Button(PC,EKeys::Gamepad_FaceButton_Left);Stage(3); }
        }
        else if(Phase==3 && Car->Modes->GetMode()==EMaskVehicleMode::Combat)
        {
            auto* Move=CastChecked<UChaosWheeledVehicleMovementComponent>(Car->GetVehicleMovement());
            if(Move->Wheels.Num()!=6 || !Move->GetWheelState(4).bInContact || !Move->GetWheelState(5).bInContact) { return true; }
            Check(TEXT("six_chaos_wheels_in_combat"),true);Check(TEXT("same_hondo_gunner_masked"),Hondo.Get()==Car->Matt && Car->Matt->GetRelativeLocation().Z>140.f && Car->IsMaskVisible());
            Check(TEXT("moving_transformation_preserves_driving"),Car->GetVelocity().Size2D()>200.f);
            Analog.Add(EKeys::Gamepad_RightTriggerAxis,0);Key(PC,EKeys::Gamepad_LeftShoulder,true);
            Check(TEXT("still_ground_physics"),Move->bMechanicalSimEnabled && Move->bSuspensionEnabled && !Car->Definition->bSupportsFlight);
            TArray<USpringArmComponent*> Arms;Car->GetComponents(Arms);
            for(auto* Arm:Arms) { if(Arm->GetFName()==TEXT("Outside Spring Arm")) { Arm->bUsePawnControlRotation=true; } }
            PC->SetControlRotation(FRotator(-12,Car->GetActorRotation().Yaw+45,0));
            for(auto* CrewMesh:{Car->Matt.Get(),Car->Spectrum.Get()})
            {
                auto* Material=CrewMesh->GetMaterial(0);UTexture* Texture=nullptr;
                if(Material) { Material->GetTextureParameterValue(FMaterialParameterInfo(TEXT("Atlas")),Texture); }
                UE_LOG(LogTemp,Display,TEXT("MASK_HURRICANE material=%s atlas=%s"),*GetNameSafe(Material),*GetNameSafe(Texture));
            }
            Key(PC,EKeys::Gamepad_RightShoulder,true);Stage(4);
        }
        else if(Phase==4 && Age>1.5)
        {
            Shot(TEXT("combat.png"));
            Key(PC,EKeys::Gamepad_RightShoulder,false);Check(TEXT("weapon_projectiles"),Projectiles>0);
            SpareStart=Spare->GetActorLocation();LaunchForward=Car->GetActorForwardVector();Button(PC,EKeys::Gamepad_FaceButton_Top);Stage(5);
        }
        else if(Phase==5 && Age>1.5)
        {
            Check(TEXT("lb_y_ejects_same_spare_actor"),Hurricane->SpareWheel==Spare.Get() && Spare->bEjected && !Spare->GetAttachParentActor() && Spare->WheelMesh->IsSimulatingPhysics());
            Check(TEXT("spare_projects_rearward"),FVector::DotProduct(Spare->GetActorLocation()-SpareStart,LaunchForward)<-100.f);
            int32 Count=0;for(TActorIterator<AHurricaneSpareWheel> It(World);It;++It) { ++Count; }Check(TEXT("no_duplicate_spare"),Count==1);
            Shot(TEXT("spare-ejected.png"));Button(PC,EKeys::Gamepad_FaceButton_Left);Stage(6);
        }
        else if(Phase==6 && Car->Modes->GetMode()==EMaskVehicleMode::Road)
        {
            auto* Move=CastChecked<UChaosWheeledVehicleMovementComponent>(Car->GetVehicleMovement());
            if(Move->GetWheelState(4).bInContact || Move->GetWheelState(5).bInContact) { return true; }
            Check(TEXT("returns_to_four_supports_without_rebuilding_wheel_arrays"),Move->Wheels.Num()==6);
            Check(TEXT("same_hondo_driving_again"),Hondo.Get()==Car->Matt && Car->Matt->GetRelativeLocation().Z<40.f);Key(PC,EKeys::Gamepad_LeftShoulder,false);
            auto* AI=World->SpawnActor<AVehicleBotController>();Bot=AI;AI->TrainingIndex=2;CastChecked<ACustomGameMode>(World->GetAuthGameMode())->RestartPlayer(AI);Stage(7);
        }
        else if(Phase==7 && Age>1.) { Button(PC,EKeys::Gamepad_DPad_Up);Stage(8); }
        else if(Phase==8 && Age>.7)
        {
            Check(TEXT("dpad_up_switches_away_ai_takes_hurricane"),Car!=Hurricane.Get() && Bot->GetPawn()==Hurricane.Get());Button(PC,EKeys::Gamepad_DPad_Down);Stage(9);
        }
        else if(Phase==9 && Age>.7)
        {
            Check(TEXT("dpad_down_returns_same_masked_hondo"),Car==Hurricane.Get() && Car->Matt==Hondo.Get() && Car->IsMaskVisible());
            Button(PC,EKeys::Gamepad_Special_Right);Stage(10);
        }
        else if(Phase==10 && Age>.5) { Check(TEXT("pause_contains_controls"),Car->IsPauseMenuOpen());Shot(TEXT("pause-controls.png"));Stage(11); }
        else if(Phase==11 && Age>.5) { return Finish(); }
        for(const auto& Axis:Analog) { PC->InputKey(FInputKeyEventArgs::CreateSimulated(Axis.Key,IE_Axis,Axis.Value,1,FInputDeviceId::CreateFromInternalId(0))); }
        Save(false);return true;
    }
};
TUniquePtr<FRun> Runner;
FAutoConsoleCommand Command(TEXT("MASK.HurricaneSmoke"),TEXT("Opt-in Hurricane, masked Hondo, six wheels and spare ejection validation."),FConsoleCommandDelegate::CreateLambda([]()
{ if(Runner) { return; }Runner=MakeUnique<FRun>();FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda([](float Delta){return Runner->Tick(Delta);})); }));
}

namespace HurricaneWheelProbe
{
class FRun
{
    FString Directory;double Started=FPlatformTime::Seconds(),Ready=-1.;
    TArray<TSharedPtr<FJsonValue>> Samples;
    float OffsetMin[2][2]={{MAX_flt,MAX_flt},{MAX_flt,MAX_flt}},OffsetMax[2][2]={{-MAX_flt,-MAX_flt},{-MAX_flt,-MAX_flt}};
    float StepMax[2]={0,0},RotationStepMax[2]={0,0},PreviousOffset[2]={0,0},PreviousAngle[2]={0,0};
    bool PreviousRest=false;
    TWeakObjectPtr<AHurricanePawn> Other;bool IndependentModes=false,OtherRecalled=false;
    int32 DrivingSamples=0,DrivingRearContactMisses=0;
public:
    FRun() { FParse::Value(FCommandLine::Get(),TEXT("MigrationReportDir="),Directory);IFileManager::Get().MakeDirectory(*Directory,true); }
    bool Tick(float)
    {
        if(FPlatformTime::Seconds()-Started>90.) { FPlatformMisc::RequestExit(false);return false; }
        UWorld* World=nullptr;for(const auto& C:GEngine->GetWorldContexts()) { if(C.WorldType==EWorldType::Game) { World=C.World();break; } }
        if(!World) { return true; }auto* PC=World->GetFirstPlayerController();auto* Car=PC?Cast<AHurricanePawn>(PC->GetPawn()):nullptr;if(!Car || !Car->Definition) { return true; }
        if(Ready<0)
        {
            if(World->GetTimeSeconds()<3.f) { return true; }
            World->SpawnActor<ADynamicsTestFloor>(FVector(0,0,19950),FRotator::ZeroRotator);
            Car->SetActorLocationAndRotation(FVector(0,0,20015),FRotator::ZeroRotator,false,nullptr,ETeleportType::TeleportPhysics);
            Car->GetMesh()->SetPhysicsLinearVelocity(FVector::ZeroVector);Car->GetMesh()->SetPhysicsAngularVelocityInRadians(FVector::ZeroVector);
            Other=World->SpawnActor<AHurricanePawn>(Car->GetClass(),FVector(0,2000,20015),FRotator::ZeroRotator);
            if(Other.IsValid()) { Other->Modes->ServerToggleMode(); }
            Ready=FPlatformTime::Seconds();
        }
        const double Age=FPlatformTime::Seconds()-Ready;const bool Driving=Age>=7. && Age<11.,Braking=Age>=11. && Age<14.;
        const int32 Window=Age>=14.?1:0;const bool Rest=(Age>=3. && Age<7.) || Age>=16.;
        PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::Gamepad_RightTriggerAxis,IE_Axis,Driving?1.f:0.f,1,FInputDeviceId::CreateFromInternalId(0)));
        PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::Gamepad_LeftShoulder,Braking?IE_Pressed:IE_Released,Braking?1.f:0.f,-1,FInputDeviceId::CreateFromInternalId(0)));
        auto* Move=CastChecked<UChaosWheeledVehicleMovementComponent>(Car->GetVehicleMovement());
        if(Other.IsValid() && Age>5. && Age<7.)
        {
            const auto* OtherMove=CastChecked<UChaosWheeledVehicleMovementComponent>(Other->GetVehicleMovement());
            IndependentModes=Other->Modes->GetMode()==EMaskVehicleMode::Combat && OtherMove->GetWheelState(4).bInContact && !Move->GetWheelState(4).bInContact;
        }
        if(Other.IsValid() && Age>8. && !OtherRecalled) { Other->Modes->ServerToggleMode();OtherRecalled=true; }
        if(Age>8. && Driving) { ++DrivingSamples;DrivingRearContactMisses+=(!Move->GetWheelState(2).bInContact || !Move->GetWheelState(3).bInContact)?1:0; }
        auto Sample=MakeShared<FJsonObject>();Sample->SetNumberField(TEXT("seconds"),Age);Sample->SetNumberField(TEXT("speed_cmps"),Car->GetVelocity().Size());Sample->SetNumberField(TEXT("chassis_z"),Car->GetActorLocation().Z);
        for(int32 I=0;I<6 && I<Move->Wheels.Num();++I)
        {
            const auto* Wheel=Move->Wheels[I].Get();const float Offset=Wheel->GetSuspensionOffset(),Angle=Wheel->GetRotationAngle();
            Sample->SetNumberField(FString::Printf(TEXT("w%d_offset_cm"),I),Offset);Sample->SetNumberField(FString::Printf(TEXT("w%d_angle"),I),Angle);
            Sample->SetBoolField(FString::Printf(TEXT("w%d_contact"),I),Move->GetWheelState(I).bInContact);
            if(I==2 || I==3)
            {
                const int32 R=I-2;
                if(Rest)
                {
                    OffsetMin[Window][R]=FMath::Min(OffsetMin[Window][R],Offset);OffsetMax[Window][R]=FMath::Max(OffsetMax[Window][R],Offset);
                    if(PreviousRest) { StepMax[R]=FMath::Max(StepMax[R],FMath::Abs(Offset-PreviousOffset[R]));RotationStepMax[R]=FMath::Max(RotationStepMax[R],FMath::Abs(FMath::FindDeltaAngleDegrees(PreviousAngle[R],Angle))); }
                }
                PreviousOffset[R]=Offset;PreviousAngle[R]=Angle;
            }
        }
        PreviousRest=Rest;Samples.Add(MakeShared<FJsonValueObject>(Sample));
        if(Age<20.) { return true; }
        auto Report=MakeShared<FJsonObject>();auto Checks=MakeShared<FJsonObject>();auto Metrics=MakeShared<FJsonObject>();bool Passed=true;
        Checks->SetBoolField(TEXT("two_hurricanes_keep_independent_wheel_modes"),IndependentModes);Passed&=IndependentModes;
        const bool RoadContact=DrivingSamples>30 && DrivingRearContactMisses<DrivingSamples*.05f;
        Checks->SetBoolField(TEXT("rear_contacts_stable_while_driving_on_flat_ground"),RoadContact);Passed&=RoadContact;
        Metrics->SetNumberField(TEXT("driving_frames"),DrivingSamples);Metrics->SetNumberField(TEXT("driving_rear_contact_misses"),DrivingRearContactMisses);
        for(int32 W=0;W<2;++W)
        {
            for(int32 WindowIndex=0;WindowIndex<2;++WindowIndex)
            {
                const float Range=OffsetMax[WindowIndex][W]-OffsetMin[WindowIndex][W];
                Metrics->SetNumberField(FString::Printf(TEXT("rear%d_rest%d_range_cm"),W,WindowIndex),Range);
                const bool Stable=Range>=0.f && Range<1.f;Checks->SetBoolField(FString::Printf(TEXT("rear%d_rest%d_stable"),W,WindowIndex),Stable);Passed&=Stable;
            }
            Metrics->SetNumberField(FString::Printf(TEXT("rear%d_max_rest_offset_step_cm"),W),StepMax[W]);
            Metrics->SetNumberField(FString::Printf(TEXT("rear%d_max_rest_rotation_step_degrees"),W),RotationStepMax[W]);
        }
        Report->SetBoolField(TEXT("passed"),Passed);Report->SetBoolField(TEXT("complete"),true);Report->SetObjectField(TEXT("checks"),Checks);Report->SetObjectField(TEXT("metrics"),Metrics);
        Report->SetStringField(TEXT("fixture"),TEXT("Flat temporary floor; tested car stays in road mode. Rest, four seconds RT, three seconds handbrake, rest. A second Hurricane deploys/retracts separately. Physics wheel offsets sampled every rendered frame."));
        FString Json;FJsonSerializer::Serialize(Report,TJsonWriterFactory<>::Create(&Json));FFileHelper::SaveStringToFile(Json,*(Directory/TEXT("hurricane.json")));
        Report->SetArrayField(TEXT("samples"),Samples);Json.Reset();FJsonSerializer::Serialize(Report,TJsonWriterFactory<>::Create(&Json));FFileHelper::SaveStringToFile(Json,*(Directory/TEXT("wheel-samples.json")));
        FPlatformMisc::RequestExit(false);return false;
    }
};
TUniquePtr<FRun> Runner;
FAutoConsoleCommand Command(TEXT("MASK.HurricaneWheelProbe"),TEXT("Opt-in road suspension stability measurement."),FConsoleCommandDelegate::CreateLambda([]()
{ if(Runner) { return; }Runner=MakeUnique<FRun>();FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda([](float Delta){return Runner->Tick(Delta);})); }));
}
#endif
