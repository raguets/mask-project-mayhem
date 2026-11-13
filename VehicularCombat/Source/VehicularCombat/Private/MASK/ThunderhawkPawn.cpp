#include "MASK/ThunderhawkPawn.h"
#include "MASK/MaskVehicleDefinition.h"
#include "MASK/MaskVehicleModeComponent.h"
#include "MASK/MaskDynamicsComponent.h"
#include "MASK/MaskVehicleMovementComponent.h"
#include "MASK/MaskDriverCharacter.h"
#include "SilentValley/SilentValleyMission.h"
#include "ChaosWheeledVehicleMovementComponent.h"
#include "Components/InputComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/WidgetComponent.h"
#include "Animation/AnimSequence.h"
#include "Camera/CameraComponent.h"
#include "Net/UnrealNetwork.h"
#include "Engine/World.h"
#include "Engine/SkeletalMesh.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/GameStateBase.h"
#include "GameFramework/SpringArmComponent.h"

UThunderhawkFrontWheel::UThunderhawkFrontWheel()
{
	WheelRadius=32.8f;WheelWidth=24.f;MaxSteerAngle=35.f;bAffectedBySteering=true;
	SuspensionMaxRaise=8.f;SuspensionMaxDrop=12.f;SpringRate=280.f;SpringPreload=50.f;
	SuspensionDampingRatio=.65f;FrictionForceMultiplier=1.15f;
}
UThunderhawkRearWheel::UThunderhawkRearWheel()
{
	WheelRadius=32.8f;WheelWidth=24.f;MaxSteerAngle=0.f;bAffectedBySteering=false;
	bAffectedByEngine=true;bAffectedByHandbrake=true;
	SuspensionMaxRaise=8.f;SuspensionMaxDrop=12.f;SpringRate=280.f;SpringPreload=50.f;
	SuspensionDampingRatio=.65f;FrictionForceMultiplier=1.15f;
}

AThunderhawkPawn::AThunderhawkPawn(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer.SetDefaultSubobjectClass<UMaskVehicleMovementComponent>(AWheeledVehiclePawn::VehicleMovementComponentName))
{
	PrimaryActorTick.bStartWithTickEnabled=true;
	Modes=CreateDefaultSubobject<UMaskVehicleModeComponent>(TEXT("VehicleModes"));
 Dynamics=CreateDefaultSubobject<UMaskDynamicsComponent>(TEXT("VehicleDynamics"));
	Matt=CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("MattTrakker"));Matt->SetupAttachment(GetMesh());
	MattHair=CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("MattHair"));MattHair->SetupAttachment(Matt);
	Spectrum=CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("Spectrum"));Spectrum->SetupAttachment(Matt);
	Passenger=CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("Passenger"));Passenger->SetupAttachment(GetMesh());
	PassengerHair=CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("PassengerHair"));PassengerHair->SetupAttachment(Passenger);
	PassengerMask=CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("PassengerMask"));PassengerMask->SetupAttachment(Passenger);
	for (auto* Part : {Matt.Get(),MattHair.Get(),Spectrum.Get(),Passenger.Get(),PassengerHair.Get(),PassengerMask.Get()})
	{
		Part->SetCollisionEnabled(ECollisionEnabled::NoCollision);Part->SetGenerateOverlapEvents(false);
	}
	Matt->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
	Passenger->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
}

