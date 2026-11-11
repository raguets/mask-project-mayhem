#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Engine/DataAsset.h"
#include "GameFramework/SaveGame.h"
#include "SilentValleyMission.generated.h"

UENUM(BlueprintType)
enum class ESVPhase:uint8 { Briefing,Departure,Travel,Recon,Intercept,Combat,Recover,Extract,Success,Failed };

UCLASS(BlueprintType)
class USilentValleyMissionDefinition:public UDataAsset
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere) float BriefingSeconds=4.f;
    UPROPERTY(EditAnywhere) float ReconSeconds=3.f;
    UPROPERTY(EditAnywhere) float RecoverySeconds=3.f;
    UPROPERTY(EditAnywhere) float ExtractionSeconds=2.f;
    UPROPERTY(EditAnywhere) int32 TechReward=25;
};

UCLASS()
class USilentValleyProgress:public USaveGame
{
    GENERATED_BODY()
public:
    UPROPERTY(SaveGame) int32 TechComponents=0;
    UPROPERTY(SaveGame) TArray<FGuid> RewardedRuns;
};

/** Server-owned first mission slice. Existing vehicles, AI, weapons and HUD. */
UCLASS()
class ASilentValleyMission:public AActor
{
    GENERATED_BODY()
public:
    ASilentValleyMission();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Props) const override;
    static ASilentValleyMission* Find(UWorld* World);
    bool IsTerminal() const { return Phase==ESVPhase::Success || Phase==ESVPhase::Failed; }
    void Retry(class APlayerController* Requester);
    FString Objective() const;
    UPROPERTY(Replicated,BlueprintReadOnly) ESVPhase Phase=ESVPhase::Briefing;
    UPROPERTY(Replicated,BlueprintReadOnly) int32 TargetZone=0;
    UPROPERTY(Replicated,BlueprintReadOnly) FVector TargetLocation=FVector::ZeroVector;
    UPROPERTY(Replicated,BlueprintReadOnly) float HoldProgress=0;
    UPROPERTY(Replicated,BlueprintReadOnly) bool bRewardSaved=false;
    UPROPERTY(Replicated,BlueprintReadOnly) int32 Reward=0;
    UPROPERTY(Replicated,BlueprintReadOnly) FGuid RunId;
    UPROPERTY(Replicated,BlueprintReadOnly) TObjectPtr<class APlayerWheeledVehiclePawn> Enemy;
    UPROPERTY(VisibleAnywhere) TObjectPtr<class UStaticMeshComponent> Module;
private:
    UPROPERTY() TObjectPtr<USilentValleyMissionDefinition> Definition;
    UPROPERTY() TObjectPtr<class AVehicleBotController> EnemyController;
    TArray<FVector> Zones;
    float PhaseAge=0,AllDownSeconds=0,SaveRetrySeconds=0;
    bool bRestartQueued=false;
    void Enter(ESVPhase Next,int32 Zone);
    bool AtTarget(class APawn* Pawn) const;
    bool SpawnEscort();
    void SaveReward();
};
