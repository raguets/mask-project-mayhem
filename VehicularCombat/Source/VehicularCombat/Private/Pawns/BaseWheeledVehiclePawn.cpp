// Copyright 2022 Danial Kamali. All Rights Reserved.

#include "BaseWheeledVehiclePawn.h"
#include "Components/AudioComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "ChaosWheeledVehicleMovementComponent.h"
#include "Actors/AmmoPickupActor.h"
#include "Actors/HealthPickupActor.h"
#include "Actors/SpeedBoostPickupActor.h"
#include "Actors/WeaponPickupActor.h"
#include "Components/HealthComponent.h"
#include "Core/CustomPlayerState.h"
#include "Net/UnrealNetwork.h"

const FName ABaseWheeledVehiclePawn::EngineAudioRPM("RPM");

ABaseWheeledVehiclePawn::ABaseWheeledVehiclePawn(const FObjectInitializer& ObjectInitializer) : Super(ObjectInitializer)
{
	GetMesh()->SetSimulatePhysics(true);
	GetMesh()->SetAnimationMode(EAnimationMode::AnimationBlueprint);

	GetVehicleMovementComponent()->EnableSelfRighting(true);

	// Setup the audio component
	EngineSoundComp = CreateDefaultSubobject<UAudioComponent>(TEXT("EngineSound"));
	EngineSoundComp->SetupAttachment(GetMesh());
	EngineSoundComp->SetComponentTickEnabled(false);
	
	HealthComponent = CreateDefaultSubobject<UHealthComponent>(TEXT("Health Component"));

	// Initialize variables
	CurrentWeapon = nullptr;
	PlayerStateRef = nullptr;
	RespawnDelay = 5.0f;
	bDoOnceMoving = bDoOnceStopped = true;
	bIsAlive = true;
	bCanFireWeapon = true;
	bDoOnceReload = true;
	bBoostSpeed = false;
	SpeedBoostTime = 0.0f;
	SpeedBoostMultiplier = 1.0;
	JumpIntensity = 500.0f;
}

void ABaseWheeledVehiclePawn::GetLifetimeReplicatedProps(TArray<FLifetimeProperty> &OutLifetimeProps) const
{
	Super::GetLifetimeReplicatedProps(OutLifetimeProps);

	// Replicate to everyone
	DOREPLIFETIME(ABaseWheeledVehiclePawn, PlayerStateRef);
	DOREPLIFETIME(ABaseWheeledVehiclePawn, CurrentCamera);
	DOREPLIFETIME(ABaseWheeledVehiclePawn, bDoOnceReload);
	DOREPLIFETIME(ABaseWheeledVehiclePawn, bCanFireWeapon);
	DOREPLIFETIME(ABaseWheeledVehiclePawn, CurrentWeapon);
	DOREPLIFETIME(ABaseWheeledVehiclePawn, CurrentWeaponSlot);
	DOREPLIFETIME(ABaseWheeledVehiclePawn, bBoostSpeed);
	DOREPLIFETIME(ABaseWheeledVehiclePawn, SpeedBoostTime);
	DOREPLIFETIME(ABaseWheeledVehiclePawn, SpeedBoostMultiplier);
	DOREPLIFETIME(ABaseWheeledVehiclePawn, bIsAlive);
	DOREPLIFETIME(ABaseWheeledVehiclePawn, RespawnDelay);
}

void ABaseWheeledVehiclePawn::BeginPlay()
{
	Super::BeginPlay();
	
	if (GetLocalRole() == ROLE_Authority)
	{
		HealthComponent->ServerInitialize();
	}
}

void ABaseWheeledVehiclePawn::UpdateBotCombat(AActor* Target, bool bFire)
{
	if (!HasAuthority() || !GetController() || GetController()->IsPlayerController()) { return; }
	if (!bIsAlive || !IsValid(Target)) { ServerStopFireWeapon(); return; }
	if (PlayerStateRef && PlayerStateRef->SecondaryWeapon && CurrentWeaponSlot != EWeaponToDo::Secondary)
	{
		ServerSwitchWeapon(EWeaponToDo::Secondary);
	}
	if (!CurrentWeapon) { return; }
	if (auto* WeaponMesh = CurrentWeapon->FindComponentByClass<USkeletalMeshComponent>())
	{
		const FTransform Muzzle = WeaponMesh->GetSocketTransform(TEXT("MuzzleSocket"));
		const FQuat Relative = CurrentWeapon->GetActorQuat().Inverse() * Muzzle.GetRotation();
		FVector Origin, Extent;
		Target->GetActorBounds(true, Origin, Extent);
		const FVector Direction = Origin - Muzzle.GetLocation();
		CurrentWeapon->SetActorRotation(Direction.ToOrientationQuat() * Relative.Inverse());
	}
	if (bFire) { ServerStartFireWeapon(); }
	else { ServerStopFireWeapon(); }
}