void AThunderhawkPawn::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);
	if (!Definition) { Definition=LoadObject<UMaskVehicleDefinition>(nullptr,DefaultDefinitionPath()); }
	if (!Definition || !Definition->Chassis) { return; }
	// Set final wheel definitions before swapping meshes, because that swap can
	// immediately recreate Chaos and otherwise evaluates old names on the new rig.
	auto* Movement=CastChecked<UChaosWheeledVehicleMovementComponent>(GetVehicleMovement());
	Movement->WheelSetups.SetNum(4);
	const FName Bones[]={TEXT("wheel_FL"),TEXT("wheel_FR"),TEXT("wheel_RL"),TEXT("wheel_RR")};
	for (int32 I=0;I<4;++I)
	{
		Movement->WheelSetups[I].BoneName=Bones[I];Movement->WheelSetups[I].AdditionalOffset=FVector::ZeroVector;
		Movement->WheelSetups[I].WheelClass=I<2 ? UThunderhawkFrontWheel::StaticClass() : UThunderhawkRearWheel::StaticClass();
	}
	if (!Definition->Wheels.IsEmpty())
	{
		Movement->WheelSetups.SetNum(Definition->Wheels.Num());
		for(int32 I=0;I<Definition->Wheels.Num();++I)
		{
			Movement->WheelSetups[I].BoneName=FName(*(TEXT("wheel_")+Definition->Wheels[I].Name.ToString()));
			Movement->WheelSetups[I].AdditionalOffset=FVector::ZeroVector;
			Movement->WheelSetups[I].WheelClass=Definition->Wheels[I].WheelClass;
		}
	}
	Movement->Mass=Definition->MassKg;Movement->DownforceCoefficient=0.f;Movement->DragCoefficient=0.f;
 Movement->ThrottleInputRate.RiseRate=2.f;Movement->ThrottleInputRate.FallRate=4.f;
	Movement->SteeringInputRate.RiseRate=5.f;Movement->SteeringInputRate.FallRate=7.f;
	// Keep full lock for recovery/parking; progressively soften it at road speed.
	auto* Steering=Movement->SteeringSetup.SteeringCurve.GetRichCurve();Steering->Reset();
	Steering->AddKey(0.f,1.f);Steering->AddKey(20.f,1.f);Steering->AddKey(60.f,.65f);Steering->AddKey(120.f,.3f);
	if(Definition->Dynamics.bTwoWheelRoadBalance)
	{
		Movement->SteeringInputRate.RiseRate=2.f;Movement->SteeringInputRate.FallRate=3.f;
		Steering->Reset();Steering->AddKey(0.f,.7f);Steering->AddKey(20.f,.5f);Steering->AddKey(60.f,.2f);Steering->AddKey(120.f,.08f);
	}
	Movement->TransmissionSetup.ForwardGearRatios={3.8f,2.4f,1.6f,1.15f,.85f};
	Movement->TransmissionSetup.ReverseGearRatios={3.8f};
	Movement->TransmissionSetup.FinalRatio=3.4f;
	Movement->TransmissionSetup.ChangeDownRPM=2500.f;
	Movement->TransmissionSetup.GearChangeTime=.2f;
	// A broad low-rpm torque band supports hill starts on the existing driven tires.
	auto* TorqueCurve=Movement->EngineSetup.TorqueCurve.GetRichCurve();TorqueCurve->Reset();
	const float MaxRPM=Movement->EngineSetup.MaxRPM;
	TorqueCurve->AddKey(0.f,.8f);TorqueCurve->AddKey(MaxRPM*.25f,1.f);
	TorqueCurve->AddKey(MaxRPM*.7f,1.f);TorqueCurve->AddKey(MaxRPM,.8f);
	if(Definition->bOverrideCenterOfMass)
	{
		Movement->bEnableCenterOfMassOverride=true;
		Movement->CenterOfMassOverride=Definition->Chassis->GetRefSkeleton().GetRefBonePose()[0].InverseTransformPosition(Definition->CenterOfMass);
	}
	Movement->EngineSetup.MaxTorque=Definition->EngineTorque>0.f?Definition->EngineTorque:Definition->MassKg*.35f;
	GetMesh()->SetSkeletalMesh(Definition->Chassis);
	GetMesh()->SetPhysicsAsset(Definition->Chassis->GetPhysicsAsset(),true);
	GetMesh()->SetAnimInstanceClass(nullptr);
	// VehicleMesh IS the actor root: resetting its relative transform would move
	// the spawned physics body back to world origin without a physics teleport.
	// A hidden physics proxy must also leave the depth pass. Otherwise its box
	// occludes the real hood/trunk and appears as black rectangular patches.
	GetMesh()->SetRenderInMainPass(false);GetMesh()->SetRenderInDepthPass(false);GetMesh()->SetCastShadow(false);
	GetMesh()->SetVisibleInRayTracing(false);
	GetMesh()->bReplicatePhysicsToAutonomousProxy=true;
	Matt->SetSkeletalMesh(Definition->Driver);MattHair->SetSkeletalMesh(Definition->Hair);Spectrum->SetSkeletalMesh(Definition->Mask);
	MattHair->SetLeaderPoseComponent(Matt);Spectrum->SetLeaderPoseComponent(Matt);
	Passenger->SetSkeletalMesh(Definition->Passenger);PassengerHair->SetSkeletalMesh(Definition->PassengerHair);PassengerMask->SetSkeletalMesh(Definition->PassengerMask);
	PassengerHair->SetLeaderPoseComponent(Passenger);PassengerMask->SetLeaderPoseComponent(Passenger);
	Modes->Duration=Definition->TransformSeconds*.5f;Modes->bSupportsFlight=Definition->bSupportsFlight;
	Modes->ClearanceCenter=Definition->ClearanceCenter;Modes->ClearanceExtent=Definition->ClearanceExtent;
	TArray<USpringArmComponent*> Arms;GetComponents(Arms);
	for (auto* Arm:Arms)
	{
		if (Arm->GetFName()==TEXT("Outside Spring Arm")) { Arm->TargetArmLength=Definition->ChaseDistance;Arm->SetRelativeLocation(Definition->ChaseLocation); }
		else if (Arm->GetFName()==TEXT("Inside Spring Arm"))
		{
			Arm->TargetArmLength=0.f;Arm->SocketOffset=FVector::ZeroVector;Arm->SetRelativeLocation(Definition->CockpitLocation);
			Arm->SetRelativeRotation(FRotator::ZeroRotator);Arm->bDoCollisionTest=false;
		}
	}
	TArray<UCameraComponent*> Cameras;GetComponents(Cameras);
	for (auto* Camera:Cameras)
	{
		// The copied sedan Blueprint has its own cockpit camera transform. Use the
		// Thunderhawk eye point rather than inheriting that unrelated cabin framing.
		if (Camera->GetFName()==TEXT("Internal Camera"))
		{
			Camera->SetRelativeLocation(FVector::ZeroVector);Camera->SetRelativeRotation(FRotator(-5,0,0));
		}
	}
}

