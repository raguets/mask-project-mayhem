#include "SilentValley/SilentValleyCheckpoint.h"
#include "Components/BoxComponent.h"
#include "Pawns/PlayerWheeledVehiclePawn.h"

ASilentValleyCheckpoint::ASilentValleyCheckpoint()
{
    Volume=CreateDefaultSubobject<UBoxComponent>(TEXT("CheckpointVolume"));SetRootComponent(Volume);Volume->SetBoxExtent(FVector(1500,1500,700));
    Volume->SetCollisionProfileName(TEXT("Trigger"));Volume->SetGenerateOverlapEvents(true);Volume->OnComponentBeginOverlap.AddDynamic(this,&ASilentValleyCheckpoint::Enter);
}
void ASilentValleyCheckpoint::BeginPlay() { Super::BeginPlay(); }
void ASilentValleyCheckpoint::Enter(UPrimitiveComponent*,AActor* Other,UPrimitiveComponent*,int32,bool,const FHitResult&)
{
    const auto* Vehicle=Cast<APlayerWheeledVehiclePawn>(Other);auto* Controller=Vehicle?Vehicle->GetController():nullptr;
    if(HasAuthority() && Controller && Controller->IsPlayerController() && !Seen.Contains(Controller))
    { Seen.Add(Controller);UE_LOG(LogTemp,Display,TEXT("SV_ROUTE_CHECKPOINT zone=%s index=%d vehicle=%s player=%s"),*ZoneName,ZoneIndex,*Vehicle->GetName(),*Controller->GetName()); }
}
