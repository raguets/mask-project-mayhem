#pragma once
#include "CoreMinimal.h"
#include "MASK/ThunderhawkPawn.h"
#include "RhinoPawn.generated.h"

UCLASS()
class URhinoFrontWheel : public UChaosVehicleWheel
{
    GENERATED_BODY()
public: URhinoFrontWheel();
};
UCLASS()
class URhinoRearWheel : public UChaosVehicleWheel
{
    GENERATED_BODY()
public: URhinoRearWheel();
};
UCLASS()
class URhinoPodFrontWheel : public UChaosVehicleWheel
{
    GENERATED_BODY()
public: URhinoPodFrontWheel();
};
UCLASS()
class URhinoPodRearWheel : public UChaosVehicleWheel
{
    GENERATED_BODY()
public: URhinoPodRearWheel();
};
class ARhinoPawn;

/** Six-wheel playable companion; the same Bruce moves from cab to rear seat. */
UCLASS()
class ARhinoRearModule : public AThunderhawkPawn
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
    virtual bool IsAvailableToSwitch() const override { return bDetached && Super::IsAvailableToSwitch(); }
    void SetDetached(bool Value);
    UPROPERTY(ReplicatedUsing=ApplyMountedState, BlueprintReadOnly) bool bDetached = false;
    UPROPERTY(Replicated, BlueprintReadOnly) TObjectPtr<ARhinoPawn> ParentTruck;
protected:
    virtual const TCHAR* DefaultDefinitionPath() const override { return TEXT("/Game/MASK/Rhino/DA_RhinoRear.DA_RhinoRear"); }
    virtual float VisualDeployment() const override;
    virtual const UChaosVehicleWheel* AnimationWheel(FName Name) const override;
    virtual void ToggleMode() override;
    virtual void Destroyed() override;
private:
    UFUNCTION() void ApplyMountedState();
    UFUNCTION(Server, Reliable) void ServerRequestDock();
};

/** Ground-only truck and its independently controllable, allied rear vehicle. */
UCLASS()
class ARhinoPawn : public AThunderhawkPawn
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    virtual void Tick(float DeltaSeconds) override;
    virtual bool CanChangeVehicleMode(FString& Reason) const override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
    UPROPERTY(Replicated, BlueprintReadOnly) TObjectPtr<ARhinoRearModule> RearModule;
	FVector CompanionOffset() const { return FVector(-750,450,0); }
protected:
    virtual const TCHAR* DefaultDefinitionPath() const override { return TEXT("/Game/MASK/Rhino/DA_Rhino.DA_Rhino"); }
};
