#include "UI/MainMenuWidget.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/Button.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/CheckBox.h"
#include "Components/EditableText.h"
#include "Components/EditableTextBox.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "Components/TextBlock.h"
#include "Core/OnlineGameInstance.h"
#include "Styling/CoreStyle.h"
#include "TimerManager.h"
#include "GameFramework/PlayerController.h"

void UMainMenuWidget::NativeConstruct()
{
	Super::NativeConstruct();
	SetIsFocusable(true);
	if (!WidgetTree) { return; }
	// The old host form uses a hint, not a default session name. Its Blueprint
	// refuses an empty field before calling the GameInstance, showing only EMPTY.
	WidgetTree->ForEachWidgetAndDescendants([this](UWidget* Widget)
	{
		if (auto* Button = Cast<UButton>(Widget))
		{
			if (auto* Label = Cast<UTextBlock>(Button->GetChildAt(0)); Label && Label->GetText().ToString() == TEXT("Join"))
			{
				Button->OnClicked.AddUniqueDynamic(this, &UMainMenuWidget::SearchLAN);
			}
			else if (Label && Label->GetText().ToString() == TEXT("Host"))
			{
				Button->OnClicked.AddUniqueDynamic(this, &UMainMenuWidget::ShowHostInstructions);
			}
		}
		if (auto* Text = Cast<UEditableText>(Widget))
		{
			if (Text->GetName().Contains(TEXT("Session")) || Text->GetHintText().ToString().Contains(TEXT("Session")))
			{
				if (Text->GetText().IsEmpty()) { Text->SetText(FText::FromString(TEXT("Partie locale"))); }
				FEditableTextStyle Style = FEditableTextStyle::GetDefault();
				Style.SetFont(FCoreStyle::GetDefaultFontStyle(TEXT("Regular"), 22));
				Style.SetColorAndOpacity(FSlateColor(FLinearColor::White));
				Text->SetWidgetStyle(Style);
				Text->OnTextChanged.AddUniqueDynamic(this, &UMainMenuWidget::SessionNameChanged);
			}
		}
		if (auto* TextBox = Cast<UEditableTextBox>(Widget))
		{
			if (TextBox->GetName().Contains(TEXT("Session")) || TextBox->GetHintText().ToString().Contains(TEXT("Session")))
			{
				if (TextBox->GetText().IsEmpty()) { TextBox->SetText(FText::FromString(TEXT("Partie locale"))); }
				TextBox->SetForegroundColor(FLinearColor::White);
				TextBox->OnTextChanged.AddUniqueDynamic(this, &UMainMenuWidget::SessionNameChanged);
			}
		}
		if (auto* Check = Cast<UCheckBox>(Widget); Check && Check->GetName().Contains(TEXT("LAN"))) { Check->SetIsChecked(true); }
	});
	if (!StatusText)
	{
		auto* Canvas = Cast<UCanvasPanel>(WidgetTree->RootWidget);
		if (!Canvas) { UE_LOG(LogTemp, Error, TEXT("MainMenu extension expects the original CanvasPanel root")); return; }
		auto* Background = WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass(), TEXT("TrainingMenuBar"));
		Background->SetBrushColor(FLinearColor(0.025f,0.035f,0.05f,0.96f));
		Background->SetPadding(FMargin(12.f));
		auto* BarSlot = Canvas->AddChildToCanvas(Background);
		// Reserve the empty space above the left navigation. A full-width bar
		// overlaps the original server browser's first row on the right.
		BarSlot->SetAnchors(FAnchors(0.f,0.f,0.25f,0.f));
		BarSlot->SetOffsets(FMargin(20.f,20.f,20.f,325.f));
		BarSlot->SetZOrder(10000);
		auto* Row = WidgetTree->ConstructWidget<UVerticalBox>();
		Background->SetContent(Row);
		auto* Solo = WidgetTree->ConstructWidget<UButton>(UButton::StaticClass(), TEXT("PlaySoloButton"));
		Solo->SetBackgroundColor(FLinearColor(0.08f,0.55f,0.35f));
		Solo->OnClicked.AddUniqueDynamic(this, &UMainMenuWidget::PlaySolo);
		auto* Label = WidgetTree->ConstructWidget<UTextBlock>();
		Label->SetText(FText::FromString(TEXT("Solo contre 3 bots")));
		Label->SetFont(FCoreStyle::GetDefaultFontStyle(TEXT("Bold"), 22));
		Label->SetColorAndOpacity(FLinearColor::White);
		Solo->SetContent(Label);
		auto* ButtonSlot = Row->AddChildToVerticalBox(Solo);
		ButtonSlot->SetPadding(FMargin(8.f));
		auto* Vehicle=WidgetTree->ConstructWidget<UCheckBox>(UCheckBox::StaticClass(),TEXT("ThunderhawkSelection"));
		auto* VehicleLabel=WidgetTree->ConstructWidget<UTextBlock>();
		VehicleLabel->SetText(FText::FromString(TEXT("Thunderhawk (Solo / Host)")));
		VehicleLabel->SetFont(FCoreStyle::GetDefaultFontStyle(TEXT("Regular"),18));
		VehicleLabel->SetColorAndOpacity(FLinearColor::White);Vehicle->SetContent(VehicleLabel);
		if (auto* GI=Cast<UOnlineGameInstance>(GetGameInstance())) { Vehicle->SetIsChecked(GI->bThunderhawkSelected); }
		Vehicle->OnCheckStateChanged.AddUniqueDynamic(this,&UMainMenuWidget::SelectThunderhawk);
		Row->AddChildToVerticalBox(Vehicle);Vehicle->SetVisibility(ESlateVisibility::Collapsed);
		auto* Choice=WidgetTree->ConstructWidget<UButton>(UButton::StaticClass(),TEXT("VehicleChoiceButton"));
		VehicleChoiceText=WidgetTree->ConstructWidget<UTextBlock>();VehicleChoiceText->SetFont(FCoreStyle::GetDefaultFontStyle(TEXT("Regular"),18));
		Choice->SetContent(VehicleChoiceText);Choice->OnClicked.AddUniqueDynamic(this,&UMainMenuWidget::CycleVehicleChoice);
		Row->AddChildToVerticalBox(Choice)->SetPadding(FMargin(8.f));RefreshVehicleChoice();
		auto* PadHelp=WidgetTree->ConstructWidget<UTextBlock>();
		PadHelp->SetText(FText::FromString(TEXT("Xbox : stick/croix pour naviguer\nA : valider  X : vehicule\nMenu : jouer en solo  B : retour")));
		PadHelp->SetFont(FCoreStyle::GetDefaultFontStyle(TEXT("Regular"),16));PadHelp->SetColorAndOpacity(FLinearColor(.7f,.9f,1));
		Row->AddChildToVerticalBox(PadHelp)->SetPadding(FMargin(8.f));
		StatusText = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), TEXT("SessionStatusText"));
		StatusText->SetFont(FCoreStyle::GetDefaultFontStyle(TEXT("Regular"), 18));
		StatusText->SetColorAndOpacity(FLinearColor::White);
		StatusText->SetAutoWrapText(true);
		auto* TextSlot = Row->AddChildToVerticalBox(StatusText);
		TextSlot->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
		TextSlot->SetPadding(FMargin(16.f,8.f));
		TextSlot->SetVerticalAlignment(VAlign_Center);
	}
	if (auto* GI = Cast<UOnlineGameInstance>(GetGameInstance()))
	{
		GI->FrontendStatusChanged.AddUniqueDynamic(this, &UMainMenuWidget::ShowStatus);
		ShowStatus(GI->FrontendStatus.IsEmpty()
			? FText::FromString(TEXT("Solo : jouez immediatement sans reseau. Host cree une partie ; Join cherche celle d'un autre joueur.")) : GI->FrontendStatus);
	}
	GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this]()
	{
		if (IsInViewport()) { if (auto* Button=Cast<UButton>(GetWidgetFromName(TEXT("PlaySoloButton")))) { Button->SetUserFocus(GetOwningPlayer()); } }
	}));
}

