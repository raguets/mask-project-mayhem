#include "MASK/MaskVehicleModeComponent.h"
#include "Engine/World.h"
#include "GameFramework/GameStateBase.h"
#include "Components/PrimitiveComponent.h"
#include "Components/HealthComponent.h"
#include "Net/UnrealNetwork.h"
#include "Engine/OverlapResult.h"
#include "MASK/ThunderhawkPawn.h"
#include "MASK/MaskVehicleDefinition.h"

UMaskVehicleModeComponent::UMaskVehicleModeComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
	SetIsReplicatedByDefault(true);
}

void UMaskVehicleModeComponent::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
	Super::GetLifetimeReplicatedProps(OutLifetimeProps);
	DOREPLIFETIME(UMaskVehicleModeComponent, State);
}

double UMaskVehicleModeComponent::ServerNow() const
{
	const auto* GS = GetWorld()->GetGameState();
	return GS ? GS->GetServerWorldTimeSeconds() : GetWorld()->GetTimeSeconds();
}

float UMaskVehicleModeComponent::GetDeployment() const
{
	const float Alpha = FMath::Clamp(static_cast<float>((ServerNow()-State.ServerStartTime) / FMath::Max(Duration,.1f)),0.f,1.f);
	switch (State.Mode)
	{
	case EMaskVehicleMode::Flight:
	case EMaskVehicleMode::Landing:
	case EMaskVehicleMode::Combat: return 1.f;
	case EMaskVehicleMode::Deploying: return Alpha;
	case EMaskVehicleMode::Retracting: return 1.f-Alpha;
	default: return 0.f;
	}
}

void UMaskVehicleModeComponent::ServerToggleMode_Implementation()
{
	LastRefusal.Reset();ClientFeedback(TEXT(""));
	if (State.Mode==EMaskVehicleMode::Deploying || State.Mode==EMaskVehicleMode::Retracting || State.Mode==EMaskVehicleMode::Landing) { return; }
	FString Reason;
	if(const auto* Vehicle=Cast<APlayerWheeledVehiclePawn>(GetOwner());Vehicle && Vehicle->IsDriverOnFoot()) { Refuse(TEXT("Remontez dans le vehicule avant de le transformer"));return; }
	if(const auto* Vehicle=Cast<AThunderhawkPawn>(GetOwner());Vehicle && !Vehicle->CanChangeVehicleMode(Reason)) { Refuse(*Reason);return; }
	if (const auto* Health=GetOwner()->FindComponentByClass<UHealthComponent>(); Health && Health->CurrentHealth<=0.f) { return; }
	if(State.Mode==EMaskVehicleMode::Flight)
	{
		State.Mode=EMaskVehicleMode::Landing;State.ServerStartTime=ServerNow();GetOwner()->ForceNetUpdate();return;
	}
	if(State.Mode==EMaskVehicleMode::Road && !HasArticulationClearance()) { return; }
	State.Mode=State.Mode==EMaskVehicleMode::Road?EMaskVehicleMode::Deploying:EMaskVehicleMode::Retracting;
	State.ServerStartTime=ServerNow();GetOwner()->ForceNetUpdate();
	UE_LOG(LogTemp,Display,TEXT("MASK_TRANSFORM start mode=%d speed=%.1f"),static_cast<int>(State.Mode),GetOwner()->GetVelocity().Size());
}

bool UMaskVehicleModeComponent::HasArticulationClearance()
{
	FCollisionQueryParams Query(SCENE_QUERY_STAT(MaskDeploymentClearance),false,GetOwner());
	TArray<AActor*> Attached;GetOwner()->GetAttachedActors(Attached,true,true);Query.AddIgnoredActors(Attached);
	for(const auto& Module:IgnoredModules) { if(Module) { Query.AddIgnoredActor(Module); } }
	const auto* Car=Cast<AThunderhawkPawn>(GetOwner());
	const bool Motorcycle=Car && Car->Definition && Car->Definition->Dynamics.bTwoWheelRoadBalance;
	// Keep the upper rotor envelope clear of the road while the bike leans.
	// Obstacles above/alongside the mechanism still block deployment.
	const FQuat ClearanceRotation=Motorcycle?FRotator(0,GetOwner()->GetActorRotation().Yaw,0).Quaternion():GetOwner()->GetActorQuat();
	const FVector Center=GetOwner()->GetActorLocation()+ClearanceRotation.RotateVector(ClearanceCenter);
	TArray<FOverlapResult> Overlaps;
	// Use the vehicle's collision contract: dropped pickups explicitly ignore
	// vehicles and must not become phantom ceilings during descent/retraction.
	if (GetWorld()->OverlapMultiByChannel(Overlaps,Center,ClearanceRotation,ECC_Vehicle,
		FCollisionShape::MakeBox(ClearanceExtent),Query))
	{
		Refuse(TEXT("Espace insuffisant pour les articulations"));
		for (const auto& Hit:Overlaps)
		{
			if (Hit.bBlockingHit && Hit.GetActor())
			{
				FVector Origin,Extent;Hit.GetActor()->GetActorBounds(true,Origin,Extent);
				UE_LOG(LogTemp,Display,TEXT("MASK_TRANSFORM blocker=%s origin=%s extent=%s owner=%s rotation=%s"),*GetNameSafe(Hit.GetActor()),*Origin.ToString(),*Extent.ToString(),*GetOwner()->GetActorLocation().ToString(),*GetOwner()->GetActorRotation().ToString());
			}
		}
		UE_LOG(LogTemp,Display,TEXT("MASK_TRANSFORM refused clearance"));return false;
	}
	return true;
}
void UMaskVehicleModeComponent::NotifyTouchdown()
{
	if(!GetOwner()->HasAuthority() || State.Mode!=EMaskVehicleMode::Landing) { return; }
	if(!HasArticulationClearance()) { return; }
	State.Mode=EMaskVehicleMode::Retracting;State.ServerStartTime=ServerNow();LastRefusal.Reset();ClientFeedback(TEXT(""));GetOwner()->ForceNetUpdate();
}

void UMaskVehicleModeComponent::Refuse(const TCHAR* Message) { LastRefusal=Message;ClientFeedback(LastRefusal);UE_LOG(LogTemp,Display,TEXT("MASK_TRANSFORM refused=%s"),Message); }
void UMaskVehicleModeComponent::ClientFeedback_Implementation(const FString& Message) { LastRefusal=Message; }

void UMaskVehicleModeComponent::TickComponent(float DeltaTime,ELevelTick TickType,FActorComponentTickFunction* TickFunction)
{
	Super::TickComponent(DeltaTime,TickType,TickFunction);
	if (!GetOwner()->HasAuthority() || ServerNow()-State.ServerStartTime<Duration) { return; }
	if (State.Mode==EMaskVehicleMode::Deploying) { State.Mode=bSupportsFlight?EMaskVehicleMode::Flight:EMaskVehicleMode::Combat;GetOwner()->ForceNetUpdate(); }
	else if (State.Mode==EMaskVehicleMode::Retracting) { State.Mode=EMaskVehicleMode::Road;GetOwner()->ForceNetUpdate(); }
}
