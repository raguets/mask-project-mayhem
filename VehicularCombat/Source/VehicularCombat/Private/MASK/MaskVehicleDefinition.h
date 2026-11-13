#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "MaskVehicleDefinition.generated.h"

class UStaticMesh;
class USkeletalMesh;
class UAnimSequence;
class UChaosVehicleWheel;

UENUM(BlueprintType)
enum class EMaskFlightModel : uint8 { FixedWing, Rotorcraft };

/** SI tuning for assisted flight. Values are gameplay estimates, not aircraft specifications. */
USTRUCT(BlueprintType)
struct FMaskDynamicsSettings
{
	GENERATED_BODY()
	UPROPERTY(EditAnywhere) EMaskFlightModel FlightModel = EMaskFlightModel::FixedWing;
	UPROPERTY(EditAnywhere, meta=(ClampMin="1")) float MinimumAirspeedMPS = 50.f / 3.6f;
	UPROPERTY(EditAnywhere, meta=(ClampMin="5")) float MaximumAirspeedMPS = 300.f / 3.6f;
	UPROPERTY(EditAnywhere, meta=(ClampMin="0")) float RotorcraftMaximumAirspeedMPS = 30.f;
	UPROPERTY(EditAnywhere) float SpeedCommandRateMPS2 = 8.f;
	UPROPERTY(EditAnywhere) float FlightPowerKW = 600.f;
	UPROPERTY(EditAnywhere) float MaximumThrustN = 10000.f;
	UPROPERTY(EditAnywhere) float AirDragAreaM2 = 1.2f;
	UPROPERTY(EditAnywhere) float MaximumBankDegrees = 42.f;
	/** Force-based arcade turn assistance; gameplay estimates, not aircraft performance. */
	UPROPERTY(EditAnywhere, meta=(ClampMin="1",ClampMax="90")) float LowSpeedTurnRateDegrees = 55.f;
	UPROPERTY(EditAnywhere, meta=(ClampMin="1",ClampMax="90")) float HighSpeedTurnRateDegrees = 30.f;
	UPROPERTY(EditAnywhere) float MaximumPitchDegrees = 22.f;
	UPROPERTY(EditAnywhere) float AutomaticTakeoffHeightM = 2.f;
	UPROPERTY(EditAnywhere) float LandingDescentMPS = 8.f;
	UPROPERTY(EditAnywhere) float RotorcraftClimbMPS = 7.f;
	/** Zero selects a mass-dependent estimate; Chaos still supplies gears, tires and brakes. */
	UPROPERTY(EditAnywhere) float RoadPowerKW = 0.f;
	UPROPERTY(EditAnywhere) float RoadDragAreaM2 = 0.f;
	UPROPERTY(EditAnywhere) float RollingResistance = .015f;
	/** Assisted balance for a motorcycle's two actual contact wheels; no hidden extra tires. */
	UPROPERTY(EditAnywhere) bool bTwoWheelRoadBalance = false;
};

USTRUCT(BlueprintType)
struct FMaskWheelDefinition
{
	GENERATED_BODY()
	UPROPERTY(EditAnywhere) FName Name;
	UPROPERTY(EditAnywhere) FVector Center = FVector::ZeroVector;
	UPROPERTY(EditAnywhere) TSubclassOf<UChaosVehicleWheel> WheelClass;
};

/** A rigid assembly retains its actual source pivot in the sampled delta track. */
USTRUCT(BlueprintType)
struct FMaskVehiclePart
{
	GENERATED_BODY()
	UPROPERTY(EditAnywhere, BlueprintReadOnly) FName Name;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) TObjectPtr<UStaticMesh> Mesh;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) TArray<FTransform> Samples;
	/** FL, FR, RL, RR: animated from the corresponding Chaos wheel, not a duplicate tire. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly) FName Wheel;
	/** Continuous rotor rotation at full deployment, in source vehicle centimetres. */
	UPROPERTY(EditAnywhere) FVector RotorAxis = FVector::ZeroVector;
	UPROPERTY(EditAnywhere) FVector RotorPivot = FVector::ZeroVector;
	UPROPERTY(EditAnywhere) float RotorSpeedDegrees = 0.f;
};

