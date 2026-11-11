// Copyright 2022 Danial Kamali. All Rights Reserved.

#include "PlayerHUD.h"
#include "MASK/MaskDriverCharacter.h"
#include "Actors/WeaponPickupActor.h"
#include "Blueprint/UserWidget.h"
#include "Blueprint/WidgetBlueprintLibrary.h"
#include "AI/VehicleBotController.h"
#include "Components/HealthComponent.h"
#include "Core/CustomGameMode.h"
#include "Engine/Canvas.h"
#include "EngineUtils.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerState.h"
#include "GameFramework/GameStateBase.h"
#include "Pawns/PlayerWheeledVehiclePawn.h"
#include "MASK/ThunderhawkPawn.h"
#include "MASK/MaskVehicleModeComponent.h"
#include "MASK/MaskVehicleDefinition.h"
#include "SilentValley/SilentValleyMission.h"

void APlayerHUD::DrawHUD()
{
	Super::DrawHUD();
	if (!Canvas) { return; }
	const auto* Driver=GetOwningPlayerController()?Cast<AMaskDriverCharacter>(GetOwningPlayerController()->GetPawn()):nullptr;
	SetOnFootMode(Driver!=nullptr);
	if(Driver)
	{
		DrawText(FString::Printf(TEXT("%s | A PIED | %s %s"),Driver->Definition?*Driver->Definition->DriverName:TEXT("Conducteur"),Driver->Definition?*Driver->Definition->MaskName:TEXT("Masque"),Driver->IsMasked()?TEXT("equipe"):TEXT("retire")),FColor(120,230,255),20,18);
		DrawText(FString::Printf(TEXT("Vie : %.0f / 100"),Driver->Health),FColor::White,20,48);
		if(Driver->HandWeapon) { DrawText(FString::Printf(TEXT("Fusil : %d / %d %s"),Driver->HandWeapon->CurrentMagazineAmmo,Driver->HandWeapon->CurrentAmmo,Driver->IsReloading()?TEXT("RECHARGEMENT"):TEXT("")),FColor::White,20,72); }
		if(!Driver->Status.IsEmpty()) { DrawText(Driver->Status,FColor(255,190,80),20,98); }
		DrawLine(Canvas->SizeX*.5f-6,Canvas->SizeY*.5f,Canvas->SizeX*.5f+6,Canvas->SizeY*.5f,FLinearColor::White);
		DrawLine(Canvas->SizeX*.5f,Canvas->SizeY*.5f-6,Canvas->SizeX*.5f,Canvas->SizeY*.5f+6,FLinearColor::White);
		if(Driver->IsPauseMenuOpen())
		{
			DrawRect(FLinearColor(.015f,.025f,.04f,.96f),30,150,FMath::Min(1050.f,Canvas->SizeX-60.f),290);
			const TCHAR* Rows[]={TEXT("A PIED — A ou B : reprendre | Y : menu principal"),TEXT("Stick gauche : marcher | maintenir L3 : courir | Stick droit : regarder / viser"),TEXT("A : sauter | Y : mettre / enlever le masque | RT ou RB : tirer"),TEXT("X : remonter dans son vehicule a proximite | Rechargement automatique"),TEXT("Menu : pause / commandes | View : scores"),TEXT("En vehicule : A fait sortir le conducteur, uniquement a l'arret et au sol.")};
			for(int32 I=0;I<UE_ARRAY_COUNT(Rows);++I) { DrawText(Rows[I],FColor::White,50,175+I*38.f); }
		}
	}
	const auto* Vehicle=GetOwningPlayerController()?Cast<APlayerWheeledVehiclePawn>(GetOwningPlayerController()->GetPawn()):nullptr;
	if (Vehicle)
	{
		if (const auto* MaskCar=Cast<AThunderhawkPawn>(Vehicle))
		{
			const auto State=MaskCar->Modes->GetMode();
			const TCHAR* Mode=State==EMaskVehicleMode::Road?TEXT("ROUTE"):State==EMaskVehicleMode::Flight?TEXT("VOL"):State==EMaskVehicleMode::Landing?TEXT("ATTERRISSAGE AUTO"):State==EMaskVehicleMode::Combat?TEXT("COMBAT"):TEXT("TRANSFORMATION");
			if(MaskCar->Definition) { DrawText(FString::Printf(TEXT("%s  |  %s  |  %s  |  %s %s"),*MaskCar->Definition->VehicleName,*MaskCar->Definition->DriverName,Mode,*MaskCar->Definition->MaskName,MaskCar->IsMaskVisible()?TEXT("equipe"):TEXT("retire")),FColor(120,230,255),20,18); }
			if (!MaskCar->Modes->LastRefusal.IsEmpty()) { DrawText(MaskCar->Modes->LastRefusal,FColor(255,190,80),20,95); }
		}
		if(!Vehicle->VehicleSwitchStatus.IsEmpty()) { DrawText(Vehicle->VehicleSwitchStatus,FColor(255,190,80),20,115); }
		if (Vehicle->IsPauseMenuOpen())
		{
			DrawRect(FLinearColor(.015f,.025f,.04f,.96f),30,155,FMath::Min(1050.f,Canvas->SizeX-60.f),320);
			DrawText(Vehicle->IsPauseMenuOpen()?TEXT("PAUSE / MENU  —  A ou B : reprendre  |  Y : menu principal"):TEXT("COMMANDES XBOX"),FColor::White,50,172);
			const TCHAR* Rows[]={TEXT("RT / LT : accelerer / freiner ; en avion : regler la vitesse (minimum de vol)"),
				TEXT("Stick gauche : virer avec roulis ; haut/bas : cabrer / piquer"),TEXT("Stick droit : camera libre     Clic L3 : recentrer     Clic R3 : cockpit / exterieur"),
				TEXT("RB : tirer (maintenir)     Y : changer d'arme     Croix gauche/droite : armes 1/2"),
				TEXT("X : transformer en roulant ; en avion : atterrissage puis retour voiture automatiques"),
				TEXT("A : sortir du vehicule (a l'arret et au sol)     B : frein a main / piquer en avion"),
				TEXT("LB : frein a main     Croix haut/bas : vehicule IA suivant / precedent"),
				TEXT("L'IA reprend votre ancien vehicule     View (maintenir) : scores     Menu : pause/commandes")};
			for (int32 I=0;I<UE_ARRAY_COUNT(Rows);++I) { DrawText(Rows[I],FColor::White,50,205+I*30.f); }
			if(const auto* Mask=Cast<AThunderhawkPawn>(Vehicle);Mask && Mask->Definition)
			{
				if(Mask->Definition->VehicleName==TEXT("Hurricane"))
				{ DrawText(TEXT("Hurricane reste au sol. En combat : LB + Y projette la roue de secours (une seule fois)."),FColor(120,230,255),50,450); }
				else if(!Mask->Definition->bSupportsFlight)
				{ DrawText(TEXT("Rhino et son module restent au sol. X sur le module : retour au camion et rassemblement."),FColor(120,230,255),50,450); }
				else
				{
					const FString Help=Mask->Definition->Dynamics.FlightModel==EMaskFlightModel::Rotorcraft
						?TEXT("Helicoptere : LT jusqu'a vitesse nulle pour stationner ; stick haut/bas : monter/descendre ; X : poser.")
						:FString::Printf(TEXT("Avion : %.0f a %.0f km/h ; RT/LT reglent la vitesse ; X descend puis replie automatiquement."),Mask->Definition->Dynamics.MinimumAirspeedMPS*3.6f,Mask->Definition->Dynamics.MaximumAirspeedMPS*3.6f);
					DrawText(Help,FColor(120,230,255),50,450);
				}
			}
		}
	}
	if (bShowPlayerScores && GetWorld()->GetGameState())
	{
		const float X=FMath::Max(30.f,Canvas->SizeX-340.f);DrawRect(FLinearColor(0,0,0,.9f),X,180,310,230);
		DrawText(TEXT("JOUEURS / SCORES"),FColor::White,X+15,195);
		int32 Row=0;for (const auto& Entry:GetWorld()->GetGameState()->PlayerArray)
		{
			const auto* Player=Entry.Get();
			if (Player) { DrawText(FString::Printf(TEXT("%s   %.0f"),*Player->GetPlayerName(),Player->GetScore()),FColor::White,X+15,225+Row++*24.f); }
		}
	}
	if(const auto* Mission=ASilentValleyMission::Find(GetWorld());Mission && !(Driver && Driver->IsPauseMenuOpen()) && !(Vehicle && Vehicle->IsPauseMenuOpen()))
	{
		const float Width=FMath::Min(620.f,Canvas->SizeX-40.f),X=(Canvas->SizeX-Width)*.5f;
		DrawRect(FLinearColor(.01f,.02f,.035f,.85f),X,52,Width,104);
		DrawText(TEXT("OPERATION SILENT VALLEY"),FColor(120,230,255),X+14,62,nullptr,1.15f);
		DrawText(Mission->Objective(),FColor::White,X+14,89);
		const APawn* Pawn=GetOwningPlayerController()?GetOwningPlayerController()->GetPawn():nullptr;
		if(Mission->Phase==ESVPhase::Success) { DrawText(FString::Printf(TEXT("+%d composants techniques"),Mission->Reward),FColor(160,240,130),X+14,120); }
		else if(!Mission->IsTerminal() && Pawn)
		{
			DrawText(FString::Printf(TEXT("Objectif : %.0f m"),FVector::Dist2D(Pawn->GetActorLocation(),Mission->TargetLocation)/100),FColor(220,220,200),X+14,120);
			if(Mission->HoldProgress>0) { DrawRect(FLinearColor(.15f,.7f,.8f,1),X+180,123,(Width-200)*Mission->HoldProgress,8); }
			const FVector Pin=Project(Mission->Phase==ESVPhase::Combat && IsValid(Mission->Enemy)?Mission->Enemy->GetActorLocation()+FVector(0,0,220):Mission->TargetLocation+FVector(0,0,180));
			if(Pin.Z>0 && Pin.X>30 && Pin.X<Canvas->SizeX-140 && Pin.Y>175 && Pin.Y<Canvas->SizeY-100)
			{
				const auto* EnemyLife=IsValid(Mission->Enemy)?Mission->Enemy->FindComponentByClass<UHealthComponent>():nullptr;
				DrawText(Mission->Phase==ESVPhase::Combat && EnemyLife?FString::Printf(TEXT("ESCORTE : %.0f PV"),EnemyLife->CurrentHealth):TEXT("OBJECTIF"),FColor(255,210,105),Pin.X-45,Pin.Y);
			}
		}
	}
	const auto* Mode = GetWorld() ? Cast<ACustomGameMode>(GetWorld()->GetAuthGameMode()) : nullptr;
	if (!Canvas || !Mode || Mode->GetTrainingBotCount() == 0) { return; }
	if(!Driver) { DrawText(TEXT("ENTRAINEMENT SOLO"), FColor::White, 20.f, 48.f); }
	const APawn* Human = GetOwningPlayerController() ? GetOwningPlayerController()->GetPawn() : nullptr;
	const auto* HumanHealth = Human ? Human->FindComponentByClass<UHealthComponent>() : nullptr;
	if(!Driver) { DrawText(HumanHealth ? FString::Printf(TEXT("Vie : %d / %d"), FMath::CeilToInt(HumanHealth->CurrentHealth), FMath::CeilToInt(HumanHealth->MaxHealth))
		: TEXT("Vehicule detruit. Reapparition en cours..."), FColor::White, 20.f, 68.f);
	}
	for (TActorIterator<AVehicleBotController> It(GetWorld()); It; ++It)
	{
		const APawn* Bot = It->GetPawn();
		if (!Bot) { continue; }
		const auto* Health = Bot->FindComponentByClass<UHealthComponent>();
		const FVector Position = Project(Bot->GetActorLocation() + FVector(0,0,180));
		if (Position.Z > 0.f)
		{
			DrawText(FString::Printf(TEXT("BOT %d  %d PV"), It->TrainingIndex + 1, Health ? FMath::CeilToInt(Health->CurrentHealth) : 0), FColor(255,170,60), Position.X - 40.f, Position.Y);
		}
	}
}

