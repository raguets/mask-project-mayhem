#include "CoreMinimal.h"

#if !UE_BUILD_SHIPPING
#include "AI/VehicleBotController.h"
#include "Actors/ProjectileActor.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Button.h"
#include "Components/CheckBox.h"
#include "Components/EditableText.h"
#include "Components/HealthComponent.h"
#include "Components/TextBlock.h"
#include "Containers/Ticker.h"
#include "Core/OnlineGameInstance.h"
#include "Dom/JsonObject.h"
#include "Engine/Engine.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerState.h"
#include "HAL/FileManager.h"
#include "HAL/IConsoleManager.h"
#include "InputKeyEventArgs.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "OnlineSubsystemUtils.h"
#include "OnlineSessionSettings.h"
#include "Pawns/PlayerWheeledVehiclePawn.h"
#include "Serialization/JsonSerializer.h"
#include "UI/MainMenuWidget.h"
#include "UnrealClient.h"

namespace VCTrainingTest
{
class FRun
{
public:
	FString Directory;
	TSharedRef<FJsonObject> Report = MakeShared<FJsonObject>();
	TSharedRef<FJsonObject> Checks = MakeShared<FJsonObject>();
	int32 Phase = 0, BotProjectiles = 0, PlayerProjectiles = 0;
	double Started = FPlatformTime::Seconds(), PhaseStarted = Started;
	float MinHumanHealth = BIG_NUMBER;
	TMap<TWeakObjectPtr<AVehicleBotController>, FVector> InitialPositions;
	TWeakObjectPtr<AVehicleBotController> VictimController;
	TWeakObjectPtr<APawn> OldVictim;

