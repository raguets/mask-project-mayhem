// Copyright 2022 Danial Kamali. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Enumerations/ActorEnums.h"
#include "Pawns/BaseWheeledVehiclePawn.h"
#include "PlayerWheeledVehiclePawn.generated.h"

class USpringArmComponent;
class UCameraComponent;
class AMaskDriverCharacter;
class UMaskVehicleDefinition;

UCLASS()
class APlayerWheeledVehiclePawn : public ABaseWheeledVehiclePawn
{
	GENERATED_BODY()

	/** Spring arm that will offset the camera */
	UPROPERTY(VisibleDefaultsOnly, BlueprintReadOnly, Category = "Components", meta = (AllowPrivateAccess = "true"))
	USpringArmComponent* SpringArmOutside;

	/** Camera component that will be our viewpoint */
	UPROPERTY(VisibleDefaultsOnly, BlueprintReadOnly, Category = "Components", meta = (AllowPrivateAccess = "true"))
	UCameraComponent* CameraOutside;

	UPROPERTY(VisibleDefaultsOnly, BlueprintReadOnly, Category = "Components", meta = (AllowPrivateAccess = "true"))
	USpringArmComponent* SpringArmInside;

	/** Camera component for the In-Car view */
	UPROPERTY(VisibleDefaultsOnly, BlueprintReadOnly, Category = "Components", meta = (AllowPrivateAccess = "true"))
	UCameraComponent* CameraInside;

	UPROPERTY(VisibleDefaultsOnly, BlueprintReadOnly, Category = "Components", meta = (AllowPrivateAccess = "true"))
	class UWidgetComponent* WidgetDashboard;

	/** Reset controller rotation timeline */
	UPROPERTY()
	class UTimelineComponent* ResetRotationTimeline;

// Functions
public:
	APlayerWheeledVehiclePawn(const FObjectInitializer& ObjectInitializer = FObjectInitializer::Get());
	void ReturnToMainMenu();
	bool IsPauseMenuOpen() const { return bPauseMenuOpen; }
	bool IsInCarView() const { return bInCarCamera; }
	virtual bool IsAvailableToSwitch() const { return !IsDriverOnFoot(); }
	bool IsDriverOnFoot() const;
	virtual UMaskVehicleDefinition* GetDriverDefinition() const;
	virtual bool CanDriverExit(FString& Reason) const;
	TArray<FVector> GetDriverExitOffsets() const;
	UPROPERTY(ReplicatedUsing=RefreshDriverCharacter,BlueprintReadOnly) TObjectPtr<AMaskDriverCharacter> DriverCharacter;
	UFUNCTION(Server,Reliable) void ServerRequestDriverExit();
	UFUNCTION(Server,Reliable) void ServerRetryMission();
	virtual int32 FleetSelectionGroup() const { return 100; }
	virtual bool CanVehicleJump() const { return true; }
	virtual bool UsesPhysicalPowerBoost() const { return false; }
	bool IsAlliedWith(const APlayerWheeledVehiclePawn* Other) const { return Other && FleetTeamId!=0 && FleetTeamId==Other->FleetTeamId; }
	UPROPERTY(Replicated, BlueprintReadOnly) int32 FleetTeamId = 0;
	void CycleVehicle(int32 Direction);
	UPROPERTY(BlueprintReadOnly) FString VehicleSwitchStatus;
	UFUNCTION(Client, Reliable) void ClientVehicleSwitchFeedback(const FString& Message);
	
protected:
	virtual void DriverCharacterReady();
	virtual bool HandleVehicleWeaponModifier() { return false; }
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type Reason) override;
	virtual void PawnClientRestart() override;
	virtual void PossessedBy(AController* NewController) override;
	virtual void UnPossessed() override;
	virtual void Tick(float DeltaSeconds) override;
	virtual void SetupPlayerInputComponent(UInputComponent* InputComponent) override;
	virtual void Destroyed() override;

