// Copyright 2022 Danial Kamali. All Rights Reserved.

#include "PlayerWheeledVehiclePawn.h"
#include "MASK/MaskDriverCharacter.h"
#include "SilentValley/SilentValleyMission.h"
#include "MASK/MaskVehicleDefinition.h"
#include "Components/CapsuleComponent.h"
#include "ChaosWheeledVehicleMovementComponent.h"
#include "Actors/WeaponPickupActor.h"
#include "Camera/CameraComponent.h"
#include "Components/TimelineComponent.h"
#include "Components/WidgetComponent.h"
#include "Components/HealthComponent.h"
#include "Core/CustomGameMode.h"
#include "Core/OnlineGameInstance.h"
#include "Core/CustomPlayerState.h"
#include "GameFramework/SpringArmComponent.h"
#include "Kismet/KismetMathLibrary.h"
#include "Kismet/GameplayStatics.h"
#include "Net/UnrealNetwork.h"
#include "UI/InCarWidget.h"
#include "UI/PlayerHUD.h"

APlayerWheeledVehiclePawn::APlayerWheeledVehiclePawn(const FObjectInitializer& ObjectInitializer) : Super(ObjectInitializer)
{
	PrimaryActorTick.bStartWithTickEnabled = false;
	
	// Create a spring arm component for our chase camera
	SpringArmOutside = CreateDefaultSubobject<USpringArmComponent>(TEXT("Outside Spring Arm"));
	SpringArmOutside->SetRelativeLocation(FVector(0.0f, 0.0f, 35.0f));
	SpringArmOutside->SetupAttachment(RootComponent);
	SpringArmOutside->SetComponentTickEnabled(false);
	SpringArmOutside->SocketOffset = FVector(0.0f, 0.0f, 60.0f);
	SpringArmOutside->TargetArmLength = 250.0f;
	SpringArmOutside->bUsePawnControlRotation = false;
	SpringArmOutside->bInheritPitch = true;
	SpringArmOutside->bInheritYaw = true;
	SpringArmOutside->bInheritRoll = false;
	SpringArmOutside->bEnableCameraLag = true;
	SpringArmOutside->CameraLagMaxDistance = 50.0f;

	// Create the chase camera component 
	CameraOutside = CreateDefaultSubobject<UCameraComponent>(TEXT("Chase Camera"));
	CameraOutside->SetupAttachment(SpringArmOutside, USpringArmComponent::SocketName);
	CameraOutside->SetRelativeRotation(FRotator(-15.0f, 0.0f, 0.0f));
	CameraOutside->SetComponentTickEnabled(false);
	CameraOutside->SetIsReplicated(true);
	CameraOutside->bUsePawnControlRotation = false;

	SpringArmInside = CreateDefaultSubobject<USpringArmComponent>(TEXT("Inside Spring Arm"));
	SpringArmInside->SetRelativeLocation(FVector(0.0f, 0.0f, 40.0f));
	SpringArmInside->SetupAttachment(RootComponent);
	SpringArmInside->SetComponentTickEnabled(false);
	SpringArmInside->SocketOffset = FVector(0.0f, 0.0f, 5.0f);
	SpringArmInside->TargetArmLength = 25.0f;
	SpringArmInside->bUsePawnControlRotation = false;
	SpringArmInside->bInheritPitch = true;
	SpringArmInside->bInheritYaw = true;
	SpringArmInside->bInheritRoll = false;
	SpringArmInside->bEnableCameraLag = true;
	SpringArmInside->bEnableCameraRotationLag = true;
	SpringArmInside->CameraLagSpeed = 5.0f;
	SpringArmInside->CameraRotationLagSpeed = 20.0f;
	SpringArmInside->CameraLagMaxDistance = 2.5f;

	CameraInside = CreateDefaultSubobject<UCameraComponent>(TEXT("Internal Camera"));
	CameraInside->SetupAttachment(SpringArmInside, USpringArmComponent::SocketName);
	CameraInside->SetRelativeRotation(FRotator(-5.0f, 0.0f, 0.0f));
	CameraInside->SetComponentTickEnabled(false);
	CameraInside->SetIsReplicated(true);
	CameraInside->bUsePawnControlRotation = false;

	WidgetDashboard = CreateDefaultSubobject<UWidgetComponent>(TEXT("Dashboard Widget"));
	WidgetDashboard->SetupAttachment(GetMesh());
	WidgetDashboard->SetComponentTickEnabled(false);
	WidgetDashboard->SetRelativeLocation(FVector(35.0f, 0.0f, 20.0f));
	WidgetDashboard->SetRelativeRotation(FRotator(0.0f, -180.0f, 0.0f));
	WidgetDashboard->SetRelativeScale3D(FVector(0.05f, 0.05f, 0.05f));
	WidgetDashboard->SetDrawSize(FVector2D(300.0f, 150.0f));
	WidgetDashboard->SetGenerateOverlapEvents(false);
	WidgetDashboard->CanCharacterStepUpOn = ECB_No;

	ResetRotationTimeline = CreateDefaultSubobject<UTimelineComponent>(TEXT("Reset Rotation Timeline"));

	// Initialize variables
	CurrentCamera = CameraOutside;
	LookRightValue = LookUpValue = 0.0f;
	bAutoAdjustCamera = true;
	bCanAim = true;
	bInCarCamera = false;
	bAlwaysUpdateDashboard = false;
	bDoOnceResetRotation = true;
	bCanToggleCamera = true;
	ToggleCameraCooldown = 0.3f;
	bCanWakeRigidBodies = false;
}