	FRun()
	{
		FParse::Value(FCommandLine::Get(), TEXT("MigrationReportDir="), Directory);
		if (Directory.IsEmpty()) { Directory = FPaths::ProjectSavedDir() / TEXT("Migration/training"); }
		IFileManager::Get().MakeDirectory(*Directory, true);
		Report->SetObjectField(TEXT("checks"), Checks);
		Report->SetStringField(TEXT("method"), TEXT("One real game process; original Blueprint menu and native UMG button delegates; real Chaos AI inputs, projectiles and health. Separate explicit death injection verifies bot respawn."));
	}
	void Stage(int32 Value) { Phase = Value; PhaseStarted = FPlatformTime::Seconds(); UE_LOG(LogTemp, Display, TEXT("VC_TRAINING_TEST phase=%d"), Phase); }
	void Check(const TCHAR* Name, bool Value) { Checks->SetBoolField(Name, Value); }
	void Save(bool Complete)
	{
		bool Passed = Complete && Checks->Values.Num() >= 15;
		for (const auto& Pair : Checks->Values) { Passed &= Pair.Value->AsBool(); }
		Report->SetBoolField(TEXT("passed"), Passed); Report->SetBoolField(TEXT("complete"), Complete);
		Report->SetNumberField(TEXT("phase"), Phase); Report->SetNumberField(TEXT("elapsed_seconds"), FPlatformTime::Seconds() - Started);
		Report->SetNumberField(TEXT("bot_projectiles"), BotProjectiles); Report->SetNumberField(TEXT("player_projectiles"), PlayerProjectiles);
		Report->SetNumberField(TEXT("min_human_health"), MinHumanHealth);
		FString Json; FJsonSerializer::Serialize(Report, TJsonWriterFactory<>::Create(&Json));
		FFileHelper::SaveStringToFile(Json, *(Directory / TEXT("training.json")));
	}
	bool Finish(bool Timeout = false)
	{
		Check(TEXT("completed_without_timeout"), !Timeout); Save(true);
		FPlatformMisc::RequestExit(false); return false;
	}
	void Shot(const TCHAR* File)
	{
		if (!FParse::Param(FCommandLine::Get(), TEXT("NullRHI"))) { FScreenshotRequest::RequestScreenshot(Directory / File, true, false); }
	}
	static void Key(APlayerController* PC, FKey KeyValue, bool Down)
	{
		PC->InputKey(FInputKeyEventArgs(nullptr, FInputDeviceId::CreateFromInternalId(0), KeyValue, Down ? IE_Pressed : IE_Released, Down ? 1.f : 0.f, false, FPlatformTime::Cycles64()));
	}
	static UMainMenuWidget* Menu(UWorld* World)
	{
		for (TObjectIterator<UMainMenuWidget> It; It; ++It) { if (It->GetWorld() == World && It->IsInViewport()) { return *It; } }
		return nullptr;
	}
	bool Tick(float)
	{
		static auto* FPS = IConsoleManager::Get().FindConsoleVariable(TEXT("t.MaxFPS"));
		if (FPS && FPS->GetFloat() != 30.f) { FPS->Set(30.f, ECVF_SetByConsole); }
		if (FPlatformTime::Seconds() - Started > 100) { return Finish(true); }
		UWorld* World = nullptr;
		for (const FWorldContext& Context : GEngine->GetWorldContexts()) { if (Context.WorldType == EWorldType::Game) { World = Context.World(); break; } }
		if (!World) { return true; }
		auto* GI = Cast<UOnlineGameInstance>(World->GetGameInstance());
		auto* PC = World->GetFirstPlayerController();
		auto* Human = PC ? Cast<APlayerWheeledVehiclePawn>(PC->GetPawn()) : nullptr;
		const auto Age = [this]() { return FPlatformTime::Seconds() - PhaseStarted; };
		if (!GI || !PC) { return true; }
		if (Phase == 0 && Age() > 2)
		{
			if (auto* Frontend = Menu(World))
			{
				Check(TEXT("original_menu_has_native_extension"), true);
				Check(TEXT("solo_button_present"), Frontend->GetWidgetFromName(TEXT("PlaySoloButton")) != nullptr);
				bool NameReady = false; UButton* Join = nullptr;
				Frontend->WidgetTree->ForEachWidgetAndDescendants([&](UWidget* Widget)
				{
					if (auto* Text = Cast<UEditableText>(Widget); Text && Text->GetHintText().ToString().Contains(TEXT("Session"))) { NameReady |= !Text->GetText().IsEmpty(); }
					if (auto* Button = Cast<UButton>(Widget))
					{
						if (auto* Label = Cast<UTextBlock>(Button->GetChildAt(0)); Label && Label->GetText().ToString() == TEXT("Join")) { Join = Button; }
					}
				});
				Check(TEXT("host_name_prefilled"), NameReady); Check(TEXT("original_join_button_present"), Join != nullptr);
				if (!Join) { return Finish(); }
				Join->OnClicked.Broadcast(); Stage(1);
			}
		}
		if (Phase == 1 && (GI->FrontendStatus.ToString().Contains(TEXT("Aucune partie")) || Age() > 12))
		{
			Check(TEXT("empty_lan_search_explains_result"), GI->FrontendStatus.ToString().Contains(TEXT("Aucune partie")));
			Shot(TEXT("menu-empty-search.png")); Stage(2);
		}
		if (Phase == 2 && Age() > 0.3)
		{
			if (auto* Frontend = Menu(World))
			{
				if (auto* Vehicle=Cast<UCheckBox>(Frontend->GetWidgetFromName(TEXT("ThunderhawkSelection"))))
				{
					const bool Selected=FParse::Param(FCommandLine::Get(),TEXT("MaskThunderhawk"));
					Vehicle->SetIsChecked(Selected);Vehicle->OnCheckStateChanged.Broadcast(Selected);
					if (Selected) { Check(TEXT("thunderhawk_selection_present"),true); }
				}
				if (auto* Solo = Cast<UButton>(Frontend->GetWidgetFromName(TEXT("PlaySoloButton")))) { Solo->OnClicked.Broadcast(); Stage(3); }
			}
		}
		if (Phase == 3 && Human && World->GetTimeSeconds() > 4.f)
		{
			int32 Count = 0; bool Possessed = true, States = true;
			for (TActorIterator<AVehicleBotController> It(World); It; ++It)
			{
				if(It->bCompanion) { continue; }
				++Count; Possessed &= It->GetPawn() && It->GetPawn()->GetController() == *It;
				States &= It->PlayerState != nullptr;
				if (It->GetPawn()) { InitialPositions.Add(*It, It->GetPawn()->GetActorLocation()); }
			}
			Check(TEXT("solo_map_loaded"), World->GetOutermost()->GetName() == TEXT("/Game/Maps/TestMaps/Test"));
			Check(TEXT("human_vehicle_controllable"), Human->IsLocallyControlled());
			Check(TEXT("three_bots_spawned"), Count == 3); Check(TEXT("bots_possess_real_vehicles"), Possessed); Check(TEXT("bots_have_player_states"), States);
			Check(TEXT("solo_has_no_network_session"), World->GetNetMode() == NM_Standalone && !Online::GetSessionInterface(World)->GetNamedSession(NAME_GameSession));
			Key(PC, EKeys::Two, true); Key(PC, EKeys::Two, false);
			World->AddOnActorSpawnedHandler(FOnActorSpawned::FDelegate::CreateLambda([this](AActor* Actor)
			{
				if (!Actor->IsA<AProjectileActor>()) { return; }
				if (auto* Owner = Cast<APawn>(Actor->GetOwner()))
				{
					if (Cast<AVehicleBotController>(Owner->GetController())) { ++BotProjectiles; }
					else if (Owner->IsPlayerControlled()) { ++PlayerProjectiles; }
				}
			}));
			Stage(4);
		}
		if (Phase == 4 && Human)
		{
			if (const auto* Health = Human->FindComponentByClass<UHealthComponent>()) { MinHumanHealth = FMath::Min(MinHumanHealth, Health->CurrentHealth); }
			if (Age() > 12)
			{
				bool Moved = InitialPositions.Num() == 3;
				for (const auto& Pair : InitialPositions)
				{
					Moved &= Pair.Key.IsValid() && Pair.Key->GetPawn() && FVector::Dist2D(Pair.Key->GetPawn()->GetActorLocation(), Pair.Value) > 100.f;
					if (!VictimController.IsValid()) { VictimController = Pair.Key; }
				}
				Check(TEXT("bots_drive_with_chaos"), Moved); Check(TEXT("bots_fire_original_projectiles"), BotProjectiles > 0);
				Check(TEXT("bot_projectiles_damage_human"), MinHumanHealth < 1000.f);
				Shot(TEXT("solo-combat.png"));
				Key(PC, EKeys::LeftMouseButton, true); Stage(5);
			}
		}
		if (Phase == 5 && Age() > 0.4 && Human)
		{
			Key(PC, EKeys::LeftMouseButton, false); Check(TEXT("human_fire_input_spawns_projectile"), PlayerProjectiles > 0);
			if (VictimController.IsValid())
			{
				OldVictim = VictimController->GetPawn();
				UGameplayStatics::ApplyDamage(OldVictim.Get(), 100000.f, PC, Human, UDamageType::StaticClass());
			}
			Stage(6);
		}
		if (Phase == 6 && Age() > 7)
		{
			APawn* Replacement = VictimController.IsValid() ? VictimController->GetPawn() : nullptr;
			const auto* Health = Replacement ? Replacement->FindComponentByClass<UHealthComponent>() : nullptr;
			Check(TEXT("destroyed_bot_respawns"), !OldVictim.IsValid() && Replacement && Health && Health->CurrentHealth == Health->MaxHealth);
			Key(PC, EKeys::F10, true); Stage(7);
		}
		if (Phase == 7 && Age() > 2)
		{
			if (auto* Frontend = Menu(World))
			{
				Check(TEXT("f10_returns_to_menu"), true);
				if (auto* Solo = Cast<UButton>(Frontend->GetWidgetFromName(TEXT("PlaySoloButton")))) { Solo->OnClicked.Broadcast(); Stage(8); }
			}
		}
		if (Phase == 8 && Human && World->GetTimeSeconds() > 4.f)
		{
			int32 Count = 0; for (TActorIterator<AVehicleBotController> It(World); It; ++It) { if (It->GetPawn() && !It->bCompanion) { ++Count; } }
			Check(TEXT("solo_can_be_restarted_without_duplicate_bots"), Count == 3);
			return Finish();
		}
		Save(false); return true;
	}
};
TUniquePtr<FRun> Runner;
FAutoConsoleCommand Command(TEXT("VC.TrainingSmoke"), TEXT("Opt-in end-to-end training/menu integration test."), FConsoleCommandDelegate::CreateLambda([]()
{
	if (Runner) { return; }
	Runner = MakeUnique<FRun>();
	FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda([](float Delta) { return Runner->Tick(Delta); }));
}));
}
#endif