void ABaseWheeledVehiclePawn::PossessedBy(AController* NewController)
{
	Super::PossessedBy(NewController);
	
	PlayerStateRef = Cast<ACustomPlayerState>(NewController->PlayerState);
}

void ABaseWheeledVehiclePawn::Tick(float Delta)
{
	Super::Tick(Delta);

	// Pass the engine RPM to the sound component
	const UChaosWheeledVehicleMovementComponent* WheeledVehicle = static_cast<UChaosWheeledVehicleMovementComponent*>(GetVehicleMovement());
	const float RPMToAudioScale = 2500.0f / WheeledVehicle->GetEngineMaxRotationSpeed();
	EngineSoundComp->SetFloatParameter(EngineAudioRPM, WheeledVehicle->GetEngineRotationSpeed()*RPMToAudioScale);
}

bool ABaseWheeledVehiclePawn::ServerJump_Validate()
{
	if (bIsAlive)
	{
		return true;
	}
	return false;
}

void ABaseWheeledVehiclePawn::ServerJump_Implementation()
{
	const FVector Impulse = GetMesh()->GetUpVector() * JumpIntensity;
	GetMesh()->AddImpulse(Impulse, FName(""), true);
}

void ABaseWheeledVehiclePawn::OnRep_PickupRef()
{
	if (GetLocalRole() == ROLE_Authority && PickupRef)
	{
		switch (PickupRef->PickupType)
		{
		case EPickupType::Weapon:
			// Weapon
			{
				AWeaponPickupActor* PickupWeapon = Cast<AWeaponPickupActor>(PickupRef);
				if (PickupWeapon)
				{
					ServerAddWeapon(PickupWeapon);
					ClientUpdatePickup(EPickupType::Weapon);
				}
			}
			break;
		case EPickupType::Ammo:
			// Ammo
			{
				AAmmoPickupActor* PickupAmmo = Cast<AAmmoPickupActor>(PickupRef);
				if (PickupAmmo)
				{
					ServerAddAmmo(PickupAmmo);
					ClientUpdatePickup(EPickupType::Ammo);
				}
			}
			break;
		case EPickupType::Health:
			// Health
			{
				AHealthPickupActor* PickupHealth = Cast<AHealthPickupActor>(PickupRef);
				if (PickupHealth && HealthComponent->CurrentHealth < HealthComponent->MaxHealth)
				{
					ClientUpdatePickup(EPickupType::Health);
					HealthComponent->ServerIncreaseHealth(PickupHealth->HealthAmount);
					PickupHealth->PickupState = EPickupState::Used;
					PickupHealth->OnRep_PickupState();
				}
			}
			break;
		case EPickupType::SpeedBoost:
			// Speed Boost
			{
				ASpeedBoostPickupActor* PickupSpeedBoost = Cast<ASpeedBoostPickupActor>(PickupRef);
				if (PickupSpeedBoost)
				{
					bBoostSpeed = true;
					SpeedBoostMultiplier = PickupSpeedBoost->BoostMultiplier;
					SpeedBoostTime += PickupSpeedBoost->BoostTime;
					GetWorld()->GetTimerManager().SetTimer(SpeedBoostTimer, this, &ABaseWheeledVehiclePawn::ServerUpdateSpeedBoost, 1.0f, true);
					ClientUpdatePickup(EPickupType::SpeedBoost);
					PickupSpeedBoost->PickupState = EPickupState::Used;
					PickupSpeedBoost->OnRep_PickupState();
				}
			}
			break;
		}
	}
}

bool ABaseWheeledVehiclePawn::ServerAddWeapon_Validate(AWeaponPickupActor* NewWeapon)
{
	if (NewWeapon)
	{
		return true;
	}
	return false;
}

