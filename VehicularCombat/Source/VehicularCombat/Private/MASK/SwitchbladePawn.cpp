#include "MASK/SwitchbladePawn.h"
#include "MASK/MaskDynamicsComponent.h"
#include "MASK/MaskVehicleModeComponent.h"

ASwitchbladePawn::ASwitchbladePawn(const FObjectInitializer& Initializer):Super(Initializer) { FleetTeamId=2; }
bool ASwitchbladePawn::CanDriverExit(FString& Reason) const
{
    if(Modes->GetMode()!=EMaskVehicleMode::Road || Dynamics->GroundClearanceCM>40.f)
    { Reason=TEXT("Posez l'helicoptere avant de sortir");return false; }
    return Super::CanDriverExit(Reason);
}
