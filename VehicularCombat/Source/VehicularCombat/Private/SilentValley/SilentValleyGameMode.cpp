#include "SilentValley/SilentValleyGameMode.h"
#include "SilentValley/SilentValleyMission.h"
#include "GameFramework/PlayerStart.h"
#include "EngineUtils.h"
#include "Kismet/GameplayStatics.h"

void ASilentValleyGameMode::InitGame(const FString& MapName,const FString& Options,FString& Error)
{
    bMissionEnabled=UGameplayStatics::ParseOption(Options,TEXT("Mission"))!=TEXT("0");
    const FString Actual=UGameplayStatics::ParseOption(Options,TEXT("Vehicle")).IsEmpty()?Options+TEXT("?Vehicle=Thunderhawk"):Options;
    Super::InitGame(MapName,Actual,Error);
}
void ASilentValleyGameMode::BeginPlay()
{
    Super::BeginPlay();if(bMissionEnabled && !ASilentValleyMission::Find(GetWorld())) { GetWorld()->SpawnActor<ASilentValleyMission>(); }
}
AActor* ASilentValleyGameMode::ChoosePlayerStart_Implementation(AController* Player)
{
    if(!Player || !Player->IsPlayerController()) { return Super::ChoosePlayerStart_Implementation(Player); }
    if(!Slots.Contains(Player)) { Slots.Add(Player,Slots.Num()%3); }
    const FName Tag(*FString::Printf(TEXT("SV_Start%d"),Slots[Player]));
    for(TActorIterator<APlayerStart> It(GetWorld());It;++It) { if(It->PlayerStartTag==Tag) { return *It; } }
    return Super::ChoosePlayerStart_Implementation(Player);
}