void APlayerHUD::Initialize_Implementation()
{
}

void APlayerHUD::EnsureInitialized()
{
	if (!bWidgetsInitialized) { bWidgetsInitialized=true;Initialize(); }
}
void APlayerHUD::SetOnFootMode(bool Value)
{
	if(Value==bOnFootUI) { return; }bOnFootUI=Value;
	if(Value)
	{
		TArray<UUserWidget*> Widgets;UWidgetBlueprintLibrary::GetAllWidgetsOfClass(this,Widgets,UUserWidget::StaticClass(),false);
		for(auto* Widget:Widgets)
		{
			const FString Path=Widget->GetClass()->GetPathName();
			if(Path.StartsWith(TEXT("/Game/UI/WBP_PlayerUI.")) || Path.StartsWith(TEXT("/Game/UI/WBP_CarOutside.")) || Path.StartsWith(TEXT("/Game/UI/WBP_CarInside.")))
			{ VehicleWidgetVisibility.Add(Widget,static_cast<uint8>(Widget->GetVisibility()));Widget->SetVisibility(ESlateVisibility::Collapsed); }
		}
	}
	else { for(const auto& Entry:VehicleWidgetVisibility) { if(Entry.Key.IsValid()) { Entry.Key->SetVisibility(static_cast<ESlateVisibility>(Entry.Value)); } }VehicleWidgetVisibility.Reset(); }
}

void APlayerHUD::SetUIState_Implementation(bool bInCar)
{
}
void APlayerHUD::AddCrosshairRecoil_Implementation(float Recoil, float ControlTime)
{
}

void APlayerHUD::UpdateSpeedAndGear_Implementation(int32 Speed, int32 Gear)
{
}

void APlayerHUD::UpdateHealth_Implementation(float NewHealth)
{
}

void APlayerHUD::UpdateCurrentWeapon_Implementation(EWeaponName WeaponName)
{
}

void APlayerHUD::UpdateWeaponState_Implementation(EWeaponState WeaponState)
{
}

void APlayerHUD::UpdateAmmo_Implementation(int32 CurrentAmmo)
{
}

void APlayerHUD::UpdateMagAmmo_Implementation(int32 CurrentMagAmmo)
{
}

void APlayerHUD::PickupMessage_Implementation(EPickupType PickupType)
{
}