private:
	void InitializeDriverCharacter();
	UFUNCTION() void RefreshDriverCharacter();
	UFUNCTION(Client, Reliable)
	void ClientInitialize();
	void ClientInitialize_Implementation();
	
	/** Handle pressing forwards */
	void MoveForward(float Value);

	/** Handle pressing right */
	void MoveRight(float Value);

	void LookUp(float Value);
	void LookRight(float Value);
	void LookUpRate(float Value);
	void LookRightRate(float Value);
	void RecenterCamera();
	void CycleWeaponOrReturnToMenu();
	void TogglePauseMenu();
	void ResumeFromPause();
	void ToggleControlsHelp();
	void NextVehicle();
	void PreviousVehicle();
	UFUNCTION(Server, Reliable) void ServerCycleVehicle(int32 Direction);
	void ShowScoreboard();
	void HideScoreboard();

	UFUNCTION(Server, Reliable)
	void ServerWakeRigidBodies();
	void ServerWakeRigidBodies_Implementation();

	UFUNCTION()
	void PlayResetTimeline();

	/** Reset control rotation with timeline */
	UFUNCTION()
	void ResetControlRotation(float Value);

	/** Set Use Pawn Control Rotation to false after timeline finished */
	UFUNCTION()
	void SetUseRotation();
	
	/** Handle handbrake pressed */
	void OnHandbrakePressed();
	
	/** Handle handbrake released */
	void OnHandbrakeReleased();
	
	/** Switch between cameras */
	void ToggleCamera();

	UFUNCTION()
	void ResetToggleCamera();

	UFUNCTION(Server, Reliable)
	void ServerToggleCamera();
	void ServerToggleCamera_Implementation();

	virtual void ServerSetHealthLevel_Implementation(float CurrentHealth, float MaxHealth) override;

	/** Update health on player UI */
	UFUNCTION(Client, Unreliable)
	void ClientUpdateHealth(float NewHealth);
	void ClientUpdateHealth_Implementation(float NewHealth);

	UFUNCTION(Client, Reliable)
	void ClientUpdateCurrentCamera(bool bInCar);
	void ClientUpdateCurrentCamera_Implementation(bool bInCar);

	void TryToJump();

	/** Switch to primary weapon */
	void SwitchToPrimary();

	/** Switch to secondary weapon */
	void SwitchToSecondary();

	void StartFireWeapon();
	void StopFireWeapon();

	/** Add recoil to player crosshair */
	void AddRecoil();
	
	virtual void ClientUpdatePickup_Implementation(EPickupType PickupType) override;
	
	virtual void OnRep_CurrentWeapon() override;
	virtual void OnRep_IsAlive() override;

	/** Update the gear and speed */
	void UpdateUI() const;
	void InitializeLocalView();
	bool bLocalViewInitialized = false;
	bool bCameraTimelineConfigured = false;
	bool bLoadoutInitialized = false;
	UPROPERTY() TObjectPtr<AWeaponPickupActor> StoredPrimary;
	UPROPERTY() TObjectPtr<AWeaponPickupActor> StoredSecondary;
	bool bPauseMenuOpen = false;
	bool bGamepadCameraDriven = false;
	FVector2D GamepadLook = FVector2D::ZeroVector;
	float LastCameraVehicleYaw = 0.f;

	virtual void ClientUpdateWeaponState_Implementation(EWeaponState WeaponState) override;
	virtual void ClientUpdateAmmo_Implementation(int32 CurrentAmmo) override;
	virtual void ClientUpdateMagAmmo_Implementation(int32 CurrentMagAmmo) override;

// Variables
private:
	UPROPERTY(EditDefaultsOnly, Category = "Defaults")
	TSubclassOf<AWeaponPickupActor> PrimaryWeaponToAdd;

	UPROPERTY(EditDefaultsOnly, Category = "Defaults")
	TSubclassOf<AWeaponPickupActor> SecondaryWeaponToAdd;

	UPROPERTY(Replicated, EditDefaultsOnly, Category = "Defaults", meta = (ToolTip = "Setting this to false will override Auto Adjust Camera.", AllowPrivateAccess = true))
	uint8 bCanAim : 1;

	UPROPERTY(EditDefaultsOnly, Category = "Defaults", meta = (ToolTip = "Automatically moves the camera to its default location", AllowPrivateAccess = true))
	uint8 bAutoAdjustCamera : 1;

	UPROPERTY(EditDefaultsOnly, Category = "Defaults", meta = (ToolTip = "A delay between toggling the camera to stop the player from spamming the server.", AllowPrivateAccess = true))
	float ToggleCameraCooldown;
	
	UPROPERTY(EditDefaultsOnly, Category = "Defaults", meta = (ToolTip = "Enable it if the vehicle has no roof and the dashboard is always visible.", AllowPrivateAccess = true))
	uint8 bAlwaysUpdateDashboard : 1;
	
	UPROPERTY(EditDefaultsOnly, Category = "Defaults")
	UCurveFloat* ResetRotationCurve;
	
	/** Are we using In-Car camera */
	UPROPERTY(Replicated)
	bool bInCarCamera;

	uint8 bDoOnceResetRotation : 1, bCanToggleCamera : 1, bCanWakeRigidBodies : 1;

	/** Can the player look left and right? Used to limit the player's field of view inside the car. */
	uint8 bCanLookRight : 1;
	
	/** Initial offset of inCar camera */
	FVector InternalCameraOrigin;

	float LookUpValue, LookRightValue;

	UPROPERTY(Replicated)
	APlayerController* PlayerControllerRef;

	UPROPERTY()
	class APlayerHUD* PlayerHUDRef;

	UPROPERTY()
	class UInCarWidget* WidgetRef;

	FTimerHandle ResetRotationTimer, RecoilTimer, ToggleCameraTimer;
};
