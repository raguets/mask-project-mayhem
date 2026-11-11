#include "MASK/RhinoPawn.h"
#include "MASK/MaskDriverCharacter.h"
#include "MASK/MaskVehicleDefinition.h"
#include "MASK/MaskVehicleModeComponent.h"
#include "AI/VehicleBotController.h"
#include "Core/CustomGameMode.h"
#include "ChaosWheeledVehicleMovementComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "Net/UnrealNetwork.h"

URhinoFrontWheel::URhinoFrontWheel()
{
    WheelRadius=58.f;WheelWidth=34.f;MaxSteerAngle=35.f;bAffectedBySteering=true;
    MaxBrakeTorque=20000.f;
    SuspensionMaxRaise=12.f;SuspensionMaxDrop=20.f;SpringRate=1100.f;SpringPreload=250.f;
    SuspensionDampingRatio=.7f;FrictionForceMultiplier=1.15f;
}
URhinoRearWheel::URhinoRearWheel()
{
    WheelRadius=58.f;WheelWidth=29.f;MaxSteerAngle=0.f;bAffectedBySteering=false;
    bAffectedByEngine=true;bAffectedByHandbrake=true;
    MaxBrakeTorque=20000.f;MaxHandBrakeTorque=30000.f;
    SuspensionMaxRaise=12.f;SuspensionMaxDrop=20.f;SpringRate=1100.f;SpringPreload=250.f;
    SuspensionDampingRatio=.7f;FrictionForceMultiplier=1.15f;
}
URhinoPodFrontWheel::URhinoPodFrontWheel()
{
    WheelRadius=58.f;WheelWidth=29.f;MaxSteerAngle=35.f;bAffectedBySteering=true;
    MaxBrakeTorque=5000.f;
    SuspensionMaxRaise=8.f;SuspensionMaxDrop=12.f;SpringRate=250.f;SpringPreload=50.f;
    SuspensionDampingRatio=.7f;FrictionForceMultiplier=1.15f;
}
URhinoPodRearWheel::URhinoPodRearWheel()
{
    WheelRadius=58.f;WheelWidth=29.f;MaxSteerAngle=0.f;bAffectedBySteering=false;
    bAffectedByEngine=true;bAffectedByHandbrake=true;
    MaxBrakeTorque=5000.f;MaxHandBrakeTorque=10000.f;
    SuspensionMaxRaise=8.f;SuspensionMaxDrop=12.f;SpringRate=250.f;SpringPreload=50.f;
    SuspensionDampingRatio=.7f;FrictionForceMultiplier=1.15f;
}

void ARhinoRearModule::BeginPlay()
{
    if(HasAuthority() && !ParentTruck) { bDetached=true; }
    Super::BeginPlay();ApplyMountedState();
    if(ParentTruck) { AddTickPrerequisiteActor(ParentTruck); }
}
void ARhinoRearModule::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME(ARhinoRearModule,bDetached);DOREPLIFETIME(ARhinoRearModule,ParentTruck);
}
void ARhinoRearModule::ApplyMountedState()
{
    SetReplicateMovement(bDetached);
    auto* Move=CastChecked<UChaosWheeledVehicleMovementComponent>(GetVehicleMovement());
    // Chaos builds the engine/transmission only when mechanical simulation is
    // enabled during physics creation. Restore these flags BEFORE rebuilding.
    Move->EnableMechanicalSim(bDetached);Move->EnableSuspension(bDetached);Move->EnableWheelFriction(bDetached);
    if(!bDetached) { GetMesh()->SetSimulatePhysics(false); }
    GetMesh()->SetCollisionProfileName(bDetached?TEXT("Vehicle"):TEXT("NoCollision"));
    GetMesh()->SetEnableGravity(bDetached);
    if(bDetached)
    {
        GetMesh()->SetSimulatePhysics(true);
        GetMesh()->RecreatePhysicsState();Move->RecreatePhysicsState();
        GetMesh()->SetAllBodiesSimulatePhysics(true);GetMesh()->WakeAllRigidBodies();
    }
}
void ARhinoRearModule::SetDetached(bool Value)
{
    if(!HasAuthority() || Value==bDetached) { return; }
    bDetached=Value;
    if(Value) { DetachFromActor(FDetachmentTransformRules::KeepWorldTransform); }
    ApplyMountedState();ForceNetUpdate();
}
float ARhinoRearModule::VisualDeployment() const { return bDetached?1.f:0.f; }
const UChaosVehicleWheel* ARhinoRearModule::AnimationWheel(FName Name) const
{
    if(!bDetached && ParentTruck && Definition)
    {
        const auto* Part=Definition->Wheels.FindByPredicate([Name](const FMaskWheelDefinition& W){return W.Name==Name;});
        const auto* Move=CastChecked<UChaosWheeledVehicleMovementComponent>(ParentTruck->GetVehicleMovement());
        if(Part)
        {
            for(int32 I=0;I<ParentTruck->Definition->Wheels.Num();++I)
            {
                const auto& W=ParentTruck->Definition->Wheels[I];
                if(W.Center.X<0 && W.Center.Y*Part->Center.Y>0 && Move->Wheels.IsValidIndex(I)) { return Move->Wheels[I]; }
            }
        }
    }
    return Super::AnimationWheel(Name);
}
void ARhinoRearModule::Tick(float DeltaSeconds)
{
    // Ownership, attachment and bDetached can arrive in different network
    // updates after possession changes. The replicated mounted state wins over
    // any late free-body physics packet, on every peer.
    if(!bDetached && ParentTruck && ParentTruck->Definition)
    {
        if(GetMesh()->IsSimulatingPhysics()) { ApplyMountedState(); }
        if(GetAttachParentActor()!=ParentTruck) { AttachToActor(ParentTruck,FAttachmentTransformRules::KeepWorldTransform); }
        SetActorRelativeTransform(FTransform(ParentTruck->Definition->RearModuleOrigin));
    }
    Super::Tick(DeltaSeconds);
    if(!Definition) { return; }
    const float CrewTransfer=bDetached?1.f:0.f;
    if(!IsDriverOnFoot()) { Matt->SetRelativeLocation(FMath::Lerp(Definition->MountedDriverLocation,Definition->DriverLocation,CrewTransfer)); }
    TArray<AActor*> Attached;GetAttachedActors(Attached);
    for(auto* Actor:Attached) { if(Actor!=DriverCharacter.Get()) { Actor->SetActorHiddenInGame(!bDetached); } }
}
void ARhinoRearModule::ToggleMode() { if(!IsPauseMenuOpen()) { ServerRequestDock(); } }
void ARhinoRearModule::ServerRequestDock_Implementation()
{
    if(!ParentTruck || !bDetached) { ClientVehicleSwitchFeedback(TEXT("Module autonome : retour au camion indisponible"));return; }
    if(auto* PC=Cast<APlayerController>(GetController()))
    {
        auto* GM=Cast<ACustomGameMode>(GetWorld()->GetAuthGameMode());
        if(!GM || !GM->SwitchPlayerVehicleTo(PC,ParentTruck)) { ClientVehicleSwitchFeedback(TEXT("Le camion est occupe par un autre joueur"));return; }
    }
    ParentTruck->Modes->ServerToggleMode();
}
void ARhinoRearModule::Destroyed()
{
    // A destroyed AI companion is replaced with its truck at the next full truck
    // spawn, not by an unrelated training opponent. Human respawns keep the class.
    auto* AI=Cast<AVehicleBotController>(GetController());
    if(AI) { AI->UnPossess(); }
    Super::Destroyed();
    if(AI) { AI->Destroy(); }
}

