#pragma once
#include "CoreMinimal.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "MaskDriverMovementComponent.generated.h"

/** Keep the existing CharacterMovement prediction and landing events. */
UCLASS()
class UMaskDriverMovementComponent : public UCharacterMovementComponent
{
    GENERATED_BODY()
protected:
    virtual void PhysFalling(float DeltaTime,int32 Iterations) override;
};
