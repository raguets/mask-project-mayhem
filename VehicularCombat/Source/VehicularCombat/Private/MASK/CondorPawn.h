#pragma once
#include "CoreMinimal.h"
#include "MASK/ThunderhawkPawn.h"
#include "CondorPawn.generated.h"

UCLASS()
class UCondorFrontWheel : public UThunderhawkFrontWheel
{
    GENERATED_BODY()
public: UCondorFrontWheel();
};
UCLASS()
class UCondorRearWheel : public UThunderhawkRearWheel
{
    GENERATED_BODY()
public: UCondorRearWheel();
};
/** Two persistent road tires, then assisted rotorcraft flight with stationary hover. */
UCLASS()
class ACondorPawn : public AThunderhawkPawn
{
    GENERATED_BODY()
public:
    virtual void Tick(float DeltaSeconds) override;
protected:
    virtual const TCHAR* DefaultDefinitionPath() const override { return TEXT("/Game/MASK/Condor/DA_Condor.DA_Condor"); }
};