void ARhinoPawn::BeginPlay()
{
    Super::BeginPlay();
    if(HasAuthority() && Definition && Definition->RearModule)
    {
        FleetTeamId=GetUniqueID();
        auto* Class=LoadClass<ARhinoRearModule>(nullptr,TEXT("/Game/MASK/Rhino/BP_RhinoRear.BP_RhinoRear_C"));
        if(!Class) { UE_LOG(LogTemp,Error,TEXT("Rhino rear playable Blueprint missing"));return; }
        RearModule=GetWorld()->SpawnActorDeferred<ARhinoRearModule>(Class,GetActorTransform(),this,nullptr,ESpawnActorCollisionHandlingMethod::AlwaysSpawn);
        if(RearModule)
        {
            RearModule->ParentTruck=this;RearModule->FleetTeamId=FleetTeamId;RearModule->FinishSpawning(GetActorTransform());
            RearModule->AttachToActor(this,FAttachmentTransformRules::KeepWorldTransform);
            RearModule->SetActorRelativeTransform(FTransform::Identity);Modes->IgnoredModules.Add(RearModule);
            auto* AI=GetWorld()->SpawnActor<AVehicleBotController>();if(AI) { AI->Possess(RearModule); }
        }
    }
}
void ARhinoPawn::EndPlay(const EEndPlayReason::Type Reason)
{
    if(HasAuthority() && IsValid(RearModule))
    {
        if(!RearModule->bDetached || Reason!=EEndPlayReason::Destroyed) { RearModule->Destroy(); }
        else { RearModule->ParentTruck=nullptr;RearModule->ForceNetUpdate(); }
    }
    Super::EndPlay(Reason);
}
void ARhinoPawn::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);DOREPLIFETIME(ARhinoPawn,RearModule);
}
bool ARhinoPawn::CanChangeVehicleMode(FString& Reason) const
{
    if(!IsValid(RearModule)) { Reason=TEXT("Le module arriere est indisponible");return false; }
    if(IsDriverOnFoot() || RearModule->IsDriverOnFoot()) { Reason=TEXT("Un conducteur est a pied : remontez avant de transformer Rhino");return false; }
    if(RearModule->bDetached && Modes->GetMode()==EMaskVehicleMode::Combat)
    {
        if(RearModule->GetController() && RearModule->GetController()->IsPlayerController())
        { Reason=TEXT("Le module arriere est pilote par un autre joueur");return false; }
    }
    return true;
}
void ARhinoPawn::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if(!HasAuthority() || !IsValid(RearModule) || !Definition || Definition->RearModuleTrack.IsEmpty()) { return; }
    const auto State=Modes->GetMode();
    if(State==EMaskVehicleMode::Deploying || State==EMaskVehicleMode::Combat)
    {
        if(!RearModule->bDetached)
        {
            const FVector Velocity=GetMesh()->GetPhysicsLinearVelocity();
            RearModule->SetDetached(true);
            // Fast gameplay ejection. Clear the overlapping mounted collision
            // volumes first, then inherit truck momentum and add a rearward kick.
            const FVector Start=Definition->RearModuleOrigin-FVector(180,0,-10);
            RearModule->SetActorLocationAndRotation(GetActorTransform().TransformPosition(Start),GetActorRotation(),false,nullptr,ETeleportType::TeleportPhysics);
            RearModule->GetMesh()->SetPhysicsLinearVelocity(Velocity-GetActorForwardVector()*800.f);
            RearModule->GetMesh()->SetPhysicsAngularVelocityInRadians(GetMesh()->GetPhysicsAngularVelocityInRadians());RearModule->ForceNetUpdate();
        }
        return;
    }
    if(RearModule->bDetached) { RearModule->SetDetached(false);RearModule->AttachToActor(this,FAttachmentTransformRules::KeepWorldTransform); }
    RearModule->SetActorRelativeTransform(FTransform(Definition->RearModuleOrigin));
}
