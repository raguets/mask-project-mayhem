#pragma once
#include "CoreMinimal.h"
#include "Core/CustomGameMode.h"
#include "SilentValleyGameMode.generated.h"

/** Existing vehicle/controller/HUD behavior with deterministic starts only in this map. */
UCLASS()
class ASilentValleyGameMode : public ACustomGameMode
{
    GENERATED_BODY()
public:
    virtual void InitGame(const FString& MapName,const FString& Options,FString& Error) override;
    virtual void BeginPlay() override;
    virtual AActor* ChoosePlayerStart_Implementation(AController* Player) override;
private:
    bool bMissionEnabled=true;
    TMap<TWeakObjectPtr<AController>,int32> Slots;
};