void AThunderhawkPawn::BeginPlay()
{
	Super::BeginPlay();
	if (!Definition) { UE_LOG(LogTemp,Error,TEXT("Thunderhawk definition missing"));return; }
	// Construction replaces the mesh and wheel definitions inherited from the old
	// Blueprint. Rebuild the simulation from that final configuration, explicitly.
	GetMesh()->SetCollisionProfileName(TEXT("Vehicle"));
	GetMesh()->SetEnableGravity(true);GetMesh()->SetSimulatePhysics(true);
	GetMesh()->RecreatePhysicsState();GetVehicleMovement()->RecreatePhysicsState();
	GetMesh()->SetAllBodiesSimulatePhysics(true);GetMesh()->WakeAllRigidBodies();
	UE_LOG(LogTemp,Display,TEXT("MASK_PHYS sim=%d mass=%.2f root=%s wheelFL=%s actor=%s"),GetMesh()->IsSimulatingPhysics(),GetMesh()->GetMass(),
		*GetMesh()->GetBoneName(0).ToString(),*GetMesh()->GetBoneLocation(TEXT("wheel_FL"),EBoneSpaces::ComponentSpace).ToString(),*GetActorLocation().ToString());
	for (const auto& Part : Definition->Parts)
	{
		auto* Component=NewObject<UStaticMeshComponent>(this,Part.Name);
		Component->SetStaticMesh(Part.Mesh);Component->SetupAttachment(GetMesh());Component->SetMobility(EComponentMobility::Movable);
		Component->SetCollisionEnabled(ECollisionEnabled::NoCollision);Component->SetGenerateOverlapEvents(false);
		Component->RegisterComponent();AddInstanceComponent(Component);VisualParts.Add(Component);
	}
	if (HasAuthority()) { bMaskVisible=true; }
	ApplyPilotState();
	// The original abstract dashboard is not the Thunderhawk instrument panel.
	TArray<UWidgetComponent*> Widgets;GetComponents(Widgets);
	for (auto* Widget : Widgets) { Widget->SetVisibility(false); }
	UE_LOG(LogTemp,Display,TEXT("MASK_THUNDERHAWK initialized parts=%d wheels=%d"),VisualParts.Num(),CastChecked<UChaosWheeledVehicleMovementComponent>(GetVehicleMovement())->WheelSetups.Num());
}

