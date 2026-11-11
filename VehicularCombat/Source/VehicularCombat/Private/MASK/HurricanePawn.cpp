#include "MASK/HurricanePawn.h"
#include "MASK/MaskVehicleDefinition.h"
#include "MASK/MaskVehicleModeComponent.h"
#include "ChaosWheeledVehicleMovementComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/SpringArmComponent.h"
#include "Net/UnrealNetwork.h"

namespace
{
FTransform SampleHurricane(const TArray<FTransform>& Samples,float Progress)
{
    if(Samples.IsEmpty()) { return FTransform::Identity; }
    const float Frame=FMath::Clamp(Progress,0.f,1.f)*(Samples.Num()-1);
    const int32 A=FMath::FloorToInt(Frame),B=FMath::Min(A+1,Samples.Num()-1);
    FTransform Result;Result.Blend(Samples[A],Samples[B],Frame-A);return Result;
}
}
UHurricaneFrontWheel::UHurricaneFrontWheel()
{
    WheelRadius=38.f;WheelWidth=23.f;MaxSteerAngle=35.f;bAffectedBySteering=true;
    MaxBrakeTorque=4000.f;SuspensionMaxRaise=8.f;SuspensionMaxDrop=12.f;
    SpringRate=350.f;SpringPreload=60.f;SuspensionDampingRatio=.7f;FrictionForceMultiplier=1.15f;
}
UHurricaneRearWheel::UHurricaneRearWheel()
{
    WheelRadius=38.f;WheelWidth=23.f;MaxSteerAngle=0.f;bAffectedBySteering=false;
    bAffectedByEngine=true;bAffectedByHandbrake=true;MaxBrakeTorque=4000.f;MaxHandBrakeTorque=6000.f;
    SuspensionMaxRaise=8.f;SuspensionMaxDrop=12.f;SpringRate=350.f;SpringPreload=60.f;
    SuspensionDampingRatio=.7f;FrictionForceMultiplier=1.15f;
}
void AHurricanePawn::BeginPlay()
{
    Super::BeginPlay();
    ConfigureRoadWheels(false);
    if(HasAuthority() && Definition && Definition->SpareMesh)
    {
        SpareWheel=GetWorld()->SpawnActorDeferred<AHurricaneSpareWheel>(AHurricaneSpareWheel::StaticClass(),GetActorTransform(),this,nullptr,ESpawnActorCollisionHandlingMethod::AlwaysSpawn);
        SpareWheel->ParentVehicle=this;SpareWheel->FinishSpawning(GetActorTransform());ForceNetUpdate();
    }
}
void AHurricanePawn::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);DOREPLIFETIME(AHurricanePawn,SpareWheel);
}
void AHurricanePawn::EndPlay(const EEndPlayReason::Type Reason)
{
    if(HasAuthority() && SpareWheel && !SpareWheel->bEjected) { SpareWheel->Destroy(); }
    Super::EndPlay(Reason);
}
void AHurricanePawn::ConfigureRoadWheels(bool Six)
{
    if(!Definition) { return; }
    auto* Move=CastChecked<UChaosWheeledVehicleMovementComponent>(GetVehicleMovement());
    if(Move->Wheels.Num()<6 || (bWheelConfigurationReady && bCentreWheelsActive==Six)) { return; }
    // Rebuilding a six-wheel simulation as four wheels leaves queued async
    // output with six entries in UE 5.8. Keep topology stable while moving.
    for(int32 I=4;I<6;++I)
    {
        Move->SetAffectedByEngine(I,Six);Move->SetAffectedByBrake(I,Six);Move->SetAffectedByHandbrake(I,Six);
        Move->SetWheelRadius(I,Six?38.f:.1f);Move->SetWheelFrictionMultiplier(I,Six?1.15f:0.f);
        Move->SetSuspensionParams(Six?350.f:0.f,Six?.7f:0.f,Six?60.f:0.f,Six?8.f:0.f,Six?12.f:0.f,I);
    }
    bWheelConfigurationReady=true;bCentreWheelsActive=Six;GetMesh()->WakeAllRigidBodies();
    UE_LOG(LogTemp,Display,TEXT("MASK_HURRICANE active_wheels=%d stable_slots=6 authority=%d"),Six?6:4,HasAuthority());
}
const UChaosVehicleWheel* AHurricanePawn::AnimationWheel(FName Name) const
{
    if(!bCentreWheelsActive && (Name==TEXT("W4") || Name==TEXT("W5"))) { return nullptr; }
    return Super::AnimationWheel(Name);
}
void AHurricanePawn::Tick(float DeltaSeconds)
{
    ConfigureRoadWheels(Modes->GetMode()==EMaskVehicleMode::Combat);
    Super::Tick(DeltaSeconds);
    if(!Definition) { return; }
    const float Progress=Modes->GetDeployment();
    if(!IsDriverOnFoot() && Definition->DriverTransformationPose)
    {
        if(!Matt->GetSingleNodeInstance() || Matt->GetSingleNodeInstance()->GetCurrentAsset()!=Definition->DriverTransformationPose)
        { Matt->PlayAnimation(Definition->DriverTransformationPose,false); }
        Matt->GetSingleNodeInstance()->SetPlaying(false);
        Matt->GetSingleNodeInstance()->SetPosition(Progress*Definition->DriverTransformationPose->GetPlayLength(),false);
        Matt->SetRelativeTransform(SampleHurricane(Definition->DriverTransformSamples,Progress));
        TArray<USpringArmComponent*> Arms;GetComponents(Arms);
        const FVector Eye=Matt->GetSocketTransform(TEXT("head"),RTS_Actor).GetLocation()+FVector(18,0,8);
        for(auto* Arm:Arms)
        { if(Arm->GetFName()==TEXT("Inside Spring Arm")) { Arm->SetRelativeLocation(FMath::Lerp(Definition->CockpitLocation,Eye,Progress)); } }
    }
    // The rear saw remains the same assembly; spin around its authored axle.
    if(Progress>.99f)
    {
        TArray<UStaticMeshComponent*> Parts;GetComponents(Parts);
        for(auto* Part:Parts)
        {
            if(Part->GetFName()!=TEXT("SM_HU_RearSawSlide")) { continue; }
            const FVector Pivot(-210,0,26);const FQuat Rotation(FVector::UpVector,GetWorld()->GetTimeSeconds()*6.f);
            Part->SetRelativeTransform(FTransform(Rotation,Pivot-Rotation.RotateVector(Pivot))*Part->GetRelativeTransform());
        }
    }
}
bool AHurricanePawn::HandleVehicleWeaponModifier()
{
    const auto* PC=Cast<APlayerController>(GetController());
    if(PC && PC->IsInputKeyDown(EKeys::Gamepad_LeftShoulder)) { ServerLaunchSpare();return true; }
    return false;
}
void AHurricanePawn::ServerLaunchSpare_Implementation()
{
    if(Modes->GetMode()!=EMaskVehicleMode::Combat) { ClientVehicleSwitchFeedback(TEXT("Transformez Hurricane avant d'ejecter la roue"));return; }
    if(!SpareWheel || SpareWheel->bEjected) { ClientVehicleSwitchFeedback(TEXT("Roue de secours deja ejectee"));return; }
    SpareWheel->Launch();ClientVehicleSwitchFeedback(TEXT("Roue de secours ejectee"));
}

