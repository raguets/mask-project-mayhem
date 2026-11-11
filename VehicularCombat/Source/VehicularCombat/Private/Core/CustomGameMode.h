// Copyright 2022 Danial Kamali. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "CustomGameMode.generated.h"

UCLASS()
class ACustomGameMode : public AGameModeBase
{
	GENERATED_BODY()
	
// Functions
public:
	virtual void InitGame(const FString& MapName, const FString& Options, FString& ErrorMessage) override;
	virtual void BeginPlay() override;
	virtual void RestartPlayer(AController* NewPlayer) override;
	virtual UClass* GetDefaultPawnClassForController_Implementation(AController* InController) override;
	void CyclePlayerVehicle(class APlayerController* Player,int32 Direction);
	bool SwitchPlayerVehicleTo(class APlayerController* Player,class APlayerWheeledVehiclePawn* Next);
	int32 GetTrainingBotCount() const { return TrainingBotCount; }
	void RememberPlayerVehicle(class APlayerController* Player,class APlayerWheeledVehiclePawn* Vehicle);
	/** Respawn Player */
	UFUNCTION(Server, Reliable)
	void ServerStartRespawn(AController* Controller);

protected:
	virtual void Logout(AController* Exiting) override;

private:
	void SpawnTrainingBots();
	int32 TrainingBotCount = 0;
	bool bMaskFleet = false;
	TMap<TWeakObjectPtr<AController>,TSubclassOf<APawn>> VehicleClasses;
	TMap<TWeakObjectPtr<APlayerController>,double> VehicleSwitchTimes;
	void ServerStartRespawn_Implementation(AController* Controller);

	UFUNCTION(Server, Reliable)
	void ServerRespawn();
	void ServerRespawn_Implementation();

// Variables
private:
	UPROPERTY()
	TArray<AController*> ControllersToRespawn;
	
	UPROPERTY()
	TArray<AController*> ExitedControllers;
};