void AThunderhawkPawn::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
	Super::GetLifetimeReplicatedProps(OutLifetimeProps);
	DOREPLIFETIME(AThunderhawkPawn,bMaskVisible);DOREPLIFETIME(AThunderhawkPawn,bDriverStanding);
}

void AThunderhawkPawn::PossessedBy(AController* NewController)
{
	Super::PossessedBy(NewController);FlightInput=FVector::ZeroVector;
	if(NewController && !NewController->IsPlayerController()) { bDriverStanding=false;ApplyPilotState(); }
}
void AThunderhawkPawn::UnPossessed() { FlightInput=FVector::ZeroVector;Super::UnPossessed(); }

void AThunderhawkPawn::ApplyPilotState()
{
	if (!Definition) { return; }
	if(!IsDriverOnFoot())
	{
	Matt->SetRelativeLocation(bDriverStanding ? FVector(0,-155,0) : Definition->DriverLocation);
	Matt->PlayAnimation(bDriverStanding ? Definition->StandingPose : Definition->DrivingPose,true);
	}
	Spectrum->SetVisibility(IsMaskVisible());MattHair->SetVisibility(!IsMaskVisible());
	Passenger->SetRelativeLocation(Definition->PassengerLocation);Passenger->PlayAnimation(Definition->PassengerPose,true);
	PassengerMask->SetVisibility(true);PassengerHair->SetVisibility(false);
}

bool AThunderhawkPawn::IsMaskVisible() const { return IsValid(DriverCharacter)?DriverCharacter->IsMasked():bMaskVisible; }
void AThunderhawkPawn::DriverCharacterReady()
{
	if(!DriverCharacter || Matt==DriverCharacter->GetMesh()) { return; }
	// Replace temporary native seat components with the persistent driver's components.
	MattHair->DestroyComponent();Spectrum->DestroyComponent();Matt->DestroyComponent();
	Matt=DriverCharacter->GetMesh();MattHair=DriverCharacter->Hair;Spectrum=DriverCharacter->Mask;ApplyPilotState();
}
bool AThunderhawkPawn::CanDriverExit(FString& Reason) const
{
	if(Modes->GetMode()!=EMaskVehicleMode::Road && Modes->GetMode()!=EMaskVehicleMode::Combat) { Reason=TEXT("Atterrissez et terminez la transformation avant de sortir");return false; }
	return Super::CanDriverExit(Reason);
}
void AThunderhawkPawn::ServerToggleMask_Implementation()
{
	if(DriverCharacter) { DriverCharacter->ToggleMaskFromVehicle();bMaskVisible=DriverCharacter->IsMasked(); }
	else { bMaskVisible=!bMaskVisible; }
	ApplyPilotState();ForceNetUpdate();
}
void AThunderhawkPawn::ServerToggleDriverPose_Implementation()
{
	// Retained keyboard-only inspection pose; gameplay exit uses the persistent driver.
	if(IsDriverOnFoot() || Modes->GetMode()!=EMaskVehicleMode::Road || GetVelocity().Size()>25.f) { return; }
	bDriverStanding=!bDriverStanding;ApplyPilotState();ForceNetUpdate();
}

