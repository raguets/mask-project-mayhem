#include "SilentValley/SilentValleyMission.h"
#include "SilentValley/SilentValleyCheckpoint.h"
#include "AI/VehicleBotController.h"
#include "MASK/MaskDriverCharacter.h"
#include "MASK/MaskVehicleDefinition.h"
#include "MASK/ThunderhawkPawn.h"
#include "Pawns/PlayerWheeledVehiclePawn.h"
#include "Components/HealthComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "ChaosWheeledVehicleMovementComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/GameModeBase.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Net/UnrealNetwork.h"
#include "UObject/ConstructorHelpers.h"

ASilentValleyMission::ASilentValleyMission()
{
    bReplicates=true;bAlwaysRelevant=true;SetReplicateMovement(true);PrimaryActorTick.bCanEverTick=true;PrimaryActorTick.TickInterval=.1f;
    Module=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("GuidanceModule"));SetRootComponent(Module);
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));Module->SetStaticMesh(Cube.Object);
    Module->SetWorldScale3D(FVector(.8f,.6f,.5f));Module->SetCollisionEnabled(ECollisionEnabled::NoCollision);
}
ASilentValleyMission* ASilentValleyMission::Find(UWorld* World)
{ if(World) { for(TActorIterator<ASilentValleyMission> It(World);It;++It) { return *It; } }return nullptr; }
void ASilentValleyMission::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME(ASilentValleyMission,Phase);DOREPLIFETIME(ASilentValleyMission,TargetZone);DOREPLIFETIME(ASilentValleyMission,TargetLocation);
    DOREPLIFETIME(ASilentValleyMission,HoldProgress);DOREPLIFETIME(ASilentValleyMission,bRewardSaved);DOREPLIFETIME(ASilentValleyMission,Reward);
    DOREPLIFETIME(ASilentValleyMission,RunId);DOREPLIFETIME(ASilentValleyMission,Enemy);
}
void ASilentValleyMission::BeginPlay()
{
    Super::BeginPlay();Module->SetVisibility(false);
    if(!HasAuthority()) { return; }
    Definition=LoadObject<USilentValleyMissionDefinition>(nullptr,TEXT("/Game/MASK/Missions/SilentValley/DA_SilentValley_01.DA_SilentValley_01"));
    if(!Definition) { Definition=NewObject<USilentValleyMissionDefinition>(this); }
    Zones.Init(FVector::ZeroVector,5);TSet<int32> Found;
    for(TActorIterator<ASilentValleyCheckpoint> It(GetWorld());It;++It) { if(Zones.IsValidIndex(It->ZoneIndex)) { Zones[It->ZoneIndex]=It->GetActorLocation();Found.Add(It->ZoneIndex); } }
    RunId=FGuid::NewGuid();Reward=Definition->TechReward;
    if(Found.Num()!=5) { Enter(ESVPhase::Failed,0);return; }
    SetActorLocation(Zones[3]+FVector(0,2000,100));Enter(ESVPhase::Briefing,0);
}
void ASilentValleyMission::Enter(ESVPhase Next,int32 Zone)
{
    if(!HasAuthority()) { return; }
    Phase=Next;TargetZone=Zone;TargetLocation=Zones.IsValidIndex(Zone)?Zones[Zone]:FVector::ZeroVector;PhaseAge=HoldProgress=0;
    if(Next==ESVPhase::Recover) { TargetLocation=GetActorLocation(); }
    if(Next==ESVPhase::Combat && EnemyController && IsValid(Enemy))
    { EnemyController->SetActorTickEnabled(true);Enemy->GetVehicleMovementComponent()->SetHandbrakeInput(false); }
    if(Next==ESVPhase::Success) { SaveReward(); }
    if(Next==ESVPhase::Failed && EnemyController) { EnemyController->SetActorTickEnabled(false);if(IsValid(Enemy)) { Enemy->UpdateBotCombat(nullptr,false); } }
    UE_LOG(LogTemp,Display,TEXT("SV_MISSION phase=%d zone=%d run=%s"),static_cast<int32>(Phase),Zone,*RunId.ToString());ForceNetUpdate();
}
bool ASilentValleyMission::AtTarget(APawn* Pawn) const
{
    return Pawn && FVector::Dist2D(Pawn->GetActorLocation(),TargetLocation)<(Phase==ESVPhase::Recover?1000.f:1500.f)
        && FMath::Abs(Pawn->GetActorLocation().Z-TargetLocation.Z)<700.f;
}
bool ASilentValleyMission::SpawnEscort()
{
    // Existing sedan is a temporary escort representation, not a new V.E.N.O.M. art asset.
    auto* Class=LoadClass<APlayerWheeledVehiclePawn>(nullptr,TEXT("/Game/Blueprints/Pawns/BP_PlayerVehicle.BP_PlayerVehicle_C"));
    if(!Class) { return false; }
    FVector Position=Zones[3]+FVector(1800,2800,300);FHitResult Ground;
    FCollisionQueryParams Query(SCENE_QUERY_STAT(SVEscortGround),false);
    if(!GetWorld()->LineTraceSingleByChannel(Ground,Position+FVector(0,0,1000),Position-FVector(0,0,2000),ECC_Visibility,Query) || Ground.ImpactNormal.Z<.95f) { return false; }
    Position.Z=Ground.ImpactPoint.Z+100;
    for(FConstPlayerControllerIterator It=GetWorld()->GetPlayerControllerIterator();It;++It)
    { if(It->Get() && It->Get()->GetPawn() && FVector::Dist2D(It->Get()->GetPawn()->GetActorLocation(),Position)<20000) { return false; } }
    FActorSpawnParameters Params;Params.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::DontSpawnIfColliding;
    Enemy=GetWorld()->SpawnActor<APlayerWheeledVehiclePawn>(Class,Position,FRotator(0,180,0),Params);
    if(!Enemy) { return false; }
    const auto* PC=GetWorld()->GetFirstPlayerController();
    const auto* Player=PC?Cast<APlayerWheeledVehiclePawn>(PC->GetPawn()):nullptr;
    Enemy->FleetTeamId=Player && Player->FleetTeamId==2?1:2;EnemyController=GetWorld()->SpawnActor<AVehicleBotController>();
    if(!EnemyController) { Enemy->Destroy();Enemy=nullptr;return false; }
    EnemyController->Possess(Enemy);EnemyController->SetActorTickEnabled(false);
    Enemy->GetVehicleMovementComponent()->SetHandbrakeInput(true);Enemy->GetVehicleMovementComponent()->SetBrakeInput(1);
    return true;
}
void ASilentValleyMission::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);Module->SetVisibility(Phase==ESVPhase::Recover);
    if(!HasAuthority() || !Definition) { return; }
    if(IsTerminal()) { if(Phase==ESVPhase::Success && !bRewardSaved && (SaveRetrySeconds+=DeltaSeconds)>1) { SaveRetrySeconds=0;SaveReward(); }return; }
    PhaseAge+=DeltaSeconds;bool Arrived=false,Stopped=false,Alive=false;int32 Players=0;
    for(FConstPlayerControllerIterator It=GetWorld()->GetPlayerControllerIterator();It;++It)
    {
        auto* PC=It->Get();APawn* Pawn=PC?PC->GetPawn():nullptr;if(!PC) { continue; }++Players;
        const auto* Life=Pawn?Pawn->FindComponentByClass<UHealthComponent>():nullptr;const auto* Driver=Cast<AMaskDriverCharacter>(Pawn);
        const bool Healthy=(Life && Life->CurrentHealth>0) || (Driver && Driver->Health>0);Alive|=Healthy;
        if(auto* Car=Cast<APlayerWheeledVehiclePawn>(Pawn)) { const auto* Def=Car->GetDriverDefinition();Car->FleetTeamId=Def?static_cast<int32>(Def->Faction):1; }
        if(Healthy && AtTarget(Pawn)) { Arrived=true;Stopped|=Pawn->GetVelocity().Size()<100; }
    }
    AllDownSeconds=Players>0 && !Alive?AllDownSeconds+DeltaSeconds:0;
    if(AllDownSeconds>2.f) { Enter(ESVPhase::Failed,TargetZone);return; }
    if(Phase==ESVPhase::Briefing) { if(PhaseAge>=Definition->BriefingSeconds && Alive) { Enter(ESVPhase::Departure,0); } }
    else if(Phase==ESVPhase::Departure && Arrived) { Enter(ESVPhase::Travel,1); }
    else if(Phase==ESVPhase::Travel && Arrived) { Enter(TargetZone==1?ESVPhase::Travel:ESVPhase::Recon,2); }
    else if(Phase==ESVPhase::Recon && PhaseAge>=Definition->ReconSeconds)
    { if(SpawnEscort()) { Enter(ESVPhase::Intercept,3); }else { Enter(ESVPhase::Failed,3); } }
    else if(Phase==ESVPhase::Intercept || Phase==ESVPhase::Combat)
    {
        const auto* Life=IsValid(Enemy)?Enemy->FindComponentByClass<UHealthComponent>():nullptr;
        if(!Life || Life->CurrentHealth<=0) { Enter(ESVPhase::Recover,3); }
        else if(Phase==ESVPhase::Intercept && Arrived) { Enter(ESVPhase::Combat,3); }
    }
    else if(Phase==ESVPhase::Recover || Phase==ESVPhase::Extract)
    {
        const float Duration=Phase==ESVPhase::Recover?Definition->RecoverySeconds:Definition->ExtractionSeconds;
        HoldProgress=Stopped?FMath::Clamp(HoldProgress+DeltaSeconds/FMath::Max(.1f,Duration),0.f,1.f):0;
        if(HoldProgress>=1) { Enter(Phase==ESVPhase::Recover?ESVPhase::Extract:ESVPhase::Success,4); }
    }
}
void ASilentValleyMission::SaveReward()
{
    if(!HasAuthority() || Phase!=ESVPhase::Success || bRewardSaved) { return; }
    FString Slot=TEXT("MASK_SilentValley_Progress");FParse::Value(FCommandLine::Get(),TEXT("SVMissionSaveSlot="),Slot);
    auto* Progress=Cast<USilentValleyProgress>(UGameplayStatics::LoadGameFromSlot(Slot,0));
    if(!Progress) { Progress=Cast<USilentValleyProgress>(UGameplayStatics::CreateSaveGameObject(USilentValleyProgress::StaticClass())); }
    if(!Progress->RewardedRuns.Contains(RunId)) { Progress->TechComponents+=Reward;Progress->RewardedRuns.Add(RunId);if(Progress->RewardedRuns.Num()>64) { Progress->RewardedRuns.RemoveAt(0); } }
    bRewardSaved=UGameplayStatics::SaveGameToSlot(Progress,Slot,0);ForceNetUpdate();
}
void ASilentValleyMission::Retry(APlayerController* Requester)
{
    if(!HasAuthority() || !Requester || !IsTerminal() || bRestartQueued) { return; }bRestartQueued=true;
    FString Vehicle=TEXT("Thunderhawk");const auto* Driver=Cast<AMaskDriverCharacter>(Requester->GetPawn());
    const auto* Car=Driver?Cast<AThunderhawkPawn>(Driver->SourceVehicle):Cast<AThunderhawkPawn>(Requester->GetPawn());
    if(Car && Car->Definition) { Vehicle=Car->Definition->VehicleName; }
    if(Vehicle!=TEXT("Rhino") && Vehicle!=TEXT("Hurricane") && Vehicle!=TEXT("Raven") && Vehicle!=TEXT("Condor") && Vehicle!=TEXT("Switchblade")) { Vehicle=TEXT("Thunderhawk"); }
    // Recreate the configured companion fleet, including an explicit solo run.
    const auto* GameMode=GetWorld()->GetAuthGameMode();
    const int32 Bots=FMath::Clamp(UGameplayStatics::GetIntOption(GameMode?GameMode->OptionsString:FString(),TEXT("Bots"),0),0,6);
    GetWorld()->ServerTravel(FString::Printf(TEXT("/Game/MASK/Maps/SilentValley/L_SilentValley_Blockout?Vehicle=%s?Bots=%d"),*Vehicle,Bots)+(GetNetMode()==NM_ListenServer?TEXT("?listen"):TEXT("")));
}
FString ASilentValleyMission::Objective() const
{
    switch(Phase)
    {
    case ESVPhase::Briefing:return TEXT("Recupere le module de guidage de V.E.N.O.M.");
    case ESVPhase::Departure:return TEXT("Quitte Boulder Hill et rejoins la route");
    case ESVPhase::Travel:return TargetZone==1?TEXT("Rejoins Pinewood Road"):TEXT("Rejoins le belvedere d'Eagle Pass");
    case ESVPhase::Recon:return TEXT("Reconnaissance de la carriere en cours...");
    case ESVPhase::Intercept:return TEXT("Intercepte l'escorte a Old Quarry");
    case ESVPhase::Combat:return TEXT("Neutralise l'escorte — RB pour tirer");
    case ESVPhase::Recover:return TEXT("Arrete-toi pres du module pour le recuperer");
    case ESVPhase::Extract:return TEXT("Rejoins North Ridge et immobilise-toi pour extraire");
    case ESVPhase::Success:return bRewardSaved?TEXT("Mission reussie — X / F6 : rejouer, retour au QG libre"):TEXT("Mission reussie — sauvegarde de la recompense...");
    default:return TEXT("Mission echouee — X / F6 : recommencer");
    }
}
