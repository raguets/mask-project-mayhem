#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MaskVehicleModeComponent.generated.h"

UENUM(BlueprintType)
enum class EMaskVehicleMode : uint8 { Road, Deploying, Flight, Retracting, Combat, Landing };

USTRUCT()
struct FMaskModeState
{
	GENERATED_BODY()
	UPROPERTY() EMaskVehicleMode Mode = EMaskVehicleMode::Road;
	UPROPERTY() double ServerStartTime = 0.;
};

/** Server-owned mode/time protocol. Presentation evaluates the shared timeline locally. */
UCLASS(ClassGroup=MASK, meta=(BlueprintSpawnableComponent))
class UMaskVehicleModeComponent : public UActorComponent
{
	GENERATED_BODY()
public:
	UMaskVehicleModeComponent();
	virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* TickFunction) override;
	UFUNCTION(Server, Reliable) void ServerToggleMode();
	void NotifyTouchdown();
	UFUNCTION(Client, Reliable) void ClientFeedback(const FString& Message);
	UFUNCTION(BlueprintPure) EMaskVehicleMode GetMode() const { return State.Mode; }
	UFUNCTION(BlueprintPure) float GetDeployment() const;
	UPROPERTY(EditAnywhere) float Duration = 4.f;
	UPROPERTY(EditAnywhere) bool bSupportsFlight = true;
	UPROPERTY(EditAnywhere) FVector ClearanceCenter = FVector(0,0,165);
	UPROPERTY(EditAnywhere) FVector ClearanceExtent = FVector(245,175,80);
	UPROPERTY(BlueprintReadOnly) FString LastRefusal;
	UPROPERTY() TArray<TObjectPtr<AActor>> IgnoredModules;
private:
	void Refuse(const TCHAR* Message);
	bool HasArticulationClearance();
	double ServerNow() const;
	UPROPERTY(Replicated) FMaskModeState State;
};