void APlayerWheeledVehiclePawn::GetLifetimeReplicatedProps(TArray<FLifetimeProperty> &OutLifetimeProps) const
{
	Super::GetLifetimeReplicatedProps(OutLifetimeProps);
	DOREPLIFETIME(APlayerWheeledVehiclePawn,FleetTeamId);
	DOREPLIFETIME(APlayerWheeledVehiclePawn,DriverCharacter);

	// Replicate to everyone
	DOREPLIFETIME(APlayerWheeledVehiclePawn, PlayerControllerRef);
	DOREPLIFETIME(APlayerWheeledVehiclePawn, bCanAim);
	DOREPLIFETIME(APlayerWheeledVehiclePawn, bInCarCamera);
}

void APlayerWheeledVehiclePawn::SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);
	PlayerInputComponent->BindKey(EKeys::F6,IE_Pressed,this,&APlayerWheeledVehiclePawn::ServerRetryMission);

	// set up gameplay key bindings
	check(PlayerInputComponent);

	PlayerInputComponent->BindAxis("MoveForward", this, &APlayerWheeledVehiclePawn::MoveForward);
	PlayerInputComponent->BindAxis("MoveRight", this, &APlayerWheeledVehiclePawn::MoveRight);
	
	PlayerInputComponent->BindAxis("LookUp", this, &APlayerWheeledVehiclePawn::LookUp);
	PlayerInputComponent->BindAxis("LookRight", this, &APlayerWheeledVehiclePawn::LookRight);
	PlayerInputComponent->BindAxis("LookUpRate",this,&APlayerWheeledVehiclePawn::LookUpRate);
	PlayerInputComponent->BindAxis("LookRightRate",this,&APlayerWheeledVehiclePawn::LookRightRate);
	
	PlayerInputComponent->BindAction("FireWeapon", IE_Pressed, this, &APlayerWheeledVehiclePawn::StartFireWeapon);
	PlayerInputComponent->BindAction("FireWeapon", IE_Released, this, &APlayerWheeledVehiclePawn::StopFireWeapon);

	PlayerInputComponent->BindAction("Handbrake", IE_Pressed, this, &APlayerWheeledVehiclePawn::OnHandbrakePressed);
	PlayerInputComponent->BindAction("Handbrake", IE_Released, this, &APlayerWheeledVehiclePawn::OnHandbrakeReleased);
	
	PlayerInputComponent->BindAction("SwitchCamera", IE_Pressed, this, &APlayerWheeledVehiclePawn::ToggleCamera);
	
	PlayerInputComponent->BindAction("Jump", IE_Pressed, this, &APlayerWheeledVehiclePawn::TryToJump).bExecuteWhenPaused=true;

	PlayerInputComponent->BindAction("SwitchToPrimary", IE_Pressed, this, &APlayerWheeledVehiclePawn::SwitchToPrimary);
	PlayerInputComponent->BindAction("SwitchToSecondary", IE_Pressed, this, &APlayerWheeledVehiclePawn::SwitchToSecondary);
	// Escape already has a Quit/PIE-stop binding in the original Blueprint/editor.
	PlayerInputComponent->BindKey(EKeys::F10, IE_Pressed, this, &APlayerWheeledVehiclePawn::ReturnToMainMenu);
	PlayerInputComponent->BindKey(EKeys::Gamepad_LeftThumbstick,IE_Pressed,this,&APlayerWheeledVehiclePawn::RecenterCamera);
	PlayerInputComponent->BindKey(EKeys::Gamepad_FaceButton_Top,IE_Pressed,this,&APlayerWheeledVehiclePawn::CycleWeaponOrReturnToMenu).bExecuteWhenPaused=true;
	PlayerInputComponent->BindKey(EKeys::Gamepad_Special_Right,IE_Pressed,this,&APlayerWheeledVehiclePawn::TogglePauseMenu).bExecuteWhenPaused=true;
	PlayerInputComponent->BindKey(EKeys::Gamepad_FaceButton_Right,IE_Pressed,this,&APlayerWheeledVehiclePawn::ResumeFromPause).bExecuteWhenPaused=true;
	PlayerInputComponent->BindKey(EKeys::Gamepad_DPad_Up,IE_Pressed,this,&APlayerWheeledVehiclePawn::NextVehicle);
	PlayerInputComponent->BindKey(EKeys::Gamepad_DPad_Down,IE_Pressed,this,&APlayerWheeledVehiclePawn::PreviousVehicle);
	PlayerInputComponent->BindKey(EKeys::PageUp,IE_Pressed,this,&APlayerWheeledVehiclePawn::NextVehicle);
	PlayerInputComponent->BindKey(EKeys::PageDown,IE_Pressed,this,&APlayerWheeledVehiclePawn::PreviousVehicle);
	PlayerInputComponent->BindKey(EKeys::Gamepad_Special_Left,IE_Pressed,this,&APlayerWheeledVehiclePawn::ShowScoreboard).bExecuteWhenPaused=true;
	PlayerInputComponent->BindKey(EKeys::Gamepad_Special_Left,IE_Released,this,&APlayerWheeledVehiclePawn::HideScoreboard).bExecuteWhenPaused=true;
}
void APlayerWheeledVehiclePawn::ServerRetryMission_Implementation()
{
	if(auto* Mission=ASilentValleyMission::Find(GetWorld())) { Mission->Retry(Cast<APlayerController>(GetController())); }
}

void APlayerWheeledVehiclePawn::BeginPlay()
{
	Super::BeginPlay();
	LastCameraVehicleYaw=GetActorRotation().Yaw;
	InitializeLocalView();
	if(HasAuthority()) { GetWorld()->GetTimerManager().SetTimerForNextTick(this,&APlayerWheeledVehiclePawn::InitializeDriverCharacter); }
}