/** Asset-specific geometry, timing and physics; no Thunderhawk mechanisms in the mode protocol. */
UCLASS(BlueprintType)
class UMaskVehicleDefinition : public UPrimaryDataAsset
{
	GENERATED_BODY()
public:
	UPROPERTY(EditAnywhere, BlueprintReadOnly) FString VehicleName = TEXT("Thunderhawk");
	UPROPERTY(EditAnywhere, BlueprintReadOnly) FString DriverName = TEXT("Matt Trakker");
	UPROPERTY(EditAnywhere, BlueprintReadOnly) FString MaskName = TEXT("Spectrum");
	UPROPERTY(EditAnywhere, BlueprintReadOnly) bool bSupportsFlight = true;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) FMaskDynamicsSettings Dynamics;
	UPROPERTY(EditAnywhere) float MassKg = 1450.f;
	UPROPERTY(EditAnywhere) float EngineTorque = 0.f;
	UPROPERTY(EditAnywhere) TArray<FMaskWheelDefinition> Wheels;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) TArray<FMaskVehiclePart> Parts;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) TObjectPtr<USkeletalMesh> Chassis;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) TObjectPtr<USkeletalMesh> Driver;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) TObjectPtr<USkeletalMesh> Hair;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) TObjectPtr<USkeletalMesh> Mask;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) TObjectPtr<UAnimSequence> DrivingPose;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) TObjectPtr<UAnimSequence> StandingPose;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) TObjectPtr<class UBlendSpace> DriverLocomotion;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) TObjectPtr<UAnimSequence> DriverJump;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) FVector DriverLocation = FVector(0,-40,0);
	UPROPERTY(EditAnywhere) TObjectPtr<USkeletalMesh> Passenger;
	UPROPERTY(EditAnywhere) TObjectPtr<USkeletalMesh> PassengerHair;
	UPROPERTY(EditAnywhere) TObjectPtr<USkeletalMesh> PassengerMask;
	UPROPERTY(EditAnywhere) TObjectPtr<UAnimSequence> PassengerPose;
	UPROPERTY(EditAnywhere) FVector PassengerLocation = FVector::ZeroVector;
	UPROPERTY(EditAnywhere) FVector ChaseLocation = FVector(0,0,110);
	UPROPERTY(EditAnywhere) float ChaseDistance = 600.f;
	UPROPERTY(EditAnywhere) FVector CockpitLocation = FVector(-45,-40,112);
	UPROPERTY(EditAnywhere) FVector MountedDriverLocation = FVector::ZeroVector;
	UPROPERTY(EditAnywhere) FVector VisualOriginOffset = FVector::ZeroVector;
	UPROPERTY(EditAnywhere) FVector RearModuleOrigin = FVector::ZeroVector;
	UPROPERTY(EditAnywhere) bool bOverrideCenterOfMass = false;
	UPROPERTY(EditAnywhere) FVector CenterOfMass = FVector::ZeroVector;
	UPROPERTY(EditAnywhere) TObjectPtr<UAnimSequence> DriverTransformationPose;
	UPROPERTY(EditAnywhere) TArray<FTransform> DriverTransformSamples;
	UPROPERTY(EditAnywhere) TObjectPtr<UStaticMesh> SpareMesh;
	UPROPERTY(EditAnywhere) TArray<FTransform> SpareMountSamples;
	UPROPERTY(EditAnywhere) TObjectPtr<UMaskVehicleDefinition> RearModule;
	UPROPERTY(EditAnywhere) TArray<FTransform> RearModuleTrack;
	UPROPERTY(EditAnywhere, BlueprintReadOnly) float TransformSeconds = 4.f;
	/** Conservative upper-body sweep, measured from the source assembly in centimetres. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly) FVector ClearanceCenter = FVector(0,0,165);
	UPROPERTY(EditAnywhere, BlueprintReadOnly) FVector ClearanceExtent = FVector(245,175,80);
};
