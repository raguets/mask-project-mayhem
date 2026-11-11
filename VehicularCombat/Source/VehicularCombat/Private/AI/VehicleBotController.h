#pragma once

#include "CoreMinimal.h"
#include "AIController.h"
#include "VehicleBotController.generated.h"

/** Lightweight training opponent. Drives the actual Chaos pawn; no transform teleport steering. */
UCLASS()
class AVehicleBotController : public AAIController
{
	GENERATED_BODY()
public:
	AVehicleBotController();
	virtual void Tick(float DeltaSeconds) override;
	virtual void OnPossess(APawn* InPawn) override;
	int32 TrainingIndex = 0;
	bool bCompanion = false;
private:
	float StuckSeconds = 0.f;
	float ReverseUntil = 0.f;
	float NextShotAt = 0.f;
};
