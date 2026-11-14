#pragma once
#include "MASK/ThunderhawkPawn.h"
#include "MantaPawn.generated.h"

UCLASS()
class UMantaFrontWheel : public UThunderhawkFrontWheel
{
    GENERATED_BODY()
public: UMantaFrontWheel();
};
UCLASS()
class UMantaRearWheel : public UThunderhawkRearWheel
{
    GENERATED_BODY()
public: UMantaRearWheel();
};

/** VENOM road / fixed-wing vehicle using the common Thunderhawk dynamics. */
UCLASS()
class AMantaPawn : public AThunderhawkPawn
{
    GENERATED_BODY()
public:
    AMantaPawn(const FObjectInitializer& Initializer=FObjectInitializer::Get());
    virtual void Tick(float DeltaSeconds) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
protected:
    virtual const UChaosVehicleWheel* AnimationWheel(FName Name) const override;
    virtual const TCHAR* DefaultDefinitionPath() const override { return TEXT("/Game/MASK/Manta/DA_Manta.DA_Manta"); }
private:
    TArray<TWeakObjectPtr<class USkeletalMeshComponent>> IntegratedWeaponMeshes;
};
