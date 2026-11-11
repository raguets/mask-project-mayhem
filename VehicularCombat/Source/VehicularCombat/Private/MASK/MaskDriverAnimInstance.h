#pragma once
#include "CoreMinimal.h"
#include "Animation/AnimInstance.h"
#include "MaskDriverAnimInstance.generated.h"

/** Threaded locomotion graph: directional blend space and a smoothly blended jump. */
UCLASS(Transient)
class UMaskDriverAnimInstance : public UAnimInstance
{
    GENERATED_BODY()
protected:
    virtual FAnimInstanceProxy* CreateAnimInstanceProxy() override;
    virtual void DestroyAnimInstanceProxy(FAnimInstanceProxy* Proxy) override;
};
