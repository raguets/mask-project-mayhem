#include "MASK/MantaPawn.h"
#include "MASK/MaskVehicleModeComponent.h"
#include "Actors/WeaponPickupActor.h"
#include "Components/SkeletalMeshComponent.h"

UMantaFrontWheel::UMantaFrontWheel() { WheelRadius=29.6f;WheelWidth=21.f; }
UMantaRearWheel::UMantaRearWheel() { WheelRadius=29.6f;WheelWidth=21.f; }
AMantaPawn::AMantaPawn(const FObjectInitializer& Initializer):Super(Initializer) { FleetTeamId=2; }
void AMantaPawn::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    // The source already contains Manta's integrated cannons. Keep the shared
    // inventory, sockets and firing logic, without adding sedan weapon models.
    // Restore a weapon's mesh as soon as it is dropped or carried on foot.
    for(int32 I=IntegratedWeaponMeshes.Num()-1;I>=0;--I)
    {
        auto* WeaponMesh=IntegratedWeaponMeshes[I].Get();
        if(!WeaponMesh || WeaponMesh->GetOwner()->GetAttachParentActor()!=this)
        {
            if(WeaponMesh) { WeaponMesh->SetVisibility(true,false); }
            IntegratedWeaponMeshes.RemoveAtSwap(I);
        }
    }
    TArray<AActor*> Attached;GetAttachedActors(Attached);
    for(auto* Actor:Attached)
    {
        if(auto* Weapon=Cast<AWeaponPickupActor>(Actor))
        {
            if(auto* WeaponMesh=Weapon->FindComponentByClass<USkeletalMeshComponent>())
            { IntegratedWeaponMeshes.AddUnique(WeaponMesh);WeaponMesh->SetVisibility(false,false); }
        }
    }
}
void AMantaPawn::EndPlay(const EEndPlayReason::Type Reason)
{
    for(const auto& Item:IntegratedWeaponMeshes)
    { if(auto* WeaponMesh=Item.Get()) { WeaponMesh->SetVisibility(true,false); } }
    IntegratedWeaponMeshes.Reset();Super::EndPlay(Reason);
}
const UChaosVehicleWheel* AMantaPawn::AnimationWheel(FName Name) const
{
    // Source tracks carry the wheels to their turbine positions, as on Raven.
    return Modes && Modes->GetDeployment()>UE_SMALL_NUMBER ? nullptr : Super::AnimationWheel(Name);
}
