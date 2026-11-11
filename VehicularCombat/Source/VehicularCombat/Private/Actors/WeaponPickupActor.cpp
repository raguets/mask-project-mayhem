// Copyright 2022 Danial Kamali. All Rights Reserved.

#include "WeaponPickupActor.h"
#include "MASK/MaskDriverCharacter.h"
#include "Components/SkeletalMeshComponent.h"
#include "ProjectileActor.h"
#include "SpawnManagerActor.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundCue.h"
#include "Components/SphereComponent.h"
#include "Net/UnrealNetwork.h"

AWeaponPickupActor::AWeaponPickupActor()
{
	SkeletalMesh = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("Skeletal Mesh"));
	SetRootComponent(SkeletalMesh);
	SkeletalMesh->PrimaryComponentTick.bStartWithTickEnabled = false;
	SkeletalMesh->bApplyImpulseOnDamage = false;
	SkeletalMesh->CanCharacterStepUpOn = ECB_No;
	SkeletalMesh->SetCollisionProfileName("Pickup");
	
	SphereCollision = CreateDefaultSubobject<USphereComponent>(TEXT("Sphere Collision"));
	SphereCollision->SetupAttachment(SkeletalMesh);
	SphereCollision->PrimaryComponentTick.bStartWithTickEnabled = false;
	SphereCollision->bApplyImpulseOnDamage = false;
	SphereCollision->CanCharacterStepUpOn = ECB_No;
	SphereCollision->SetCollisionProfileName("CollisionBound");
	SphereCollision->SetCollisionEnabled(ECollisionEnabled::NoCollision);	// Collision is only get enabled when actor get dropped or spawned.
	SphereCollision->OnComponentBeginOverlap.AddDynamic(this, &APickupActor::OnBeginOverlap);
	SphereCollision->OnComponentEndOverlap.AddDynamic(this, &APickupActor::OnEndOverlap);

	// Initialize variables
	PickupType = EPickupType::Weapon;
	ProjectileRef = nullptr;
	WeaponType = EWeaponType::Primary;
	AmmoType = EAmmoType::Rocket;
	WeaponName = EWeaponName::NoName;
	bIsAutomatic = false;
	TimeBetweenShots = 0.5;
	Range = 5000.0f;
	MaxAmmo = 150;
	CurrentAmmo = 120;
	ReloadAmount = CurrentMagazineAmmo = MagazineSize = 1;
	ReloadTime = 2.0f;
}

void AWeaponPickupActor::GetLifetimeReplicatedProps(TArray<FLifetimeProperty> &OutLifetimeProps) const
{
	Super::GetLifetimeReplicatedProps(OutLifetimeProps);

	// Replicate to everyone
	DOREPLIFETIME(AWeaponPickupActor, MaxAmmo);
	DOREPLIFETIME(AWeaponPickupActor, CurrentAmmo);
	DOREPLIFETIME(AWeaponPickupActor, MagazineSize);
	DOREPLIFETIME(AWeaponPickupActor, CurrentMagazineAmmo);
	DOREPLIFETIME(AWeaponPickupActor, ReloadAmount);
	DOREPLIFETIME(AWeaponPickupActor, ReloadTime);
}

void AWeaponPickupActor::BeginPlay()
{
	Super::BeginPlay();

	if (GetLocalRole() == ROLE_Authority)
	{
		ProjectileRef = ProjectileClass.GetDefaultObject();
		// Zero is the existing Blueprint sentinel for an automatically filled
		// initial magazine. Positive explicitly authored values are preserved.
		if (CurrentMagazineAmmo <= 0)
		{
			CurrentMagazineAmmo = FMath::Min(MagazineSize, CurrentAmmo);
			CurrentAmmo -= CurrentMagazineAmmo;
		}
	}
}

bool AWeaponPickupActor::ServerSpawnProjectile_Validate(FTransform NewTransform)
{
	if (ProjectileRef)
	{
		return true;
	}
	return false;
}

