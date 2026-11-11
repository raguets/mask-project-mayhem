#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SilentValleyCheckpoint.generated.h"

/** Route observation volume. No mission success is inferred from its mere presence. */
UCLASS()
class ASilentValleyCheckpoint : public AActor
{
    GENERATED_BODY()
public:
    ASilentValleyCheckpoint();
    virtual void BeginPlay() override;
    UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<class UBoxComponent> Volume;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) FString ZoneName;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) int32 ZoneIndex=0;
private:
    TSet<TWeakObjectPtr<AController>> Seen;
    UFUNCTION() void Enter(UPrimitiveComponent* Component,AActor* Other,UPrimitiveComponent* OtherComponent,int32 BodyIndex,bool bSweep,const FHitResult& Hit);
};