UMaskVehicleDefinition* APlayerWheeledVehiclePawn::GetDriverDefinition() const
{
	// The legacy demonstration sedan uses the existing Matt asset as its driver.
	return LoadObject<UMaskVehicleDefinition>(nullptr,TEXT("/Game/MASK/Thunderhawk/DA_Thunderhawk.DA_Thunderhawk"));
}
bool APlayerWheeledVehiclePawn::IsDriverOnFoot() const { return IsValid(DriverCharacter) && DriverCharacter->IsOnFoot(); }
void APlayerWheeledVehiclePawn::InitializeDriverCharacter()
{
	if(!HasAuthority() || DriverCharacter || !GetDriverDefinition()) { return; }
	DriverCharacter=GetWorld()->SpawnActorDeferred<AMaskDriverCharacter>(AMaskDriverCharacter::StaticClass(),GetActorTransform(),this,nullptr,ESpawnActorCollisionHandlingMethod::AlwaysSpawn);
	if(!DriverCharacter) { return; }
	DriverCharacter->InitializeDriver(this);DriverCharacter->FinishSpawning(GetActorTransform());RefreshDriverCharacter();ForceNetUpdate();
}
void APlayerWheeledVehiclePawn::RefreshDriverCharacter()
{
	if(IsValid(DriverCharacter)) { DriverCharacter->RefreshDriverState();DriverCharacterReady(); }
}
void APlayerWheeledVehiclePawn::DriverCharacterReady() {}
void APlayerWheeledVehiclePawn::EndPlay(const EEndPlayReason::Type Reason)
{
	if(HasAuthority() && IsValid(DriverCharacter) && !DriverCharacter->IsOnFoot()) { DriverCharacter->Destroy(); }
	Super::EndPlay(Reason);
}
bool APlayerWheeledVehiclePawn::CanDriverExit(FString& Reason) const
{
	const auto* Life=FindComponentByClass<UHealthComponent>();
	if(!Life || Life->CurrentHealth<=0.f || !IsValid(DriverCharacter) || IsDriverOnFoot()) { Reason=TEXT("Conducteur indisponible");return false; }
	if(GetMesh()->GetPhysicsLinearVelocity().Size()>15.f || GetMesh()->GetPhysicsAngularVelocityInRadians().Size()>.2f)
	{ Reason=TEXT("Arretez le vehicule avant de sortir");return false; }
	const auto* Move=CastChecked<UChaosWheeledVehicleMovementComponent>(GetVehicleMovement());int32 Contacts=0;
	for(int32 I=0;I<Move->Wheels.Num();++I) { Contacts+=Move->GetWheelState(I).bInContact?1:0; }
	const auto* Data=GetDriverDefinition();const bool Skids=Data && Data->VehicleCategory==EMaskVehicleCategory::HelicopterAirplane;
	if(Skids)
	{
		FCollisionQueryParams Query(SCENE_QUERY_STAT(SkidDriverExit),false,this);TArray<AActor*> Attached;GetAttachedActors(Attached,true,true);Query.AddIgnoredActors(Attached);FHitResult Hit;
		if(!GetWorld()->LineTraceSingleByChannel(Hit,GetActorLocation()+FVector(0,0,100),GetActorLocation()-FVector(0,0,400),ECC_Vehicle,Query) || GetActorLocation().Z-Hit.ImpactPoint.Z>40.f || Hit.ImpactNormal.Z<.7f)
		{ Reason=TEXT("Posez l'helicoptere avant de sortir");return false; }
	}
	if((!Skids && Contacts<2) || GetActorUpVector().Z<.8f) { Reason=TEXT("Posez le vehicule sur un sol praticable pour sortir");return false; }
	return true;
}
TArray<FVector> APlayerWheeledVehiclePawn::GetDriverExitOffsets() const
{
	const auto* Data=GetDriverDefinition();float Side=180.f;
	if(Data) { for(const auto& Wheel:Data->Wheels) { Side=FMath::Max(Side,static_cast<float>(FMath::Abs(Wheel.Center.Y))+75.f); } }
	const float CabinX=Data?static_cast<float>(Data->DriverLocation.X)-40.f:-40.f;
	return {FVector(CabinX,-Side,0),FVector(CabinX,Side,0),FVector(CabinX,-Side-65,0),FVector(CabinX,Side+65,0)};
}
void APlayerWheeledVehiclePawn::ServerRequestDriverExit_Implementation()
{
	auto* PC=Cast<APlayerController>(GetController());if(!PC || IsPauseMenuOpen()) { return; }
	FString Reason;if(!CanDriverExit(Reason)) { ClientVehicleSwitchFeedback(Reason);return; }
	FCollisionQueryParams GroundQuery(SCENE_QUERY_STAT(DriverExitGround),false,this);TArray<AActor*> Attached;GetAttachedActors(Attached,true,true);GroundQuery.AddIgnoredActors(Attached);
	FCollisionQueryParams SpaceQuery(SCENE_QUERY_STAT(DriverExitSpace),false,DriverCharacter);
	const auto* Wheels=CastChecked<UChaosWheeledVehicleMovementComponent>(GetVehicleMovement());
	float RoadZ=0.f;int32 Contacts=0;
	for(int32 I=0;I<Wheels->Wheels.Num();++I) { const auto& Wheel=Wheels->GetWheelState(I);if(Wheel.bInContact) { RoadZ+=Wheel.ContactPoint.Z;++Contacts; } }
	RoadZ/=FMath::Max(1,Contacts);
	const auto* ExitData=GetDriverDefinition();
	if(Contacts==0 && ExitData && ExitData->VehicleCategory==EMaskVehicleCategory::HelicopterAirplane)
	{
		FHitResult Ground;
		if(!GetWorld()->LineTraceSingleByChannel(Ground,GetActorLocation()+FVector(0,0,100),GetActorLocation()-FVector(0,0,400),ECC_Visibility,GroundQuery)) { return; }
		RoadZ=Ground.ImpactPoint.Z;
	}
	for(const FVector Local:GetDriverExitOffsets())
	{
		const FVector XY=GetActorTransform().TransformPosition(Local);FHitResult Ground;
		if(!GetWorld()->LineTraceSingleByChannel(Ground,XY+FVector(0,0,250),XY-FVector(0,0,400),ECC_Visibility,GroundQuery) || Ground.ImpactNormal.Z<.7f) { continue; }
		if(FMath::Abs(Ground.ImpactPoint.Z-RoadZ)>45.f) { continue; }
		const FVector Position=Ground.ImpactPoint+FVector(0,0,90);
		if(GetWorld()->OverlapBlockingTestByProfile(Position,FQuat::Identity,TEXT("Pawn"),FCollisionShape::MakeCapsule(34,88),SpaceQuery)) { continue; }
		DriverCharacter->LeaveVehicle(FTransform(FRotator(0,GetActorRotation().Yaw,0),Position),PC);
		GetVehicleMovementComponent()->SetThrottleInput(0);GetVehicleMovementComponent()->SetBrakeInput(1);GetVehicleMovementComponent()->SetHandbrakeInput(true);
		ClientVehicleSwitchFeedback(TEXT(""));return;
	}
	ClientVehicleSwitchFeedback(TEXT("Sortie bloquee : degagez un cote du vehicule"));
}

