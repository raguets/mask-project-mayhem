#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MASK/MaskVehicleModeComponent.h"
#include "MaskDynamicsComponent.generated.h"

/** Forces on the existing Chaos body, with a shared plane/helicopter transition policy. */
UCLASS(ClassGroup=MASK)
class UMaskDynamicsComponent : public UActorComponent
{
	GENERATED_BODY()
public:
	UMaskDynamicsComponent();
	virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
	void SetPilotInput(FVector Value);
	void Simulate(float DeltaSeconds);
	UFUNCTION(BlueprintPure) float GetTargetAirspeedMPS() const { return TargetAirspeedMPS; }
	UFUNCTION(BlueprintPure) float KineticEnergyKJ() const;
	bool IsAirborneMode() const;
	UPROPERTY(Replicated, BlueprintReadOnly) float GroundClearanceCM = 0.f;
private:
	UPROPERTY(Replicated) float TargetAirspeedMPS = 0.f;
	FVector PilotInput = FVector::ZeroVector;
	EMaskVehicleMode PreviousMode = EMaskVehicleMode::Road;
	bool bAirForces = false, bTakeoffAssist = false;
	float NominalEngineTorque = 0.f, LastEngineTorque = -1.f;
	void ApplyAttitude(class USkeletalMeshComponent* Body,const FQuat& Target,FVector DesiredAngularVelocity) const;
};