void AThunderhawkPawn::SetupPlayerInputComponent(UInputComponent* Input)
{
	Super::SetupPlayerInputComponent(Input);
	Input->BindKey(EKeys::T,IE_Pressed,this,&AThunderhawkPawn::ToggleMode);
	Input->BindKey(EKeys::Gamepad_FaceButton_Left,IE_Pressed,this,&AThunderhawkPawn::ToggleMode);
	Input->BindKey(EKeys::M,IE_Pressed,this,&AThunderhawkPawn::ServerToggleMask);
	Input->BindKey(EKeys::P,IE_Pressed,this,&AThunderhawkPawn::ServerToggleDriverPose);
	Input->BindAxis(TEXT("MoveForward"),this,&AThunderhawkPawn::FlightForward);
	Input->BindAxis(TEXT("MoveRight"),this,&AThunderhawkPawn::FlightTurn);
	Input->BindAxis(TEXT("FlightLift"),this,&AThunderhawkPawn::FlightLift);
}

void AThunderhawkPawn::ToggleMode()
{
    if(const auto* Mission=ASilentValleyMission::Find(GetWorld());Mission && Mission->IsTerminal()) { ServerRetryMission();return; }
    if (!IsDriverOnFoot() && !bDriverStanding && !IsPauseMenuOpen()) { Modes->ServerToggleMode(); }
}
float AThunderhawkPawn::VisualDeployment() const { return Modes->GetDeployment(); }
bool AThunderhawkPawn::CanVehicleJump() const { return false; }
int32 AThunderhawkPawn::FleetSelectionGroup() const
{
	if(!Definition) { return 100; }
	if(Definition->VehicleName==TEXT("Thunderhawk")) { return 0; }
	if(Definition->VehicleName==TEXT("Rhino")) { return 10; }
	if(Definition->VehicleName.StartsWith(TEXT("Rhino"))) { return 11; }
	if(Definition->VehicleName==TEXT("Hurricane")) { return 20; }
	if(Definition->VehicleName==TEXT("Raven")) { return 30; }
	if(Definition->VehicleName==TEXT("Condor")) { return 40; }
	return 100;
}
const UChaosVehicleWheel* AThunderhawkPawn::AnimationWheel(FName Name) const
{
	const auto* Move=CastChecked<UChaosWheeledVehicleMovementComponent>(GetVehicleMovement());
	const int32 Index=Definition->Wheels.IsEmpty()?(Name==TEXT("FL")?0:Name==TEXT("FR")?1:Name==TEXT("RL")?2:3):Definition->Wheels.IndexOfByPredicate([Name](const FMaskWheelDefinition& W){return W.Name==Name;});
	return Move->Wheels.IsValidIndex(Index)?Move->Wheels[Index].Get():nullptr;
}
void AThunderhawkPawn::FlightForward(float Value) { FlightInput.X=Value; }
void AThunderhawkPawn::FlightTurn(float Value) { FlightInput.Y=Value; }
void AThunderhawkPawn::FlightLift(float Value) { FlightInput.Z=FMath::Clamp(Value,-1.f,1.f); }
void AThunderhawkPawn::ServerFlightInput_Implementation(FVector Input)
{
	if (Input.ContainsNaN()) { return; } FlightInput=Input.BoundToCube(1.f);
}