void APlayerWheeledVehiclePawn::PawnClientRestart()
{
	Super::PawnClientRestart();
	if (IsLocallyControlled())
	{
		bLocalViewInitialized=false;bGamepadCameraDriven=false;GamepadLook=FVector2D::ZeroVector;
		LastCameraVehicleYaw=GetActorRotation().Yaw;
		PlayerControllerRef=Cast<APlayerController>(GetController());
		ClientInitialize_Implementation();
	}
}

void APlayerWheeledVehiclePawn::InitializeLocalView()
{
	if (IsLocallyControlled() && !bLocalViewInitialized)
	{
		PlayerControllerRef = Cast<APlayerController>(GetController());
		if (!PlayerControllerRef) { return; }
		bLocalViewInitialized = true;
		// Both native cameras started active while their spring arms never ticked.
		// Select the actual viewpoint after possession, including cooked-client restart.
		CameraOutside->SetActive(!bInCarCamera);CameraInside->SetActive(bInCarCamera);
		SpringArmOutside->SetComponentTickEnabled(!bInCarCamera);
		SpringArmInside->SetComponentTickEnabled(bInCarCamera);
		if (bCanAim && bAutoAdjustCamera == false)
		{
			SpringArmOutside->bUsePawnControlRotation = true;
		}
	
		WidgetDashboard->InitWidget();
		WidgetRef = Cast<UInCarWidget>(WidgetDashboard->GetUserWidgetObject());
	
		if (ResetRotationCurve && !bCameraTimelineConfigured)
		{
			bCameraTimelineConfigured=true;
			FOnTimelineFloat TimelineProgress{};
			TimelineProgress.BindUFunction(this, FName("ResetControlRotation"));
			ResetRotationTimeline->AddInterpFloat(ResetRotationCurve, TimelineProgress, FName("Alpha"));
			FOnTimelineEvent TimelineFinishEvent{};
			TimelineFinishEvent.BindUFunction(this, FName("SetUseRotation"));
			ResetRotationTimeline->SetTimelineFinishedFunc(TimelineFinishEvent);
		}
	}
}

void APlayerWheeledVehiclePawn::PossessedBy(AController* NewController)
{
	Super::PossessedBy(NewController);
	if(bLoadoutInitialized && PlayerStateRef)
	{
		PlayerStateRef->PrimaryWeapon=StoredPrimary;PlayerStateRef->SecondaryWeapon=StoredSecondary;
	}
	
	FActorSpawnParameters SpawnParameters;
	SpawnParameters.Owner = this;
	SpawnParameters.Instigator = GetInstigator();
	SpawnParameters.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	
	if (!bLoadoutInitialized && PrimaryWeaponToAdd)
	{
		AWeaponPickupActor* Weapon1 = GetWorld()->SpawnActor<AWeaponPickupActor>(PrimaryWeaponToAdd, GetMesh()->GetSocketLocation(FName("PrimaryWeaponSocket")), GetActorRotation(), SpawnParameters);
		if (Weapon1)
		{
			ServerAddWeapon(Weapon1);
		}
	}
	
	if (!bLoadoutInitialized && SecondaryWeaponToAdd)
	{
		AWeaponPickupActor* Weapon2 = GetWorld()->SpawnActor<AWeaponPickupActor>(SecondaryWeaponToAdd, GetMesh()->GetSocketLocation(FName("SecondaryWeaponSocket")), GetActorRotation(), SpawnParameters);
		if (Weapon2)
		{
			ServerAddWeapon(Weapon2);
		}
	}

	bLoadoutInitialized=true;
	PlayerControllerRef = Cast<APlayerController>(NewController);
	if (PlayerControllerRef)
	{
		ClientInitialize();

		PlayerControllerRef->PlayerCameraManager->ViewPitchMax = 25.0f;
		PlayerControllerRef->PlayerCameraManager->ViewPitchMin = -20.0f;

		SetActorTickEnabled(true);
	}
}

void APlayerWheeledVehiclePawn::UnPossessed()
{
	if(HasAuthority())
	{
		ServerStopFireWeapon();
		if(PlayerStateRef) { StoredPrimary=PlayerStateRef->PrimaryWeapon;StoredSecondary=PlayerStateRef->SecondaryWeapon; }
	}
	GetVehicleMovementComponent()->SetThrottleInput(0.f);GetVehicleMovementComponent()->SetSteeringInput(0.f);
	GetVehicleMovementComponent()->SetBrakeInput(0.f);
	GetVehicleMovementComponent()->SetHandbrakeInput(false);
	bLocalViewInitialized=false;bGamepadCameraDriven=false;bPauseMenuOpen=false;GamepadLook=FVector2D::ZeroVector;
	PlayerHUDRef=nullptr;PlayerControllerRef=nullptr;
	Super::UnPossessed();
}