AHurricaneSpareWheel::AHurricaneSpareWheel()
{
    PrimaryActorTick.bCanEverTick=true;bReplicates=true;SetReplicateMovement(true);
    WheelMesh=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("SpareWheel"));SetRootComponent(WheelMesh);
    WheelMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);WheelMesh->SetIsReplicated(true);
}
void AHurricaneSpareWheel::BeginPlay()
{
    Super::BeginPlay();ApplyState();if(ParentVehicle) { AddTickPrerequisiteActor(ParentVehicle); }
}
void AHurricaneSpareWheel::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);DOREPLIFETIME(AHurricaneSpareWheel,ParentVehicle);DOREPLIFETIME(AHurricaneSpareWheel,bEjected);
}
void AHurricaneSpareWheel::ApplyState()
{
    if(!ParentVehicle || !ParentVehicle->Definition) { return; }
    WheelMesh->SetStaticMesh(ParentVehicle->Definition->SpareMesh);
    if(!bEjected)
    {
        WheelMesh->SetSimulatePhysics(false);WheelMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        AttachToActor(ParentVehicle,FAttachmentTransformRules::KeepRelativeTransform);
        SetActorRelativeTransform(SampleHurricane(ParentVehicle->Definition->SpareMountSamples,ParentVehicle->Modes->GetDeployment()));
    }
    else
    {
        DetachFromActor(FDetachmentTransformRules::KeepWorldTransform);
        WheelMesh->SetCollisionProfileName(TEXT("PhysicsActor"));WheelMesh->SetMassOverrideInKg(NAME_None,35.f,true);
        WheelMesh->SetSimulatePhysics(true);WheelMesh->SetEnableGravity(true);WheelMesh->WakeAllRigidBodies();
    }
}
void AHurricaneSpareWheel::Launch()
{
    if(!HasAuthority() || bEjected || !ParentVehicle) { return; }
    bEjected=true;ApplyState();
    WheelMesh->SetPhysicsLinearVelocity(ParentVehicle->GetVelocity()-ParentVehicle->GetActorForwardVector()*1250.f+FVector(0,0,400));
    ForceNetUpdate();UE_LOG(LogTemp,Display,TEXT("MASK_HURRICANE same_spare_ejected=%s"),*GetName());
}
void AHurricaneSpareWheel::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if(!bEjected && ParentVehicle && ParentVehicle->Definition)
    { SetActorRelativeTransform(SampleHurricane(ParentVehicle->Definition->SpareMountSamples,ParentVehicle->Modes->GetDeployment())); }
}
