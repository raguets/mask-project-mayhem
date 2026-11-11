#include "MASK/MaskDriverAnimInstance.h"
#include "MASK/MaskDriverCharacter.h"
#include "MASK/MaskVehicleDefinition.h"
#include "Animation/AnimInstanceProxy.h"
#include "Animation/AnimNode_SequencePlayer.h"
#include "AnimNodes/AnimNode_BlendSpacePlayer.h"
#include "AnimNodes/AnimNode_TwoWayBlend.h"
#include "GameFramework/CharacterMovementComponent.h"

struct FMaskDriverAnimProxy final : FAnimInstanceProxy
{
    FAnimNode_BlendSpacePlayer_Standalone Locomotion;
    FAnimNode_SequencePlayer_Standalone Jump;
    FAnimNode_TwoWayBlend Root;
    bool bWasFalling=false;
    explicit FMaskDriverAnimProxy(UAnimInstance* Instance):FAnimInstanceProxy(Instance)
    { Root.A.SetLinkNode(&Locomotion);Root.B.SetLinkNode(&Jump);Locomotion.SetLoop(true);Jump.SetLoopAnimation(false); }
    virtual FAnimNode_Base* GetCustomRootNode() override { return &Root; }
    virtual void PreUpdate(UAnimInstance* Instance,float DeltaSeconds) override
    {
        FAnimInstanceProxy::PreUpdate(Instance,DeltaSeconds);
        const auto* Driver=Cast<AMaskDriverCharacter>(Instance->GetOwningActor());if(!Driver || !Driver->Definition) { return; }
        Locomotion.SetBlendSpace(Driver->Definition->DriverLocomotion);
        const FVector Velocity=Driver->GetActorQuat().UnrotateVector(Driver->GetVelocity());Locomotion.SetPosition(FVector(Velocity.X,Velocity.Y,0));
        Jump.SetSequence(Driver->Definition->DriverJump);
        const bool Falling=Driver->GetCharacterMovement()->IsFalling();
        if(Falling && !bWasFalling) { Jump.SetAccumulatedTime(0.f); }
        Root.Alpha=FMath::FInterpConstantTo(Root.Alpha,Falling?1.f:0.f,DeltaSeconds,8.f);bWasFalling=Falling;
    }
};
FAnimInstanceProxy* UMaskDriverAnimInstance::CreateAnimInstanceProxy() { return new FMaskDriverAnimProxy(this); }
void UMaskDriverAnimInstance::DestroyAnimInstanceProxy(FAnimInstanceProxy* Proxy) { delete Proxy; }
