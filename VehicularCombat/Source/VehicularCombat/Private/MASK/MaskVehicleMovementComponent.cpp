#include "MASK/MaskVehicleMovementComponent.h"

void UMaskVehicleMovementComponent::SetupVehicle(TUniquePtr<Chaos::FSimpleWheeledVehicle>& PVehicle)
{
    Super::SetupVehicle(PVehicle);
    if(!PVehicle) { return; }
    // UE 5.8 constructs simulations with pointers into UChaosVehicleWheel CDOs.
    // SetSuspensionParams/SetAffectedByEngine then write through those pointers.
    // Own both configurations per wheel before any runtime mode changes occur.
    WheelConfigs.SetNum(PVehicle->Wheels.Num());
    SuspensionConfigs.SetNum(PVehicle->Suspension.Num());
    for(int32 I=0;I<WheelConfigs.Num();++I)
    {
        WheelConfigs[I]=PVehicle->Wheels[I].Setup();
        if(WheelConfigs[I].SteeringEnabled)
        {
            WheelConfigs[I].MaxSteeringAngle=45;
            PVehicle->Wheels[I].MaxSteeringAngle=45.f;
        }
        PVehicle->Wheels[I].SetupPtr=&WheelConfigs[I];
        SuspensionConfigs[I]=PVehicle->Suspension[I].Setup();
        PVehicle->Suspension[I].SetupPtr=&SuspensionConfigs[I];
    }
    // Recalculate sprung masses/damping now that each suspension owns its setup.
    SetupSuspension(PVehicle);
}