void AWeaponPickupActor::ServerSpawnProjectile_Implementation(FTransform NewTransform)
{
	// Handheld fire is rate/ammo/ownership checked by the driver's server tick.
	if(GetOwner() && GetOwner()->IsA<AMaskDriverCharacter>()) { return; }
	MulticastSpawnProjectile(ProjectileClass, ProjectileRef->NumberOfPellets, SkeletalMesh->GetSocketLocation(FName("MuzzleSocket")), SkeletalMesh->GetSocketRotation(FName("MuzzleSocket")), GetOwner());
	MulticastWeaponEffects();
}

bool AWeaponPickupActor::FireFromDriver(AMaskDriverCharacter* Driver)
{
	if(!HasAuthority() || !Driver || GetOwner()!=Driver || !Driver->IsOnFoot() || Driver->Health<=0.f || !ProjectileRef || CurrentMagazineAmmo<=0) { return false; }
	const FVector Eye=Driver->GetPawnViewLocation();const FVector End=Eye+Driver->GetBaseAimRotation().Vector()*Range;
	FCollisionQueryParams Query(SCENE_QUERY_STAT(DriverWeaponAim),false,Driver);Query.AddIgnoredActor(this);FHitResult Hit;
	const bool Blocked=GetWorld()->LineTraceSingleByChannel(Hit,Eye,End,ECC_Visibility,Query);
	const FVector Muzzle=SkeletalMesh->GetSocketLocation(TEXT("MuzzleSocket"));
	MulticastSpawnProjectile(ProjectileClass,ProjectileRef->NumberOfPellets,Muzzle,((Blocked?Hit.ImpactPoint:End)-Muzzle).Rotation(),Driver);MulticastWeaponEffects();return true;
}

void AWeaponPickupActor::MulticastSpawnProjectile_Implementation(TSubclassOf<AProjectileActor> ProjectileToSpawn, int32 NumberOfPellets, FVector Location, FRotator Rotation, AActor* OwnerRef)
{
	FActorSpawnParameters SpawnParameters;
	SpawnParameters.Owner = OwnerRef;
	SpawnParameters.Instigator = OwnerRef->GetInstigator();
	SpawnParameters.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	for(uint8 i = 0; i < NumberOfPellets; ++i)
	{
		GetWorld()->SpawnActor<AProjectileActor>(ProjectileToSpawn, Location, Rotation, SpawnParameters);
	}
}

void AWeaponPickupActor::MulticastWeaponEffects_Implementation()
{
	const FVector Location = SkeletalMesh->GetSocketLocation(FName("MuzzleSocket"));
	const FRotator Rotation = SkeletalMesh->GetSocketRotation(FName("MuzzleSocket"));
	
	UGameplayStatics::SpawnSoundAtLocation(GetWorld(), Effects.FireSound, Location);
	
	UGameplayStatics::SpawnEmitterAtLocation(GetWorld(), Effects.MuzzleFlash, Location, Rotation, Effects.MuzzleFlashScale);
	if (Effects.MuzzleFlashRear)
	{
		UGameplayStatics::SpawnEmitterAtLocation(GetWorld(), Effects.MuzzleFlashRear, Location, Rotation, Effects.MuzzleFlashScale);
	}
}

void AWeaponPickupActor::OnRep_PickupState()
{
	switch (PickupState)
	{
	case EPickupState::PickedUp:
		// Picked up
		SkeletalMesh->SetSimulatePhysics(false);
		SkeletalMesh->SetCollisionProfileName("Weapon");
		SphereCollision->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		SetLifeSpan(0.0f);
		if (SpawnManager)
		{
			SpawnManager->ServerEnterSpawnQueue(PickupType);
			SpawnManager = nullptr;
		}
		break;
	case EPickupState::Dropped:
		// Dropped
		SetOwner(nullptr);
		SkeletalMesh->SetSimulatePhysics(true);
		SkeletalMesh->SetCollisionProfileName("Pickup");
		SphereCollision->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
		SetLifeSpan(FMath::FRandRange(10.0f, 15.0f));
		break;
	case EPickupState::Used:
		// Used
		Destroy();
		break;
	}
}