void APlayerWheeledVehiclePawn::CycleVehicle(int32 Direction) { if(!bPauseMenuOpen) { ServerCycleVehicle(Direction); } }
void APlayerWheeledVehiclePawn::NextVehicle() { CycleVehicle(1); }
void APlayerWheeledVehiclePawn::PreviousVehicle() { CycleVehicle(-1); }
void APlayerWheeledVehiclePawn::ServerCycleVehicle_Implementation(int32 Direction)
{
	if(auto* PC=Cast<APlayerController>(GetController()))
	{
		if(auto* GM=Cast<ACustomGameMode>(GetWorld()->GetAuthGameMode())) { GM->CyclePlayerVehicle(PC,Direction>=0?1:-1); }
	}
}
void APlayerWheeledVehiclePawn::ClientVehicleSwitchFeedback_Implementation(const FString& Message) { VehicleSwitchStatus=Message; }

void APlayerWheeledVehiclePawn::ClientInitialize_Implementation()
{
	InitializeLocalView();
	if (!PlayerControllerRef) { return; }
	PlayerControllerRef->SetInputMode(FInputModeGameOnly());
	PlayerControllerRef->bShowMouseCursor = false;
	PlayerControllerRef->PlayerCameraManager->ViewPitchMax = 25.0f;
	PlayerControllerRef->PlayerCameraManager->ViewPitchMin = -20.0f;

	PlayerHUDRef = Cast<APlayerHUD>(PlayerControllerRef->GetHUD());
	if (PlayerHUDRef)
	{
		PlayerHUDRef->EnsureInitialized();
		PlayerHUDRef->SetOnFootMode(false);
		OnRep_CurrentWeapon();
		if (const UHealthComponent* Health = FindComponentByClass<UHealthComponent>())
		{
			PlayerHUDRef->UpdateHealth(Health->MaxHealth > 0.f ? Health->CurrentHealth / Health->MaxHealth : 0.f);
		}
	}

	SetActorTickEnabled(true);
}

void APlayerWheeledVehiclePawn::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if(IsDriverOnFoot()) { GetVehicleMovementComponent()->SetThrottleInput(0);GetVehicleMovementComponent()->SetSteeringInput(0);GetVehicleMovementComponent()->SetBrakeInput(1);GetVehicleMovementComponent()->SetHandbrakeInput(true); }
	
	if (bCanAim && CurrentWeapon && PlayerControllerRef && GetLocalRole() == ROLE_Authority)
	{
		if (bInCarCamera == false)
		{
			const FRotator Rotation = UKismetMathLibrary::FindLookAtRotation(CurrentWeapon->GetActorLocation(), PlayerControllerRef->PlayerCameraManager->GetCameraLocation());
			CurrentWeapon->SetActorRotation(FRotator(0.0f, Rotation.Yaw + 90.0f, Rotation.Pitch));
		}
	}
	
	if (IsLocallyControlled() && PlayerControllerRef)
	{
		InitializeLocalView();
		const bool PadLookActive=!GamepadLook.IsNearlyZero(.01f);
		if (!bPauseMenuOpen && (PadLookActive || bGamepadCameraDriven))
		{
			if (!bGamepadCameraDriven)
			{
				GetWorld()->GetTimerManager().ClearTimer(ResetRotationTimer);ResetRotationTimeline->Stop();
				PlayerControllerRef->SetControlRotation((bInCarCamera?SpringArmInside:SpringArmOutside)->GetComponentRotation());
			}
			bGamepadCameraDriven=true;
			FRotator View=PlayerControllerRef->GetControlRotation();
			View.Yaw+=FMath::FindDeltaAngleDegrees(LastCameraVehicleYaw,GetActorRotation().Yaw)+GamepadLook.X*100.f*DeltaSeconds;
			View.Pitch=FMath::Clamp(FRotator::NormalizeAxis(View.Pitch)+GamepadLook.Y*65.f*DeltaSeconds,bInCarCamera?-25.f:-50.f,bInCarCamera?30.f:50.f);
			PlayerControllerRef->SetControlRotation(View);
			SpringArmOutside->bUsePawnControlRotation=!bInCarCamera;SpringArmInside->bUsePawnControlRotation=bInCarCamera;
			PlayerControllerRef->PlayerCameraManager->ViewPitchMax=bInCarCamera?30.f:50.f;
			PlayerControllerRef->PlayerCameraManager->ViewPitchMin=bInCarCamera?-25.f:-50.f;
		}
		LastCameraVehicleYaw=GetActorRotation().Yaw;
		if (bCanAim && bAutoAdjustCamera && !bGamepadCameraDriven)
		{
			if (bDoOnceResetRotation && LookUpValue == 0.0f && LookRightValue == 0.0f)
			{
				bDoOnceResetRotation = false;
				GetWorld()->GetTimerManager().SetTimer(ResetRotationTimer, this, &APlayerWheeledVehiclePawn::PlayResetTimeline, 1.0f);
			}
			else if (bDoOnceResetRotation != true && (LookUpValue != 0.0f || LookRightValue != 0.0f))
			{
				PlayerControllerRef->SetControlRotation(SpringArmOutside->GetComponentRotation());
				SpringArmOutside->bUsePawnControlRotation = true;
				GetWorld()->GetTimerManager().ClearTimer(ResetRotationTimer);
				ResetRotationTimeline->Stop();
				bDoOnceResetRotation = true;
			}
		}

		// Only wake rigid bodies when the player is trying to move after a full stop
		if (GetVelocity().Size() < 1.0f)
		{
			bCanWakeRigidBodies = true;
		}
		else
		{
			bCanWakeRigidBodies = false;
		}
	
		UpdateUI();
	}
}

