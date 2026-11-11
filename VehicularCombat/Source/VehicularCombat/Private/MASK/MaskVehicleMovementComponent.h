#pragma once
#include "CoreMinimal.h"
#include "ChaosWheeledVehicleMovementComponent.h"
#include "WheelSystem.h"
#include "SuspensionSystem.h"
#include "MaskVehicleMovementComponent.generated.h"

/** Runtime wheel setters must not mutate the class-default setups shared by other wheels/vehicles. */
UCLASS()
class UMaskVehicleMovementComponent : public UChaosWheeledVehicleMovementComponent
{
    GENERATED_BODY()
public:
    virtual void SetupVehicle(TUniquePtr<Chaos::FSimpleWheeledVehicle>& PVehicle) override;
private:
    // Allocated at physics creation, never resized while the simulation uses the pointers.
    TArray<Chaos::FSimpleWheelConfig> WheelConfigs;
    TArray<Chaos::FSimpleSuspensionConfig> SuspensionConfigs;
};