FReply UMainMenuWidget::NativeOnKeyDown(const FGeometry& Geometry,const FKeyEvent& Event)
{
	const FKey Key=Event.GetKey();
	if (Key==EKeys::Gamepad_Special_Right) { PlaySolo();return FReply::Handled(); }
	if (Key==EKeys::Gamepad_FaceButton_Left)
	{
		CycleVehicleChoice();return FReply::Handled();
	}
	if (Key==EKeys::Gamepad_FaceButton_Right)
	{
		UButton* Back=nullptr;
		WidgetTree->ForEachWidgetAndDescendants([&](UWidget* Widget)
		{
			if (auto* Button=Cast<UButton>(Widget);Button && Button->GetIsEnabled())
			{
				if (const auto* Label=Cast<UTextBlock>(Button->GetChildAt(0));Label && Label->GetText().ToString()==TEXT("Back")) { Back=Button; }
			}
		});
		if (Back) { Back->OnClicked.Broadcast();if (auto* Solo=Cast<UButton>(GetWidgetFromName(TEXT("PlaySoloButton")))) { Solo->SetUserFocus(GetOwningPlayer()); } }
		return FReply::Handled();
	}
	return Super::NativeOnKeyDown(Geometry,Event);
}

void UMainMenuWidget::NativeDestruct()
{
	if (auto* GI = Cast<UOnlineGameInstance>(GetGameInstance())) { GI->FrontendStatusChanged.RemoveDynamic(this, &UMainMenuWidget::ShowStatus); }
	Super::NativeDestruct();
}

