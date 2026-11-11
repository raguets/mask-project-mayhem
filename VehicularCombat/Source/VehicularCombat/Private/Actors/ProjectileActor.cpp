// Copyright 2022 Danial Kamali. All Rights Reserved.

#include "ProjectileActor.h"
#include "Engine/DataTable.h"
#include "GameFramework/ProjectileMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Kismet/KismetMathLibrary.h"
#include "Particles/ParticleSystemComponent.h"
#include "Sound/SoundCue.h"
#include "Structures/ExplosiveProjectileDamageStruct.h"
#include "Structures/ProjectileDamageStruct.h"

AProjectileActor::AProjectileActor()
{
	PrimaryActorTick.bCanEverTick = false;
	PrimaryActorTick.bStartWithTickEnabled = false;
	SetCanBeDamaged(false);

	StaticMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Static Mesh"));
	SetRootComponent(StaticMesh);
	StaticMesh->PrimaryComponentTick.bStartWithTickEnabled = false;
	StaticMesh->SetNotifyRigidBodyCollision(true);
	StaticMesh->CanCharacterStepUpOn = ECB_No;
	StaticMesh->SetCollisionProfileName("Projectile");
	StaticMesh->SetGenerateOverlapEvents(false);
	StaticMesh->bReturnMaterialOnMove = true;
	StaticMesh->SetCanEverAffectNavigation(false);
	StaticMesh->OnComponentHit.AddDynamic(this, &AProjectileActor::OnHit);

	TrailParticle = CreateDefaultSubobject<UParticleSystemComponent>(TEXT("Trail Particle"));
	TrailParticle->SetupAttachment(StaticMesh, TEXT("TrailSocket"));
	TrailParticle->PrimaryComponentTick.bStartWithTickEnabled = false;

	ProjectileMovement = CreateDefaultSubobject<UProjectileMovementComponent>(TEXT("Projectile Movement"));
	ProjectileMovement->InitialSpeed = 5000.0f;
	ProjectileMovement->MaxSpeed = 5000.0f;
	ProjectileMovement->ProjectileGravityScale = 0.1f;
	
	// Load data tables	TODO: Set it in the BP instead of loading it from C++
	static ConstructorHelpers::FObjectFinder<UDataTable> ProjectileDataObject(TEXT("DataTable'/Game/Blueprints/Projectiles/DT_ProjectileDamage.DT_ProjectileDamage'"));
	if (ProjectileDataObject.Succeeded())
	{
		ProjectileDataTable = ProjectileDataObject.Object;
	}
	
	static ConstructorHelpers::FObjectFinder<UDataTable> ExplosiveProjectileDataObject(TEXT("DataTable'/Game/Blueprints/Projectiles/DT_ExplosiveProjectileDamage.DT_ExplosiveProjectileDamage'"));
	if (ExplosiveProjectileDataObject.Succeeded())
	{
		ExplosiveProjectileDataTable = ExplosiveProjectileDataObject.Object;
	}

	// Initialize variables
	AmmoType = EAmmoType::Rocket;
	bIsExplosive = false;
	NumberOfPellets = 1;
	PelletSpread = 0.0f;
	SwitchExpression = 0;
	LifeSpan = 2.0f;
}

void AProjectileActor::BeginPlay()
{
	Super::BeginPlay();
	// A muzzle may overlap an attached weapon on spawn. Ignore the firing
	// vehicle and its attachments for movement sweeps, not other vehicles.
	if (AActor* FiringOwner = GetOwner())
	{
		StaticMesh->IgnoreActorWhenMoving(FiringOwner, true);
		TArray<AActor*> AttachedActors;
		FiringOwner->GetAttachedActors(AttachedActors, true, true);
		for (AActor* Attached : AttachedActors) { StaticMesh->IgnoreActorWhenMoving(Attached, true); }
	}

	SetLifeSpan(LifeSpan);
}

