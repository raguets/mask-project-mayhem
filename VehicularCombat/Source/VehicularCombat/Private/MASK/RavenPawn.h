#pragma once

#include "MASK/ThunderhawkPawn.h"
#include "RavenPawn.generated.h"

UCLASS()
class URavenFrontWheel : public UThunderhawkFrontWheel
{
    GENERATED_BODY()
public: URavenFrontWheel();
};

UCLASS()
class URavenRearWheel : public UThunderhawkRearWheel
{
    GENERATED_BODY()
public: URavenRearWheel();
};

/** Raven shares Thunderhawk's road/assisted fixed-wing physics and replicated controls. */
UCLASS()
class ARavenPawn : public AThunderhawkPawn
{
    GENERATED_BODY()
protected:
    virtual const UChaosVehicleWheel* AnimationWheel(FName Name) const override;
    virtual const TCHAR* DefaultDefinitionPath() const override { return TEXT("/Game/MASK/Raven/DA_Raven.DA_Raven"); }
};
