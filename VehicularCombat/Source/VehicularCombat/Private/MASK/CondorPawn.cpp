#include "MASK/CondorPawn.h"
#include "MASK/MaskVehicleDefinition.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Components/SkeletalMeshComponent.h"
UCondorFrontWheel::UCondorFrontWheel()
{
    WheelRadius=35.3f;WheelWidth=13.4f;MaxSteerAngle=32.f;
    SpringRate=75.f;SpringPreload=25.f;SuspensionMaxRaise=5.f;SuspensionMaxDrop=8.f;
    MaxBrakeTorque=700.f;FrictionForceMultiplier=1.2f;
}
UCondorRearWheel::UCondorRearWheel()
{
    WheelRadius=35.3f;WheelWidth=13.4f;
    SpringRate=75.f;SpringPreload=25.f;SuspensionMaxRaise=5.f;SuspensionMaxDrop=8.f;
    MaxBrakeTorque=600.f;MaxHandBrakeTorque=900.f;FrictionForceMultiplier=1.2f;
}

void ACondorPawn::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if(!Definition || IsDriverOnFoot() || !Definition->DriverTransformationPose) { return; }
    const float Progress=VisualDeployment();
    if(!Matt->GetSingleNodeInstance() || Matt->GetSingleNodeInstance()->GetCurrentAsset()!=Definition->DriverTransformationPose)
    { Matt->PlayAnimation(Definition->DriverTransformationPose,false); }
    Matt->GetSingleNodeInstance()->SetPlaying(false);
    Matt->GetSingleNodeInstance()->SetPosition(Progress*Definition->DriverTransformationPose->GetPlayLength(),false);
    const auto& Samples=Definition->DriverTransformSamples;
    if(!Samples.IsEmpty())
    {
        const float Frame=Progress*(Samples.Num()-1);const int32 A=FMath::FloorToInt(Frame),B=FMath::Min(A+1,Samples.Num()-1);
        FTransform Pose;Pose.Blend(Samples[A],Samples[B],Frame-A);Matt->SetRelativeTransform(Pose);
    }
}
