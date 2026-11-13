#pragma once
#include "CoreMinimal.h"
#include "MASK/ThunderhawkPawn.h"
#include "SwitchbladePawn.generated.h"

/** V.E.N.O.M. native rotorcraft / airplane. No hidden road wheels or road mode. */
UCLASS()
class ASwitchbladePawn : public AThunderhawkPawn
{
    GENERATED_BODY()
public:
    ASwitchbladePawn(const FObjectInitializer& ObjectInitializer=FObjectInitializer::Get());
    virtual bool CanDriverExit(FString& Reason) const override;
protected:
    virtual const TCHAR* DefaultDefinitionPath() const override { return TEXT("/Game/MASK/Switchblade/DA_Switchblade.DA_Switchblade"); }
};
