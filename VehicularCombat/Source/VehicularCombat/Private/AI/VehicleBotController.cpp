#include "AI/VehicleBotController.h"
#include "ChaosWheeledVehicleMovementComponent.h"
#include "Components/HealthComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerState.h"
#include "Pawns/PlayerWheeledVehiclePawn.h"
#include "MASK/RhinoPawn.h"
#include "MASK/MaskDriverCharacter.h"
#include "MASK/MaskVehicleDefinition.h"
#include "MASK/MaskVehicleModeComponent.h"

AVehicleBotController::AVehicleBotController()
{
    bWantsPlayerState=true;PrimaryActorTick.TickInterval=.1f;
}
void AVehicleBotController::OnPossess(APawn* InPawn)
{
    Super::OnPossess(InPawn);SetActorTickEnabled(true);StuckSeconds=ReverseUntil=0.f;
    NextShotAt=GetWorld()->GetTimeSeconds()+6.f+TrainingIndex*2.f;
    bCompanion=InPawn->IsA<ARhinoRearModule>();InPawn->SetActorTickEnabled(true);
    if(PlayerState)
    {
        const auto* Mask=Cast<AThunderhawkPawn>(InPawn);
        PlayerState->SetPlayerName(Mask && Mask->Definition?Mask->Definition->DriverName+TEXT(" (IA)"):FString::Printf(TEXT("Bot %d"),TrainingIndex+1));
    }
}
void AVehicleBotController::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);if(!HasAuthority()) { return; }
    auto* Vehicle=Cast<APlayerWheeledVehiclePawn>(GetPawn());if(!Vehicle) { return; }
    auto* Movement=Cast<UChaosWheeledVehicleMovementComponent>(Vehicle->GetVehicleMovement());
    const auto* Health=Vehicle->FindComponentByClass<UHealthComponent>();
    if(!Movement || !Health || Health->CurrentHealth<=0.f) { return; }
    auto* Pod=Cast<ARhinoRearModule>(Vehicle);
    if(Pod && !Pod->bDetached)
    {
        Movement->SetThrottleInput(0);Movement->SetBrakeInput(1);Vehicle->UpdateBotCombat(nullptr,false);return;
    }
    APawn* Target=nullptr;APawn* AllyHuman=nullptr;
    float Nearest=BIG_NUMBER;
    for(FConstPlayerControllerIterator It=GetWorld()->GetPlayerControllerIterator();It;++It)
    {
        APawn* Candidate=It->Get()?It->Get()->GetPawn():nullptr;
        const auto* Car=Cast<APlayerWheeledVehiclePawn>(Candidate);const auto* Driver=Cast<AMaskDriverCharacter>(Candidate);
        const auto* Life=Car?Car->FindComponentByClass<UHealthComponent>():nullptr;
        if((!Life || Life->CurrentHealth<=0.f) && (!Driver || Driver->Health<=0.f)) { continue; }
        const int32 Team=Car?Car->FleetTeamId:Driver->FleetTeamId;
        if(Team && Team==Vehicle->FleetTeamId) { AllyHuman=Candidate;continue; }
        const float Distance=FVector::DistSquared(Vehicle->GetActorLocation(),Candidate->GetActorLocation());
        if(Distance<Nearest) { Target=Candidate;Nearest=Distance; }
    }
    // When a human controls either half, its crew fights opposing AI vehicles.
    // Training opponents without an allied human retain their original human target.
    if(!Target && Vehicle->FleetTeamId!=0)
    {
        for(TActorIterator<APlayerWheeledVehiclePawn> It(GetWorld());It;++It)
        {
            const auto* Life=It->FindComponentByClass<UHealthComponent>();
            if(*It==Vehicle || !It->GetController() || !It->IsAvailableToSwitch() || Vehicle->IsAlliedWith(*It) || !Life || Life->CurrentHealth<=0.f) { continue; }
            const float Distance=FVector::DistSquared(Vehicle->GetActorLocation(),It->GetActorLocation());
            if(Distance<Nearest) { Target=*It;Nearest=Distance; }
        }
    }
    APawn* Follow=Pod && IsValid(Pod->ParentTruck)?static_cast<APawn*>(Pod->ParentTruck.Get()):AllyHuman;
    FVector Navigation;
    if(Follow)
    {
        if(Pod && Follow==Pod->ParentTruck && Pod->ParentTruck->Definition && !Pod->ParentTruck->Definition->RearModuleTrack.IsEmpty())
        {
            Navigation=Follow->GetActorTransform().TransformPosition(Pod->ParentTruck->CompanionOffset());
        }
        else if(const auto* Main=Cast<ARhinoPawn>(Vehicle);Main && Cast<ARhinoRearModule>(Follow) && Main->RearModule==Follow && !Main->Definition->RearModuleTrack.IsEmpty())
        {
            Navigation=Follow->GetActorTransform().TransformPosition(-Main->CompanionOffset());
        }
        else { Navigation=Follow->GetActorLocation()-Follow->GetActorForwardVector()*500.f+Follow->GetActorRightVector()*450.f; }
    }
    else if(Target) { Navigation=Target->GetActorLocation(); }
    else { Movement->SetThrottleInput(0);Movement->SetBrakeInput(1);Vehicle->UpdateBotCombat(nullptr,false);return; }
    const FVector Route=Navigation-Vehicle->GetActorLocation();const float Distance=Route.Size2D();
    const float Heading=FMath::FindDeltaAngleDegrees(Vehicle->GetActorRotation().Yaw,Route.Rotation().Yaw);
    const float StopDistance=Follow?(Follow->IsA<AMaskDriverCharacter>()?500.f:120.f):1600.f;const bool Approach=Distance>StopDistance;
    const float Speed=FMath::Abs(Movement->GetForwardSpeed());const float Now=GetWorld()->GetTimeSeconds();
    StuckSeconds=Approach && Speed<40.f?StuckSeconds+DeltaSeconds:0.f;
    if(StuckSeconds>3.f) { ReverseUntil=Now+1.4f;StuckSeconds=0.f; }
    // A close formation point can lie behind the rear axle. Back into it rather
    // than circling with full steering inside a truck-sized turning radius.
    const bool Reverse=Now<ReverseUntil || (Follow && Distance<1000.f && FMath::Abs(Heading)>100.f);
    if(auto* Mask=Cast<AThunderhawkPawn>(Vehicle);Mask && (Mask->IsNativeAircraft() || Mask->Modes->GetMode()==EMaskVehicleMode::Flight))
    {
        const bool Rotor=Mask->IsNativeAircraft() && Mask->Modes->GetMode()!=EMaskVehicleMode::Flight;
        const FVector Ref=Target?Target->GetActorLocation():Navigation;
        Mask->SetAIPilotInput(FVector(Approach?.35f:Rotor?-.6f:0.f,FMath::Clamp(Heading/45.f,-1.f,1.f),FMath::Clamp((Ref.Z+450.f-Vehicle->GetActorLocation().Z)/650.f,-.4f,.4f)));
    }
    Movement->SetHandbrakeInput(Follow && !Approach);Movement->SetTargetGear(Reverse?-1:1,true);
    const float TravelHeading=Reverse?FMath::FindDeltaAngleDegrees(Vehicle->GetActorRotation().Yaw+180.f,Route.Rotation().Yaw):Heading;
    Movement->SetSteeringInput(FMath::Clamp(TravelHeading/(Reverse?-45.f:45.f),-1.f,1.f));
    const float DesiredSpeed=Follow?FMath::Clamp(static_cast<float>(Follow->GetVelocity().Size2D())+Distance*.6f,80.f,4500.f):850.f;
    Movement->SetThrottleInput(Approach && Speed<DesiredSpeed?(Follow && Distance<800.f?.3f:.55f):0.f);
    Movement->SetBrakeInput(!Approach?1.f:Speed>DesiredSpeed+80.f?.65f:0.f);Vehicle->GetMesh()->WakeAllRigidBodies();
    bool Visible=false;
    if(Target)
    {
        FCollisionQueryParams Query(SCENE_QUERY_STAT(BotLineOfSight),false,Vehicle);TArray<AActor*> Attached;
        Vehicle->GetAttachedActors(Attached,true,true);Query.AddIgnoredActors(Attached);FHitResult Hit;
        const bool HitAnything=GetWorld()->LineTraceSingleByChannel(Hit,Vehicle->GetActorLocation()+FVector(0,0,100),Target->GetActorLocation()+FVector(0,0,40),ECC_Visibility,Query);
        Visible=!HitAnything || Hit.GetActor()==Target || (Hit.GetActor() && Hit.GetActor()->GetOwner()==Target);
    }
    const bool Shoot=Target && Visible && FVector::Dist2D(Vehicle->GetActorLocation(),Target->GetActorLocation())<4800.f && Now>=NextShotAt;
    Vehicle->UpdateBotCombat(Target,Shoot);if(Shoot) { NextShotAt=Now+8.f; }
}