void AProjectileActor::OnHit(UPrimitiveComponent* HitComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, FVector NormalImpulse, const FHitResult& Hit)
{
#if !UE_BUILD_SHIPPING
	UE_LOG(LogTemp, Log, TEXT("VC_PROJECTILE_HIT actor=%s component=%s point=%s explosive=%d owner=%s"), *GetNameSafe(OtherActor), *GetNameSafe(OtherComp), *Hit.ImpactPoint.ToString(), bIsExplosive, *GetNameSafe(GetOwner()));
#endif
	// Locally spawned cosmetic projectiles also have ROLE_Authority on a
	// client. Only the server/standalone world applies gameplay damage.
	if (Hit.PhysMaterial.IsValid())
	{
		SwitchExpression = StaticEnum<EPhysicalSurface>()->GetIndexByValue(UGameplayStatics::GetSurfaceType(Hit));
	}
	if (GetNetMode() != NM_Client && HasAuthority())
	{
#if !UE_BUILD_SHIPPING
		UE_LOG(LogTemp,Log,TEXT("VC_DAMAGE_TABLE table=%s ammo=%s"),*GetNameSafe(ExplosiveProjectileDataTable),*StaticEnum<EAmmoType>()->GetValueAsName(AmmoType).ToString());
#endif
		
		const FName AmmoName = StaticEnum<EAmmoType>()->GetValueAsName(AmmoType);
		if (bIsExplosive && ExplosiveProjectileDataTable)
		{
			const FExplosiveProjectileDamage* ExplosiveProjectileInfo = ExplosiveProjectileDataTable->FindRow<FExplosiveProjectileDamage>(AmmoName, TEXT("Projectile Info Context"), true);
			if (ExplosiveProjectileInfo)
			{
				// Apply radial damage with fall off for explosive projectiles
				// The projectile is still collidable until OnHit returns. It must
				// not block its own radial-damage visibility traces.
				const TArray<AActor*> IgnoreActors{this};
				// Keep the visibility trace outside the surface we just struck;
				// an epicentre on/in the floor can occlude the whole explosion.
				const FVector Origin=Hit.ImpactPoint+Hit.ImpactNormal.GetSafeNormal();
				UGameplayStatics::ApplyRadialDamageWithFalloff(GetWorld(), ExplosiveProjectileInfo->BaseDamage, ExplosiveProjectileInfo->MinimumDamage, Origin, ExplosiveProjectileInfo->DamageInnerRadius, ExplosiveProjectileInfo->DamageOuterRadius, 2.0f, DamageType, IgnoreActors, GetOwner(), GetInstigatorController(), ECollisionChannel::ECC_Visibility);
			}
		}
		else if (ProjectileDataTable)
		{
			const FProjectileDamage* ProjectileInfo = ProjectileDataTable->FindRow<FProjectileDamage>(AmmoName, TEXT("Projectile Info Context"), true);
			if (ProjectileInfo)
			{
				// Apply point damage for nonexplosive projectiles based on surface type
				UGameplayStatics::ApplyPointDamage(Hit.GetActor(), CalculatePointDamage(ProjectileInfo), Hit.TraceStart, Hit, GetInstigatorController(), GetOwner(), DamageType);
			}
		}

	}
	// The weapon multicast creates a local cosmetic projectile on each peer;
	// preserve its local impact presentation without applying client damage.
	MulticastHitEffects(SwitchExpression, Hit);
	Destroy();
}

float AProjectileActor::CalculatePointDamage(const FProjectileDamage* ProjectileInfo) const
{
	switch (SwitchExpression)
	{
	case 1:
		// Metal
		return ProjectileInfo->DamageToMetal;
	case 2:
		// Plastic
		return ProjectileInfo->DamageToPlastic;
	case 3:
		// Glass
		return ProjectileInfo->DamageToGlass;
	case 0: default:
		return ProjectileInfo->DefaultDamage;
	}
}

