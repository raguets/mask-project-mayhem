#pragma once

#include "CoreMinimal.h"
#include "MASK/ThunderhawkPawn.h"
#include "HurricanePawn.generated.h"

UCLASS()
class UHurricaneFrontWheel : public UChaosVehicleWheel
{
    GENERATED_BODY()
public: UHurricaneFrontWheel();
};
UCLASS()
class UHurricaneRearWheel : public UChaosVehicleWheel
{
    GENERATED_BODY()
public: UHurricaneRearWheel();
};
class AHurricanePawn;

/** One persistent spare: attached cover/wheel first, then a replicated rigid body. */
UCLASS()
class AHurricaneSpareWheel : public AActor
{
    GENERATED_BODY()
public:
    AHurricaneSpareWheel();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
    void Launch();
    UPROPERTY(VisibleAnywhere) TObjectPtr<UStaticMeshComponent> WheelMesh;
    UPROPERTY(ReplicatedUsing=ApplyState) TObjectPtr<AHurricanePawn> ParentVehicle;
    UPROPERTY(ReplicatedUsing=ApplyState) bool bEjected=false;
private:
    UFUNCTION() void ApplyState();
};

/** Six stable Chaos slots; the middle pair supplies contact/drive only when deployed. */
UCLASS()
class AHurricanePawn : public AThunderhawkPawn
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
    UFUNCTION(Server,Reliable) void ServerLaunchSpare();
    UPROPERTY(Replicated) TObjectPtr<AHurricaneSpareWheel> SpareWheel;
protected:
    virtual const TCHAR* DefaultDefinitionPath() const override { return TEXT("/Game/MASK/Hurricane/DA_Hurricane.DA_Hurricane"); }
    virtual bool HandleVehicleWeaponModifier() override;
    virtual const UChaosVehicleWheel* AnimationWheel(FName Name) const override;
private:
    void ConfigureRoadWheels(bool Six);
    bool bWheelConfigurationReady=false;
    bool bCentreWheelsActive=false;
};
