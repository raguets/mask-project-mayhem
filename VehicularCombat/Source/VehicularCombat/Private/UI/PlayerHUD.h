// Copyright 2022 Danial Kamali. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Enumerations/ActorEnums.h"
#include "GameFramework/HUD.h"
#include "PlayerHUD.generated.h"

UCLASS()
class APlayerHUD : public AHUD
{
	GENERATED_BODY()

// Functions
public:
	virtual void DrawHUD() override;
	/** Possession and client restart may both initialize the same HUD. */
	void EnsureInitialized();
	void SetOnFootMode(bool Value);
	bool bShowXboxControls=false;
	bool bShowPlayerScores=false;
	UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category = "PlayerHUD")
	void Initialize();
	
	UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category = "PlayerHUD")
	void SetUIState(bool bInCar);

	UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category = "PlayerHUD")
	void AddCrosshairRecoil(float Recoil, float ControlTime);
	
	UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category = "PlayerHUD")
	void UpdateSpeedAndGear(int32 Speed, int32 Gear);
	
	/** Update health level on player UI */
	UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category = "PlayerHUD")
	void UpdateHealth(float NewHealth);

	UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category = "PlayerHUD")
	void UpdateCurrentWeapon(EWeaponName WeaponName);

	UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category = "PlayerHUD")
	void UpdateWeaponState(EWeaponState WeaponState);

	UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category = "PlayerHUD")
	void UpdateAmmo(int32 CurrentAmmo);
	
	UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category = "PlayerHUD")
	void UpdateMagAmmo(int32 CurrentMagAmmo);

	UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category = "PlayerHUD")
	void PickupMessage(EPickupType PickupType);
private:
	bool bWidgetsInitialized=false;
	bool bOnFootUI=false;
	TMap<TWeakObjectPtr<class UUserWidget>,uint8> VehicleWidgetVisibility;
};
