#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "MainMenuWidget.generated.h"

class UTextBlock;

/** Extends the original Blueprint menu, retaining its Host/Join/Settings controls. */
UCLASS(meta = (DisableNativeTick))
class UMainMenuWidget : public UUserWidget
{
	GENERATED_BODY()
protected:
	virtual void NativeConstruct() override;
	virtual void NativeDestruct() override;
	virtual FReply NativeOnKeyDown(const FGeometry& Geometry,const FKeyEvent& Event) override;
private:
	UFUNCTION() void PlaySolo();
	UFUNCTION() void SelectThunderhawk(bool bChecked);
	UFUNCTION() void CycleVehicleChoice();
	void RefreshVehicleChoice();
	UPROPERTY(Transient) TObjectPtr<UTextBlock> VehicleChoiceText;
	UFUNCTION() void SearchLAN();
	UFUNCTION() void ShowHostInstructions();
	UFUNCTION() void SessionNameChanged(const FText& Name);
	UFUNCTION() void ShowStatus(FText Message);
	UPROPERTY(Transient) TObjectPtr<UTextBlock> StatusText;
};