void UMainMenuWidget::PlaySolo()
{
	if (auto* GI = Cast<UOnlineGameInstance>(GetGameInstance())) { GI->StartSoloGame(3); }
}

void UMainMenuWidget::SelectThunderhawk(bool bChecked)
{
	if (auto* GI=Cast<UOnlineGameInstance>(GetGameInstance())) { GI->bThunderhawkSelected=bChecked; }
	RefreshVehicleChoice();
}

void UMainMenuWidget::RefreshVehicleChoice()
{
	if(const auto* GI=Cast<UOnlineGameInstance>(GetGameInstance());GI && VehicleChoiceText)
	{
		VehicleChoiceText->SetText(FText::FromString(TEXT("Vehicule : ")+(GI->bThunderhawkSelected?GI->MaskVehicleChoice:TEXT("Original"))));
	}
}

void UMainMenuWidget::CycleVehicleChoice()
{
	if(auto* GI=Cast<UOnlineGameInstance>(GetGameInstance()))
	{
		if(!GI->bThunderhawkSelected) { GI->bThunderhawkSelected=true;GI->MaskVehicleChoice=TEXT("Thunderhawk"); }
		else if(GI->MaskVehicleChoice==TEXT("Thunderhawk")) { GI->MaskVehicleChoice=TEXT("Rhino"); }
		else if(GI->MaskVehicleChoice==TEXT("Rhino")) { GI->MaskVehicleChoice=TEXT("Hurricane"); }
		else if(GI->MaskVehicleChoice==TEXT("Hurricane")) { GI->MaskVehicleChoice=TEXT("Raven"); }
		else if(GI->MaskVehicleChoice==TEXT("Raven")) { GI->MaskVehicleChoice=TEXT("Condor"); }
		else if(GI->MaskVehicleChoice==TEXT("Condor")) { GI->MaskVehicleChoice=TEXT("Switchblade"); }
		else if(GI->MaskVehicleChoice==TEXT("Switchblade")) { GI->MaskVehicleChoice=TEXT("Manta"); }
		else { GI->bThunderhawkSelected=false;GI->MaskVehicleChoice=TEXT("Thunderhawk"); }
		if(auto* Check=Cast<UCheckBox>(GetWidgetFromName(TEXT("ThunderhawkSelection")))) { Check->SetIsChecked(GI->bThunderhawkSelected); }
		RefreshVehicleChoice();
	}
}

void UMainMenuWidget::SearchLAN()
{
	if (auto* GI = Cast<UOnlineGameInstance>(GetGameInstance())) { GI->FindSessions(); }
}

void UMainMenuWidget::ShowStatus(FText Message)
{
	if (StatusText)
	{
		StatusText->SetText(Message);
		// Original page-switch graphs hide the other Canvas children. The shared
		// toolbar is an extension, not one of their mutually exclusive pages.
		for (UWidget* Widget = StatusText; Widget && Widget != WidgetTree->RootWidget; Widget = Widget->GetParent())
		{
			Widget->SetVisibility(ESlateVisibility::SelfHitTestInvisible);
			if (auto* CanvasSlot = Cast<UCanvasPanelSlot>(Widget->Slot)) { CanvasSlot->SetZOrder(10000); }
		}
	}
}

void UMainMenuWidget::ShowHostInstructions()
{
	ShowStatus(FText::FromString(TEXT("Gardez ou modifiez le nom, puis Create Session. Le terrain se charge apres la creation LAN.")));
}

void UMainMenuWidget::SessionNameChanged(const FText& Name)
{
	ShowStatus(FText::FromString(Name.ToString().TrimStartAndEnd().IsEmpty()
		? TEXT("Saisissez un nom de partie avant Create Session, ou utilisez Solo contre bots.")
		: TEXT("Nom renseigne. Create Session lance le terrain en mode hote LAN.")));
}
