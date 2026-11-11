#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "MaskDriverCharacter.generated.h"

class APlayerWheeledVehiclePawn;
class UMaskVehicleDefinition;
class AWeaponPickupActor;

/** One persistent driver actor: the same mesh, face and mask rides and walks. */
UCLASS()
class AMaskDriverCharacter : public ACharacter
{
    GENERATED_BODY()
public:
    AMaskDriverCharacter(const FObjectInitializer& ObjectInitializer);
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    virtual void SetupPlayerInputComponent(UInputComponent* Input) override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
    virtual void PawnClientRestart() override;
    virtual void PossessedBy(AController* Controller) override;
    void InitializeDriver(APlayerWheeledVehiclePawn* Vehicle);
    void LeaveVehicle(const FTransform& Exit,APlayerController* Player);
    void RefreshDriverState();
    void ToggleMaskFromVehicle();
    bool IsOnFoot() const { return bOnFoot; }
    bool IsMasked() const { return bMaskVisible; }
    bool IsSprinting() const { return bSprinting; }
    bool IsPauseMenuOpen() const { return bPaused; }
    bool IsReloading() const { return bReloading; }
    UPROPERTY(ReplicatedUsing=OnRep_DriverState,BlueprintReadOnly) TObjectPtr<APlayerWheeledVehiclePawn> SourceVehicle;
    UPROPERTY(ReplicatedUsing=OnRep_DriverState,BlueprintReadOnly) TObjectPtr<UMaskVehicleDefinition> Definition;
    UPROPERTY(VisibleAnywhere) TObjectPtr<USkeletalMeshComponent> Hair;
    UPROPERTY(VisibleAnywhere) TObjectPtr<USkeletalMeshComponent> Mask;
    UPROPERTY(Replicated,BlueprintReadOnly) TObjectPtr<AWeaponPickupActor> HandWeapon;
    UPROPERTY(Replicated,BlueprintReadOnly) int32 FleetTeamId=0;
    UPROPERTY(ReplicatedUsing=OnRep_Health,BlueprintReadOnly) float Health=100.f;
    UPROPERTY(BlueprintReadOnly) FString Status;
    UFUNCTION(Server,Reliable) void ServerEnterVehicle();
    UFUNCTION(Server,Reliable) void ServerToggleMask();
    UFUNCTION(Server,Reliable) void ServerSetSprint(bool Value);
    UFUNCTION(Server,Reliable) void ServerSetFiring(bool Value);
    UFUNCTION(Client,Reliable) void ClientStatus(const FString& Value);
private:
    UPROPERTY(VisibleAnywhere) TObjectPtr<class USpringArmComponent> CameraArm;
    UPROPERTY(VisibleAnywhere) TObjectPtr<class UCameraComponent> Camera;
    UPROPERTY(ReplicatedUsing=OnRep_DriverState) bool bOnFoot=false;
    UPROPERTY(ReplicatedUsing=OnRep_DriverState) bool bMaskVisible=true;
    UPROPERTY(Replicated) bool bSprinting=false;
    UPROPERTY(Replicated) bool bReloading=false;
    bool bFiring=false,bPaused=false,bWasOnFoot=false,bViewInitialized=false;
    float NextShotAt=0.f,ReloadAt=0.f;
    FVector2D LookInput=FVector2D::ZeroVector;
    FTimerHandle RespawnTimer;
    UFUNCTION() void OnRep_DriverState();
    UFUNCTION() void OnRep_Health();
    UFUNCTION() void TakeDriverDamage(AActor* Victim,float Amount,const UDamageType* Type,AController* InstigatedBy,AActor* Causer);
    void RespawnDriver();
    void InitializeLocalView();
    void MoveForward(float Value);
    void MoveRight(float Value);
    void LookPitch(float Value);
    void LookYaw(float Value);
    void LookPitchMouse(float Value);
    void LookYawMouse(float Value);
    void JumpOrResume();
    void SprintPressed();
    void SprintReleased();
    void FirePressed();
    void FireReleased();
    void TogglePause();
    void Resume();
    void MaskOrMainMenu();
    void EnterFromInput();
    void MaskFromInput();
    void ShowScores();
    void HideScores();
};
