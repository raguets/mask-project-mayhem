#include "MASK/RavenPawn.h"
#include "MASK/MaskVehicleModeComponent.h"

URavenFrontWheel::URavenFrontWheel() { WheelRadius=33.5f;WheelWidth=22.f; }
URavenRearWheel::URavenRearWheel() { WheelRadius=33.5f;WheelWidth=22.f; }

const UChaosVehicleWheel* ARavenPawn::AnimationWheel(FName Name) const
{
    // The sampled source tracks already rotate/fold the complete wheel units.
    // A road spin/suspension transform around their old centres would displace
    // the folded wheels. Resume the normal Chaos animation once fully on road.
    return Modes && Modes->GetDeployment()>UE_SMALL_NUMBER ? nullptr : Super::AnimationWheel(Name);
}
