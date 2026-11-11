#include "MASK/MaskDriverMovementComponent.h"
#include "GameFramework/Character.h"

void UMaskDriverMovementComponent::PhysFalling(float DeltaTime,int32 Iterations)
{
    Super::PhysFalling(DeltaTime,Iterations);
    // A shallow complex-road contact can keep sliding without producing the
    // landing sweep. Remaining in Falling freezes the non-looping jump pose,
    // removes walking braking and prevents vehicle entry.
    if(!HasValidData() || !IsFalling() || Velocity.Z>0.f || Velocity.Z< -50.f || CharacterOwner->IsJumpProvidingForce()) { return; }
    FFindFloorResult Floor;
    FindFloor(UpdatedComponent->GetComponentLocation(),Floor,false);
    // Require a real walkable floor within the normal walking contact gap.
    // Never snap from jump height, accept a wall, or teleport the capsule.
    if(Floor.IsWalkableFloor() && !Floor.HitResult.bStartPenetrating && Floor.GetDistanceToFloor()>=0.f && Floor.GetDistanceToFloor()<=MAX_FLOOR_DIST)
    { ProcessLanded(Floor.HitResult,0.f,Iterations); }
}