void APlayerWheeledVehiclePawn::ReturnToMainMenu()
{
	if (bPauseMenuOpen) { bPauseMenuOpen=false;UGameplayStatics::SetGamePaused(this,false); }
	if (IsLocallyControlled())
	{
		if (auto* GI = Cast<UOnlineGameInstance>(GetGameInstance())) { GI->ReturnToMainMenu(); }
	}
}

void APlayerWheeledVehiclePawn::MoveForward(float Value)
{
	if (bPauseMenuOpen) { GetVehicleMovementComponent()->SetHandbrakeInput(true);GetVehicleMovementComponent()->SetThrottleInput(0.f);GetVehicleMovementComponent()->SetBrakeInput(0.f);return; }
	// LT intentionally becomes reverse after stopping. A held handbrake must
	// override it, otherwise LT+LB keeps driving a high-torque truck backwards.
	if(GetVehicleMovementComponent()->GetHandbrakeInput())
	{
		GetVehicleMovementComponent()->SetThrottleInput(0.f);GetVehicleMovementComponent()->SetBrakeInput(0.f);return;
	}
	if (bIsAlive)
	{
		if (Value != 0.0f && bCanWakeRigidBodies)
		{
			GetVehicleMovementComponent()->UpdatedPrimitive->WakeAllRigidBodies();
			ServerWakeRigidBodies();
			bCanWakeRigidBodies = false;
		}
		
		if (Value > 0)
		{
			GetVehicleMovementComponent()->SetThrottleInput(Value);
			GetVehicleMovementComponent()->SetBrakeInput(0.0f);
		}
		else
		{
			GetVehicleMovementComponent()->SetThrottleInput(0.0f);
			GetVehicleMovementComponent()->SetBrakeInput(-Value);
		}

		if (bBoostSpeed && !UsesPhysicalPowerBoost())
		{
			const FVector CurrentVelocity = GetVehicleMovementComponent()->UpdatedComponent->GetComponentVelocity();
			GetVehicleMovementComponent()->UpdatedComponent->ComponentVelocity = CurrentVelocity * SpeedBoostMultiplier;
		}
	}
}

void APlayerWheeledVehiclePawn::MoveRight(float Value)
{
	if (bPauseMenuOpen) { return; }
	if (bIsAlive)
	{
		GetVehicleMovementComponent()->SetSteeringInput(Value);
	}
}

void APlayerWheeledVehiclePawn::LookUp(float Value)
{
	if (bPauseMenuOpen) { return; }
	LookUpValue = Value;
	AddControllerPitchInput(Value);
}

void APlayerWheeledVehiclePawn::LookRight(float Value)
{
	if (bPauseMenuOpen) { return; }
	// Limit rotation of In-Car Camera
	// if (bInCarCamera)
	// {
	// 	// clamp view yaw between -50 and 50
	// 	float ControlYaw = PlayerControllerRef->GetControlRotation().Yaw;
	// 	if (ControlYaw > 180.0f)
	// 	{
	// 		ControlYaw = ControlYaw - 360.0f;
	// 	}
	//
	// 	const float ActorYaw = GetActorRotation().Yaw;
	// 	if (ActorYaw > ControlYaw - (50.0f - Value) && ActorYaw < ControlYaw + (50.0f - Value))
	// 	{
	// 		LookRightValue = Value;
	// 		AddControllerYawInput(Value);
	// 	}
	//
	// 	if (ActorYaw > ControlYaw - 60.0f && ActorYaw < ControlYaw + 60.0f)
	// 	{
	// 		SpringArmInside->bUsePawnControlRotation = false;
	// 	}
	// }
	// else
	// {
		LookRightValue = Value;
		AddControllerYawInput(Value);
	// }
}

void APlayerWheeledVehiclePawn::ServerWakeRigidBodies_Implementation()
{
	GetVehicleMovementComponent()->UpdatedPrimitive->WakeAllRigidBodies();
}

void APlayerWheeledVehiclePawn::StartFireWeapon()
{
	if (bPauseMenuOpen) { return; }
	UE_LOG(LogTemp, Log, TEXT("VC_FIRE local allowed=%d weapon=%s magazine=%d reserve=%d"), CanFireWeapon(), *GetNameSafe(CurrentWeapon), CurrentWeapon ? CurrentWeapon->CurrentMagazineAmmo : -1, CurrentWeapon ? CurrentWeapon->CurrentAmmo : -1);
	if (CanFireWeapon())
	{
		AddRecoil();
		ServerStartFireWeapon();

		if (CurrentWeapon->bIsAutomatic)
		{
			GetWorld()->GetTimerManager().SetTimer(RecoilTimer, this, &APlayerWheeledVehiclePawn::AddRecoil, CurrentWeapon->TimeBetweenShots, true);
		}
	}
}

void APlayerWheeledVehiclePawn::StopFireWeapon()
{
	if (CurrentWeapon)
	{
		GetWorld()->GetTimerManager().ClearTimer(RecoilTimer);
		ServerStopFireWeapon();
	}
}

void APlayerWheeledVehiclePawn::ClientUpdateWeaponState_Implementation(EWeaponState WeaponState)
{
	if (PlayerHUDRef)
	{
		PlayerHUDRef->UpdateWeaponState(WeaponState);
	}
}

void APlayerWheeledVehiclePawn::ClientUpdateAmmo_Implementation(int32 CurrentAmmo)
{
	if (PlayerHUDRef)
	{
		PlayerHUDRef->UpdateAmmo(CurrentAmmo);
	}
}

