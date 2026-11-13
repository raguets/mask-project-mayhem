#include "SilentValley/SilentValleyGameMode.h"
#include "SilentValley/SilentValleyMission.h"
#include "SilentValley/SilentValleyRoad.h"
#include "MASK/SwitchbladePawn.h"
#include "Engine/StaticMeshActor.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "GameFramework/PlayerStart.h"
#include "EngineUtils.h"
#include "Kismet/GameplayStatics.h"

void ASilentValleyGameMode::InitGame(const FString& MapName,const FString& Options,FString& Error)
{
    bMissionEnabled=UGameplayStatics::ParseOption(Options,TEXT("Mission"))!=TEXT("0");
    FString Actual=UGameplayStatics::ParseOption(Options,TEXT("Vehicle")).IsEmpty()?Options+TEXT("?Vehicle=Thunderhawk"):Options;
    if(!UGameplayStatics::HasOption(Actual,TEXT("Bots"))) { Actual+=TEXT("?Bots=5"); }
    Super::InitGame(MapName,Actual,Error);
}
bool ASilentValleyGameMode::FindNativeAircraftStart(FTransform& Transform) const
{
    FCollisionQueryParams Query(SCENE_QUERY_STAT(SwitchbladeExteriorStart),false);
    for(TActorIterator<APawn> It(GetWorld());It;++It) { Query.AddIgnoredActor(*It); }
    TArray<FBox> Bases;
    for(TActorIterator<AStaticMeshActor> It(GetWorld());It;++It)
    {
        const UStaticMesh* Mesh=It->GetStaticMeshComponent()->GetStaticMesh();
        if(Mesh && Mesh->GetPathName().Contains(TEXT("BoulderHill")))
        { FVector Origin,Extent;It->GetActorBounds(true,Origin,Extent);Bases.Add(FBox(Origin-Extent,Origin+Extent).ExpandBy(FVector(1000,1000,0))); }
    }
    for(TActorIterator<ASilentValleyRoad> Road(GetWorld());Road;++Road)
    {
        for(float Distance=15000.f;Distance<90000.f;Distance+=2000.f)
        {
            FVector P=Road->RouteLocation(Distance);const FRotator Rotation(0,Road->RouteRotation(Distance).Yaw,0);
            bool Safe=true;float Low=BIG_NUMBER,High=-BIG_NUMBER;
            for(const FBox& Base:Bases) { if(P.X>Base.Min.X && P.X<Base.Max.X && P.Y>Base.Min.Y && P.Y<Base.Max.Y) { Safe=false; } }
            if(!Safe) { continue; }
            for(FVector Offset:{FVector::ZeroVector,FVector(300,110,0),FVector(300,-110,0),FVector(-300,110,0),FVector(-300,-110,0)})
            {
                Offset=Rotation.RotateVector(Offset);FHitResult Hit;
                if(!GetWorld()->LineTraceSingleByChannel(Hit,P+Offset+FVector(0,0,3000),P+Offset-FVector(0,0,3000),ECC_Vehicle,Query) || Hit.ImpactNormal.Z<.98f) { Safe=false;break; }
                Low=FMath::Min(Low,static_cast<float>(Hit.ImpactPoint.Z));High=FMath::Max(High,static_cast<float>(Hit.ImpactPoint.Z));
            }
            if(!Safe || High-Low>30.f) { continue; }
            P.Z=High+100.f;
            for(TActorIterator<APawn> It(GetWorld());It;++It) { if(FVector::Dist2D(P,It->GetActorLocation())<1500.f) { Safe=false; } }
            if(!Safe || GetWorld()->OverlapBlockingTestByChannel(P+FVector(0,0,250),Rotation.Quaternion(),ECC_Vehicle,FCollisionShape::MakeBox(FVector(450,450,175)),Query)) { continue; }
            Transform=FTransform(Rotation,P);return true;
        }
    }
    return false;
}
void ASilentValleyGameMode::RestartPlayer(AController* Player)
{
    UClass* Class=Player?GetDefaultPawnClassForController(Player):nullptr;
    if(Class && Class->IsChildOf(ASwitchbladePawn::StaticClass()))
    {
        FTransform Outside;
        if(!FindNativeAircraftStart(Outside)) { UE_LOG(LogTemp,Error,TEXT("SWITCHBLADE_START no safe exterior takeoff site; garage fallback prohibited"));return; }
        RestartPlayerAtTransform(Player,Outside);
        UE_LOG(LogTemp,Display,TEXT("SWITCHBLADE_START exterior=%s pawn=%s"),*Outside.GetLocation().ToString(),*GetNameSafe(Player->GetPawn()));return;
    }
    Super::RestartPlayer(Player);
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