void ABaseWheeledVehiclePawn::ServerAddWeapon_Implementation(AWeaponPickupActor* NewWeapon)
{
	// Update state of the new weapon
	NewWeapon->SetOwner(this);
	NewWeapon->PickupState = EPickupState::PickedUp;
	NewWeapon->OnRep_PickupState();
		
	// Equipped weapons follow their socket; welding would merge their query bodies
	// into the vehicle and can produce self-referencing suspension constraints.
	const FAttachmentTransformRules AttachmentRules = FAttachmentTransformRules(EAttachmentRule::SnapToTarget, EAttachmentRule::SnapToTarget, EAttachmentRule::KeepWorld, false);
	const FDetachmentTransformRules DetachmentRules = FDetachmentTransformRules(EDetachmentRule::KeepWorld, EDetachmentRule::KeepWorld, EDetachmentRule::KeepRelative, false);
	
	switch (NewWeapon->WeaponType)
	{
	case EWeaponType::Primary:
		// Primary
		if (PlayerStateRef->PrimaryWeapon == nullptr)
		{
			NewWeapon->AttachToComponent(GetMesh(), AttachmentRules, FName("PrimaryWeaponSocket"));
		}
		else if (PlayerStateRef->PrimaryWeapon != nullptr)
		{
			PlayerStateRef->PrimaryWeapon->DetachFromActor(DetachmentRules);
			PlayerStateRef->PrimaryWeapon->PickupState = EPickupState::Used;
			PlayerStateRef->PrimaryWeapon->OnRep_PickupState();
			NewWeapon->AttachToComponent(GetMesh(), AttachmentRules, FName("PrimaryWeaponSocket"));
		}
		PlayerStateRef->PrimaryWeapon = NewWeapon;
		ServerUpdateCurrentWeapon(NewWeapon, EWeaponToDo::Primary);
		break;
	case EWeaponType::Secondary:
		// Secondary
		if (PlayerStateRef->SecondaryWeapon == nullptr)
		{
			NewWeapon->AttachToComponent(GetMesh(), AttachmentRules, FName("SecondaryWeaponSocket"));
		}
		else if (PlayerStateRef->SecondaryWeapon != nullptr)
		{
			PlayerStateRef->SecondaryWeapon->DetachFromActor(DetachmentRules);
			PlayerStateRef->SecondaryWeapon->PickupState = EPickupState::Used;
			PlayerStateRef->SecondaryWeapon->OnRep_PickupState();
			NewWeapon->AttachToComponent(GetMesh(), AttachmentRules, FName("SecondaryWeaponSocket"));
		}
		PlayerStateRef->SecondaryWeapon = NewWeapon;
		ServerUpdateCurrentWeapon(NewWeapon, EWeaponToDo::Secondary);
		break;
	}
}

void ABaseWheeledVehiclePawn::ServerUpdateCurrentWeapon_Implementation(AWeaponPickupActor* NewWeapon, EWeaponToDo NewWeaponSlot)
{
	if (NewWeapon)
	{
		if (CurrentWeaponSlot == NewWeaponSlot || CurrentWeaponSlot == EWeaponToDo::NoWeapon)
		{
			CurrentWeapon = NewWeapon;
			CurrentWeaponSlot = NewWeaponSlot;
		}
	}
	else
	{
		CurrentWeapon = nullptr;
		CurrentWeaponSlot = EWeaponToDo::NoWeapon;
	}
	// RepNotify runs automatically on clients, not on the listen server.
	OnRep_CurrentWeapon();
}

bool ABaseWheeledVehiclePawn::ServerAddAmmo_Validate(AAmmoPickupActor* PickupAmmo)
{
	if (PlayerStateRef->PrimaryWeapon && PlayerStateRef->PrimaryWeapon->AmmoType == PickupAmmo->AmmoType
		&& PlayerStateRef->PrimaryWeapon->CurrentAmmo < PlayerStateRef->PrimaryWeapon->MaxAmmo)
	{
		return true;
	}
	
	if (PlayerStateRef->SecondaryWeapon && PlayerStateRef->SecondaryWeapon->AmmoType == PickupAmmo->AmmoType
		&& PlayerStateRef->SecondaryWeapon->CurrentAmmo < PlayerStateRef->SecondaryWeapon->MaxAmmo)
	{
		return true;
	}
	
	return false;
}

void ABaseWheeledVehiclePawn::ServerAddAmmo_Implementation(AAmmoPickupActor* PickupAmmo)
{
	if (PlayerStateRef->PrimaryWeapon->AmmoType == PickupAmmo->AmmoType)
	{
		PlayerStateRef->PrimaryWeapon->CurrentAmmo = FMath::Clamp(PlayerStateRef->PrimaryWeapon->CurrentAmmo + PickupAmmo->AmmoAmount, 0, PlayerStateRef->PrimaryWeapon->MaxAmmo);
		if (CurrentWeapon == PlayerStateRef->PrimaryWeapon)
		{
			ClientUpdateAmmo(CurrentWeapon->CurrentAmmo);

			if (CurrentWeapon->CurrentAmmo <= 0)
			{
				ServerReloadWeapon();	// TODO - need fix
			}
		}
	}
	else
	{
		PlayerStateRef->SecondaryWeapon->CurrentAmmo = FMath::Clamp(PlayerStateRef->SecondaryWeapon->CurrentAmmo + PickupAmmo->AmmoAmount, 0, PlayerStateRef->SecondaryWeapon->MaxAmmo);
		if (CurrentWeapon == PlayerStateRef->SecondaryWeapon)
		{
			ClientUpdateAmmo(CurrentWeapon->CurrentAmmo);

			if (CurrentWeapon->CurrentAmmo <= 0)
			{
				ServerReloadWeapon();
			}
		}
	}

	PickupAmmo->PickupState = EPickupState::Used;
	PickupAmmo->OnRep_PickupState();
}