void APlayerWheeledVehiclePawn::ClientUpdateMagAmmo_Implementation(int32 CurrentMagAmmo)
{
	if (PlayerHUDRef)
	{
		PlayerHUDRef->UpdateMagAmmo(CurrentMagAmmo);
	}
}

void APlayerWheeledVehiclePawn::AddRecoil()
{
	if (CanFireWeapon())
	{
		PlayerControllerRef->ClientStartCameraShake(CurrentWeapon->Effects.CameraShake);
		PlayerHUDRef->AddCrosshairRecoil(CurrentWeapon->RecoilData.CrosshairRecoil, CurrentWeapon->RecoilData.ControlTime);
	}
	else
	{
		GetWorld()->GetTimerManager().ClearTimer(RecoilTimer);
	}
}

void APlayerWheeledVehiclePawn::PlayResetTimeline()
{
	ResetRotationTimeline->PlayFromStart();
}

void APlayerWheeledVehiclePawn::ResetControlRotation(float Value)
{
	PlayerControllerRef->SetControlRotation(UKismetMathLibrary::RLerp(PlayerControllerRef->GetControlRotation(), GetActorRotation(), Value, true));
}

void APlayerWheeledVehiclePawn::SetUseRotation()
{
	SpringArmOutside->bUsePawnControlRotation = false;
}

void APlayerWheeledVehiclePawn::OnHandbrakePressed()
{
	GetVehicleMovementComponent()->SetHandbrakeInput(true);
}

void APlayerWheeledVehiclePawn::OnHandbrakeReleased()
{
	GetVehicleMovementComponent()->SetHandbrakeInput(false);
}

void APlayerWheeledVehiclePawn::TryToJump()
{
	if(bPauseMenuOpen) { ResumeFromPause();return; }
	if(bIsAlive) { ServerRequestDriverExit(); }
}

void APlayerWheeledVehiclePawn::LookUpRate(float Value) { GamepadLook.Y=bPauseMenuOpen?0.f:Value; }
void APlayerWheeledVehiclePawn::LookRightRate(float Value) { GamepadLook.X=bPauseMenuOpen?0.f:Value; }

void APlayerWheeledVehiclePawn::RecenterCamera()
{
	if (!PlayerControllerRef || bPauseMenuOpen) { return; }
	bGamepadCameraDriven=false;GamepadLook=FVector2D::ZeroVector;
	GetWorld()->GetTimerManager().ClearTimer(ResetRotationTimer);ResetRotationTimeline->Stop();
	PlayerControllerRef->SetControlRotation(GetActorRotation());
	SpringArmOutside->bUsePawnControlRotation=false;SpringArmInside->bUsePawnControlRotation=false;
}

void APlayerWheeledVehiclePawn::CycleWeaponOrReturnToMenu()
{
	if (bPauseMenuOpen) { ReturnToMainMenu();return; }
	if(HandleVehicleWeaponModifier()) { return; }
	if (CurrentWeaponSlot==EWeaponToDo::Primary) { SwitchToSecondary(); } else { SwitchToPrimary(); }
}

void APlayerWheeledVehiclePawn::TogglePauseMenu()
{
	if (!IsLocallyControlled()) { return; }
	bPauseMenuOpen=!bPauseMenuOpen;
	GetVehicleMovementComponent()->SetHandbrakeInput(bPauseMenuOpen);
	if (bPauseMenuOpen)
	{
		StopFireWeapon();GamepadLook=FVector2D::ZeroVector;
		GetVehicleMovementComponent()->SetThrottleInput(0.f);GetVehicleMovementComponent()->SetBrakeInput(0.f);
	}
	if (GetNetMode()==NM_Standalone) { UGameplayStatics::SetGamePaused(this,bPauseMenuOpen); }
}

void APlayerWheeledVehiclePawn::ResumeFromPause() { if (bPauseMenuOpen) { TogglePauseMenu(); } }
void APlayerWheeledVehiclePawn::ToggleControlsHelp() { if (PlayerHUDRef) { PlayerHUDRef->bShowXboxControls=!PlayerHUDRef->bShowXboxControls; } }
void APlayerWheeledVehiclePawn::ShowScoreboard() { if (PlayerHUDRef) { PlayerHUDRef->bShowPlayerScores=true; } }
void APlayerWheeledVehiclePawn::HideScoreboard() { if (PlayerHUDRef) { PlayerHUDRef->bShowPlayerScores=false; } }

void APlayerWheeledVehiclePawn::ClientUpdatePickup_Implementation(EPickupType PickupType)
{
	if (PlayerHUDRef)
	{
		PlayerHUDRef->PickupMessage(PickupType);
	}
}

void APlayerWheeledVehiclePawn::OnRep_CurrentWeapon()
{
	// Only on client
	if (PlayerHUDRef && IsLocallyControlled())
	{
		PlayerHUDRef->UpdateWeaponState(EWeaponState::Idle);

		if (CurrentWeapon)
		{
			PlayerHUDRef->UpdateCurrentWeapon(CurrentWeapon->WeaponName);
			ClientUpdateAmmo(CurrentWeapon->CurrentAmmo);
			PlayerHUDRef->UpdateMagAmmo(CurrentWeapon->CurrentMagazineAmmo);
			
			if (CurrentWeapon->CurrentMagazineAmmo <= 0)
			{
				PlayerHUDRef->UpdateWeaponState(EWeaponState::NoAmmo);
			}
		}
		else
		{
			PlayerHUDRef->UpdateCurrentWeapon(EWeaponName::NoName);
		}
	}
}