void AThunderhawkPawn::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (!Definition) { return; }
	if (IsPauseMenuOpen()) { FlightInput=FVector::ZeroVector; }
	const bool HideOwnHead=IsLocallyControlled() && IsInCarView();
	for (auto* Part:{Matt.Get(),MattHair.Get(),Spectrum.Get()}) { Part->SetOwnerNoSee(HideOwnHead); }
	auto* Movement=CastChecked<UChaosWheeledVehicleMovementComponent>(GetVehicleMovement());
    if (bDriverStanding) { Movement->SetThrottleInput(0.f);Movement->SetBrakeInput(1.f); }
    if (IsLocallyControlled())
    {
        InputSendElapsed+=DeltaSeconds;
        if(InputSendElapsed>=.05f) { ServerFlightInput(FlightInput);InputSendElapsed=0.f; }
    }
    Dynamics->SetPilotInput(FlightInput);Dynamics->Simulate(DeltaSeconds);
	if(Definition->bSupportsFlight)
	{
		bool ControlRotation=false;TArray<USpringArmComponent*> Arms;GetComponents(Arms);
		for(const auto* Arm:Arms) { if(Arm->GetFName()==TEXT("Inside Spring Arm")) { ControlRotation=Arm->bUsePawnControlRotation; } }
		TArray<UCameraComponent*> Cameras;GetComponents(Cameras);
		for(auto* Camera:Cameras)
		{
			if(Camera->GetFName()==TEXT("Internal Camera"))
			{ auto Rotation=Camera->GetRelativeRotation();Rotation.Roll=ControlRotation?GetActorRotation().Roll:0.f;Camera->SetRelativeRotation(Rotation); }
		}
	}
	const float Progress=VisualDeployment();
	for (int32 I=0;I<VisualParts.Num();++I)
	{
		const auto& Part=Definition->Parts[I];FTransform Transform=FTransform::Identity;
		if (Part.Samples.Num()>0)
		{
			const float Frame=Progress*(Part.Samples.Num()-1);const int32 A=FMath::FloorToInt(Frame),B=FMath::Min(A+1,Part.Samples.Num()-1);
			Transform.Blend(Part.Samples[A],Part.Samples[B],Frame-A);
		}
		if (!Part.Wheel.IsNone() && !(Part.RotorSpeedDegrees>0.f && Progress>.01f))
		{
			const int32 Index=Definition->Wheels.IsEmpty()?(Part.Wheel==TEXT("FL") ? 0 : Part.Wheel==TEXT("FR") ? 1 : Part.Wheel==TEXT("RL") ? 2 : 3):Definition->Wheels.IndexOfByPredicate([&Part](const FMaskWheelDefinition& W){return W.Name==Part.Wheel;});
			if (const auto* Wheel=AnimationWheel(Part.Wheel);Index!=INDEX_NONE && Wheel)
			{
				const FVector Pivot=Definition->Wheels.IsEmpty()?FVector(Index<2?140.f:-142.f,Index%2==0?-81.8f:81.8f,32.8f):Definition->Wheels[Index].Center-Definition->VisualOriginOffset;
				const FQuat Rotation=FRotator(Wheel->GetRotationAngle(),Wheel->GetSteerAngle(),0).Quaternion();
				// Animate after the source track: Hurricane's middle pair first moves
				// from its stowed position to the deployed physics-wheel centres.
				Transform=Transform*FTransform(Rotation,Pivot+FVector(0,0,Wheel->GetSuspensionOffset())-Rotation.RotateVector(Pivot));
			}
		}
		if(Part.RotorSpeedDegrees>0.f && Progress>.98f)
		{
			const double Now=GetWorld()->GetGameState()?GetWorld()->GetGameState()->GetServerWorldTimeSeconds():GetWorld()->GetTimeSeconds();
			const FQuat Rotation(Part.RotorAxis.GetSafeNormal(),FMath::DegreesToRadians(FMath::Fmod(static_cast<float>(Now)*Part.RotorSpeedDegrees,360.f)));
			Transform=Transform*FTransform(Rotation,Part.RotorPivot-Rotation.RotateVector(Part.RotorPivot));
		}
		Transform.AddToTranslation(Definition->VisualOriginOffset);VisualParts[I]->SetRelativeTransform(Transform);
	}
}