bool ABaseWheeledVehiclePawn::ServerSwitchWeapon_Validate(EWeaponToDo NewWeapon)
{
	if (bIsAlive && CurrentWeaponSlot != NewWeapon)
	{
		switch (NewWeapon)
		{
		case EWeaponToDo::NoWeapon:
			// No Weapon = Nothing to switch
			return false;
		case EWeaponToDo::Primary:
			// Primary Weapon
			if (PlayerStateRef->PrimaryWeapon)
			{
				return true;
			}
			return false;
		case EWeaponToDo::Secondary:
			// Secondary Weapon
			if (PlayerStateRef->SecondaryWeapon)
			{
				return true;
			}
			return false;
		}
	}
	return false;
}

void ABaseWheeledVehiclePawn::ServerSwitchWeapon_Implementation(EWeaponToDo NewWeapon)
{
	GetWorld()->GetTimerManager().ClearTimer(ReloadTimer);
	CurrentWeaponSlot = NewWeapon;
	switch (NewWeapon)
	{
	case EWeaponToDo::NoWeapon:
		// No Weapon
		break;
	case EWeaponToDo::Primary:
		// Primary Weapon
		CurrentWeapon = PlayerStateRef->PrimaryWeapon;
		break;
	case EWeaponToDo::Secondary:
		// Secondary Weapon
		CurrentWeapon = PlayerStateRef->SecondaryWeapon;
		break;
	}
	OnRep_CurrentWeapon();
}

bool ABaseWheeledVehiclePawn::ServerStartFireWeapon_Validate()
{
	// A cooldown or empty magazine is normal gameplay, not a malformed RPC.
	return true;
}

void ABaseWheeledVehiclePawn::ServerStartFireWeapon_Implementation()
{
	UE_LOG(LogTemp, Log, TEXT("VC_FIRE server allowed=%d weapon=%s magazine=%d reserve=%d"), CanFireWeapon(), *GetNameSafe(CurrentWeapon), CurrentWeapon ? CurrentWeapon->CurrentMagazineAmmo : -1, CurrentWeapon ? CurrentWeapon->CurrentAmmo : -1);
	if (!CanFireWeapon()) { return; }
	ServerFireWeapon();
	if (CurrentWeapon->bIsAutomatic)
	{
		GetWorld()->GetTimerManager().SetTimer(FireWeaponTimer, this, &ABaseWheeledVehiclePawn::ServerFireWeapon, CurrentWeapon->TimeBetweenShots, true);
	}

	bCanFireWeapon = false;
	GetWorld()->GetTimerManager().SetTimer(ResetFireWeaponTimer, this, &ABaseWheeledVehiclePawn::ServerResetFireWeapon, CurrentWeapon->TimeBetweenShots);
}

bool ABaseWheeledVehiclePawn::ServerStopFireWeapon_Validate()
{
	return true;
}

void ABaseWheeledVehiclePawn::ServerStopFireWeapon_Implementation()
{
	GetWorld()->GetTimerManager().ClearTimer(FireWeaponTimer);
}

bool ABaseWheeledVehiclePawn::ServerFireWeapon_Validate()
{
	return true;
}

void ABaseWheeledVehiclePawn::ServerFireWeapon_Implementation()
{
	if (!bIsAlive || !CurrentWeapon || CurrentWeapon->CurrentMagazineAmmo <= 0)
	{
		GetWorld()->GetTimerManager().ClearTimer(FireWeaponTimer);
		return;
	}
	CurrentWeapon->ServerSpawnProjectile(GetActorTransform());

	CurrentWeapon->CurrentMagazineAmmo = --CurrentWeapon->CurrentMagazineAmmo;
	ClientUpdateMagAmmo(CurrentWeapon->CurrentMagazineAmmo);

	if (CurrentWeapon->CurrentMagazineAmmo <= 0)
	{
		if (CanReloadWeapon())
		{
			ClientUpdateWeaponState(EWeaponState::Reloading);
			GetWorld()->GetTimerManager().SetTimer(ReloadTimer, this, &ABaseWheeledVehiclePawn::ServerReloadWeapon, CurrentWeapon->ReloadTime);
		}
		else
		{
			ClientUpdateWeaponState(EWeaponState::NoAmmo);
		}
	}
}

