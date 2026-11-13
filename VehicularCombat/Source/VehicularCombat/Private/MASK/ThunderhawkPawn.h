#pragma once

#include "CoreMinimal.h"
#include "Pawns/PlayerWheeledVehiclePawn.h"
#include "ChaosVehicleWheel.h"
#include "ThunderhawkPawn.generated.h"

class UMaskVehicleDefinition;
class UMaskVehicleModeComponent;
class UStaticMeshComponent;
class UMaskDynamicsComponent;

UCLASS()
class UThunderhawkFrontWheel : public UChaosVehicleWheel
{
	GENERATED_BODY()
public: UThunderhawkFrontWheel();
};

UCLASS()
class UThunderhawkRearWheel : public UChaosVehicleWheel
{
	GENERATED_BODY()
public: UThunderhawkRearWheel();
};

/** First concrete M.A.S.K. vehicle; original player pawn and weapon/damage path are retained. */
UCLASS()
class AThunderhawkPawn : public APlayerWheeledVehiclePawn
{
	GENERATED_BODY()
public:
	AThunderhawkPawn(const FObjectInitializer& ObjectInitializer = FObjectInitializer::Get());
	virtual void OnConstruction(const FTransform& Transform) override;
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;
	virtual void SetupPlayerInputComponent(UInputComponent* Input) override;
	virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) TObjectPtr<UMaskVehicleDefinition> Definition;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UMaskVehicleModeComponent> Modes;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UMaskDynamicsComponent> Dynamics;
	bool HasPhysicalPowerBoost() const { return bBoostSpeed; }
	virtual bool UsesPhysicalPowerBoost() const override { return true; }
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<USkeletalMeshComponent> Matt;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<USkeletalMeshComponent> MattHair;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<USkeletalMeshComponent> Spectrum;
	UPROPERTY(VisibleAnywhere) TObjectPtr<USkeletalMeshComponent> Passenger;
	UPROPERTY(VisibleAnywhere) TObjectPtr<USkeletalMeshComponent> PassengerHair;
	UPROPERTY(VisibleAnywhere) TObjectPtr<USkeletalMeshComponent> PassengerMask;
	UFUNCTION(Server, Reliable) void ServerToggleMask();
	UFUNCTION(Server, Reliable) void ServerToggleDriverPose();
	UFUNCTION(BlueprintPure) bool IsMaskVisible() const;
	UFUNCTION(BlueprintPure) bool IsNativeAircraft() const;
	virtual bool CanChangeVehicleMode(FString& Reason) const { return true; }
	virtual bool CanVehicleJump() const override;
	virtual UMaskVehicleDefinition* GetDriverDefinition() const override { return Definition; }
	virtual bool CanDriverExit(FString& Reason) const override;
	virtual int32 FleetSelectionGroup() const override;
protected:
	virtual void DriverCharacterReady() override;
	virtual float VisualDeployment() const;
	virtual const UChaosVehicleWheel* AnimationWheel(FName Name) const;
	virtual void ToggleMode();
	virtual void PossessedBy(AController* NewController) override;
	virtual void UnPossessed() override;
	virtual const TCHAR* DefaultDefinitionPath() const { return TEXT("/Game/MASK/Thunderhawk/DA_Thunderhawk.DA_Thunderhawk"); }
public:
	FVector GetPilotInput() const { return FlightInput; }
	void SetAIPilotInput(FVector Input) { if (HasAuthority()) { FlightInput=Input.BoundToCube(1.f); } }
private:
	void FlightForward(float Value);
	void FlightTurn(float Value);
	void FlightLift(float Value);
	UFUNCTION(Server, Unreliable) void ServerFlightInput(FVector Input);
	UFUNCTION() void ApplyPilotState();
	UPROPERTY(ReplicatedUsing=ApplyPilotState) bool bMaskVisible = true;
	UPROPERTY(ReplicatedUsing=ApplyPilotState) bool bDriverStanding = false;
	UPROPERTY() TArray<TObjectPtr<UStaticMeshComponent>> VisualParts;
	FVector FlightInput = FVector::ZeroVector;
	float InputSendElapsed = 0.f;
};