void AProjectileActor::MulticastHitEffects_Implementation(uint8 InSwitchExpression, FHitResult HitResult)
{
	UParticleSystem* Emitter;
	USoundCue* Sound;
	UMaterialInterface* Decal;
	FVector DecalSize;
	float DecalLifeSpan;
	FindHitEffects(InSwitchExpression, Emitter, Sound, Decal, DecalSize, DecalLifeSpan);
	UE_LOG(LogTemp, Log, TEXT("VC_IMPACT_LOCAL mode=%d configured=%d"), static_cast<int32>(GetNetMode()), Emitter != nullptr || Sound != nullptr || (bIsExplosive && HitEffects.ExplosiveEmitter != nullptr));

	const FRotator SpawnRotation = UKismetMathLibrary::MakeRotFromX(HitResult.ImpactNormal);
	
	// Spawn impact emitter
	UGameplayStatics::SpawnEmitterAtLocation(GetWorld(), Emitter, HitResult.ImpactPoint, SpawnRotation);
	
	// Spawn decal attached to hit component
	UGameplayStatics::SpawnDecalAttached(Decal, DecalSize, HitResult.GetComponent(), HitResult.BoneName, HitResult.ImpactPoint,
		SpawnRotation, EAttachLocation::KeepWorldPosition, DecalLifeSpan);

	// Play sound at the impact location
	UGameplayStatics::PlaySoundAtLocation(GetWorld(), Sound, HitResult.ImpactPoint);
	
	// If the projectile is explosive in addition to the surface impact emitter another emitter spawn for the explosion
	if (bIsExplosive)
	{
		UGameplayStatics::SpawnEmitterAtLocation(GetWorld(), HitEffects.ExplosiveEmitter, HitResult.ImpactPoint, SpawnRotation);
	}
}

void AProjectileActor::FindHitEffects(uint8 InSwitchExpression, UParticleSystem*& Emitter, USoundCue*& Sound, UMaterialInterface*& Decal, FVector& DecalSize, float& DecalLifeSpan) const
{
	Sound			= HitEffects.ObjectHitSound;
	DecalSize		= HitEffects.DecalSize;
	DecalLifeSpan	= HitEffects.DecalLifeSpan;
	switch (InSwitchExpression)
	{
	case 1:
		// Metal
		Emitter			= HitEffects.MetalHitEmitter;
		Decal			= HitEffects.MetalDecal;
		break;
	case 2:
		// Plastic
		Emitter			= HitEffects.PlasticHitEmitter;
		Decal			= HitEffects.PlasticDecal;
		break;
	case 3:
		// Glass
		Emitter			= HitEffects.GlassHitEmitter;
		Decal			= HitEffects.GlassDecal;
		break;
	case 4:
		// Asphalt
		Emitter			= HitEffects.AsphaltHitEmitter;
		Decal			= HitEffects.AsphaltDecal;
		break;
	case 5:
		// Stone
		Emitter			= HitEffects.StoneHitEmitter;
		Decal			= HitEffects.StoneDecal;
		break;
	case 6:
		// Wood
		Emitter			= HitEffects.WoodHitEmitter;
		Decal			= HitEffects.WoodDecal;
		break;
	case 0: default:
		Emitter			= HitEffects.MetalHitEmitter;
		Decal			= HitEffects.MetalDecal;
	}
}

void AProjectileActor::LifeSpanExpired()
{
	if (bIsExplosive)
	{
		// Set it to false to stop it from happening twice.
		bIsExplosive = false;
		MulticastDestroyEffect(GetActorLocation(), GetActorRotation());
	}
	
	Super::LifeSpanExpired();
}

void AProjectileActor::MulticastDestroyEffect_Implementation(FVector Location, FRotator Rotation)
{
	UE_LOG(LogTemp, Log, TEXT("VC_EXPIRY_LOCAL mode=%d configured=%d"), static_cast<int32>(GetNetMode()), HitEffects.ExplosiveEmitter != nullptr);
	// Explode the projectile after life span expired
	UGameplayStatics::SpawnEmitterAtLocation(GetWorld(), HitEffects.ExplosiveEmitter, Location, Rotation);
}