bool ABaseWheeledVehiclePawn::CanFireWeapon() const
{
	if (bIsAlive && bCanFireWeapon && CurrentWeapon && CurrentWeapon->CurrentMagazineAmmo > 0)
	{
		return true;
	}
	return false;
}

void ABaseWheeledVehiclePawn::ServerResetFireWeapon_Implementation()
{
	bCanFireWeapon = true;
}

bool ABaseWheeledVehiclePawn::ServerReloadWeapon_Validate()
{
	if (CurrentWeapon->CurrentAmmo > 0)
	{
		return true;
	}
	return false;
}

void ABaseWheeledVehiclePawn::ServerReloadWeapon_Implementation()
{
	const int32 UsedAmmoFromMag = CurrentWeapon->MagazineSize - CurrentWeapon->CurrentMagazineAmmo;
	if (CurrentWeapon->CurrentAmmo >= UsedAmmoFromMag)
	{
		const int32 CurrentReloadAmount = FMath::Clamp(CurrentWeapon->ReloadAmount, 0, UsedAmmoFromMag);
		CurrentWeapon->CurrentAmmo -= CurrentReloadAmount;
		CurrentWeapon->CurrentMagazineAmmo = CurrentReloadAmount + CurrentWeapon->CurrentMagazineAmmo;
	}
	else
	{
		CurrentWeapon->CurrentMagazineAmmo += CurrentWeapon->CurrentAmmo;
		CurrentWeapon->CurrentAmmo = 0;
	}
	
	ClientUpdateAmmo(CurrentWeapon->CurrentAmmo);
	ClientUpdateMagAmmo(CurrentWeapon->CurrentMagazineAmmo);
	ClientUpdateWeaponState(EWeaponState::Idle);
	bDoOnceReload = true;
}

bool ABaseWheeledVehiclePawn::CanReloadWeapon() const
{
	if (bDoOnceReload && CurrentWeapon && CurrentWeapon->CurrentAmmo > 0 && CurrentWeapon->CurrentMagazineAmmo < CurrentWeapon->MagazineSize)
	{
		return true;
	}
	return false;
}

void ABaseWheeledVehiclePawn::ServerUpdateSpeedBoost_Implementation()
{
	SpeedBoostTime -= 1.0f;
	if (SpeedBoostTime <= 0.0f)
	{
		GetWorld()->GetTimerManager().ClearTimer(SpeedBoostTimer);
		bBoostSpeed = false;
	}
}

void ABaseWheeledVehiclePawn::ServerSetHealthLevel_Implementation(float CurrentHealth, float MaxHealth)
{
	// Start restoring health if 0 < Current Health < Max Health and restoring health is not started yet.
	if (CurrentHealth > 0.0f && CurrentHealth < MaxHealth && HealthComponent->bRestoreHealth != true)
	{
		HealthComponent->ServerStartRestoreHealth();
	}
	if (CurrentHealth <= 0.0f && bIsAlive)
	{
		CurrentWeapon = nullptr;
		bIsAlive = false;
		OnRep_IsAlive();
		MulticastDeath();

		FTimerHandle TimerHandle;
		GetWorld()->GetTimerManager().SetTimer(TimerHandle, this, &ABaseWheeledVehiclePawn::ServerStartDestroy, RespawnDelay);
	}
}

void ABaseWheeledVehiclePawn::MulticastDeath_Implementation()
{
	if (GetLocalRole() == ROLE_Authority)
	{
		PlayerStateRef->ServerPlayerDied();
	}

	HealthComponent->DestroyComponent();
}

void ABaseWheeledVehiclePawn::ServerStartDestroy_Implementation()
{
	Destroy();
}

// Override in the player vehicle class
void ABaseWheeledVehiclePawn::ClientUpdatePickup_Implementation(EPickupType PickupType)
{
}

void ABaseWheeledVehiclePawn::ClientUpdateWeaponState_Implementation(EWeaponState WeaponState)
{
}

void ABaseWheeledVehiclePawn::ClientUpdateAmmo_Implementation(int32 CurrentAmmo)
{
}

void ABaseWheeledVehiclePawn::ClientUpdateMagAmmo_Implementation(int32 CurrentMagAmmo)
{
}

void ABaseWheeledVehiclePawn::OnRep_CurrentWeapon()
{
}

void ABaseWheeledVehiclePawn::OnRep_IsAlive()
{
}