void APlayerWheeledVehiclePawn::SwitchToPrimary()
{
	if (bIsAlive && CurrentWeaponSlot != EWeaponToDo::Primary && PlayerStateRef->PrimaryWeapon)
	{
		ServerSwitchWeapon(EWeaponToDo::Primary);
	}
}

void APlayerWheeledVehiclePawn::SwitchToSecondary()
{
	if (bIsAlive && CurrentWeaponSlot != EWeaponToDo::Secondary && PlayerStateRef->SecondaryWeapon)
	{
		ServerSwitchWeapon(EWeaponToDo::Secondary);
	}
}

void APlayerWheeledVehiclePawn::ToggleCamera()
{
	if (bCanToggleCamera && bIsAlive)
	{
		ServerToggleCamera();

		bCanToggleCamera = false;
		GetWorld()->GetTimerManager().SetTimer(ToggleCameraTimer, this, &APlayerWheeledVehiclePawn::ResetToggleCamera, ToggleCameraCooldown);
	}
}

void APlayerWheeledVehiclePawn::ResetToggleCamera()
{
	bCanToggleCamera = true;
}

void APlayerWheeledVehiclePawn::ServerToggleCamera_Implementation()
{
	if (bIsAlive)
	{
		bInCarCamera = !bInCarCamera;
		if (bInCarCamera)
		{
			if (CurrentWeapon && CurrentWeaponSlot != EWeaponToDo::NoWeapon)
			{
				CurrentWeapon->SetActorRelativeRotation(FRotator::ZeroRotator);
			}

			CurrentCamera = CameraInside;
			ClientUpdateCurrentCamera(true);
			// PlayerControllerRef->PlayerCameraManager->ViewYawMax = 50.0f;
			// PlayerControllerRef->PlayerCameraManager->ViewYawMin = -50.0f;
			PlayerControllerRef->PlayerCameraManager->ViewPitchMax = 20.0f;
			PlayerControllerRef->PlayerCameraManager->ViewPitchMin = -20.0f;
		}
		else
		{
			CurrentCamera = CameraOutside;
			ClientUpdateCurrentCamera(false);
			// PlayerControllerRef->PlayerCameraManager->ViewYawMax = 359.99f;
			// PlayerControllerRef->PlayerCameraManager->ViewYawMin = 0.0f;
			PlayerControllerRef->PlayerCameraManager->ViewPitchMax = 25.0f;
			PlayerControllerRef->PlayerCameraManager->ViewPitchMin = -20.0f;
		}
	}
}

void APlayerWheeledVehiclePawn::ClientUpdateCurrentCamera_Implementation(bool bInCar)
{
	SpringArmOutside->SetComponentTickEnabled(!bInCar);
	SpringArmInside->SetComponentTickEnabled(bInCar);
	if (bInCar)
	{
		if (PlayerHUDRef)
		{
			PlayerHUDRef->SetUIState(true);
		}
		
		CameraOutside->Deactivate();
		CameraInside->Activate();
		PlayerControllerRef->PlayerCameraManager->ViewPitchMax = 20.0f;
		PlayerControllerRef->PlayerCameraManager->ViewPitchMin = -20.0f;
	}
	else
	{
		CameraInside->Deactivate();
		CameraOutside->Activate();
		PlayerControllerRef->PlayerCameraManager->ViewPitchMax = 25.0f;
		PlayerControllerRef->PlayerCameraManager->ViewPitchMin = -20.0f;
		
		if (PlayerHUDRef)
		{
			PlayerHUDRef->SetUIState(false);
		}
	}
}

void APlayerWheeledVehiclePawn::UpdateUI() const
{
	const float KPH = FMath::Abs(GetVehicleMovement()->GetForwardSpeed()) * 0.036f;
	if (WidgetRef && (bAlwaysUpdateDashboard || bInCarCamera))
	{
		WidgetRef->UpdateSpeedAndGear(FMath::FloorToInt(KPH), GetVehicleMovement()->GetCurrentGear());
	}
	if (bInCarCamera == false && PlayerHUDRef)
	{
		PlayerHUDRef->UpdateSpeedAndGear(FMath::FloorToInt(KPH), GetVehicleMovement()->GetCurrentGear());
	}
}

void APlayerWheeledVehiclePawn::ServerSetHealthLevel_Implementation(float CurrentHealth, float MaxHealth)
{
	Super::ServerSetHealthLevel_Implementation(CurrentHealth, MaxHealth);
	
	ClientUpdateHealth(CurrentHealth / MaxHealth);
}

void APlayerWheeledVehiclePawn::ClientUpdateHealth_Implementation(float NewHealth)
{
	if (PlayerHUDRef)
	{
		PlayerHUDRef->UpdateHealth(NewHealth);
	}
}

void APlayerWheeledVehiclePawn::Destroyed()
{
	if (GetLocalRole() == ROLE_Authority)
	{
		// In case of player leave the session without getting killed
		if (bIsAlive)
		{
			bIsAlive = false;
			OnRep_IsAlive();
		}

		// Get player controller reference before destroying the player
		AController* RespawnControllerRef = GetController();
	
		Super::Destroyed();

		// Get the World and GameMode in the world to invoke its restart player function.
		ACustomGameMode* GameMode = Cast<ACustomGameMode>(GetWorld()->GetAuthGameMode());
		if (GameMode)
		{
			GameMode->ServerStartRespawn(RespawnControllerRef);
		}
	}
}

void APlayerWheeledVehiclePawn::OnRep_IsAlive()
{
	if (bIsAlive == false && bInCarCamera && GetLocalRole() == ROLE_Authority)
	{
		if (PlayerControllerRef)
		{
			ClientUpdateCurrentCamera(false);
			PlayerControllerRef->PlayerCameraManager->ViewPitchMax = 25.0f;
			PlayerControllerRef->PlayerCameraManager->ViewPitchMin = -20.0f;
		}
	}
}
