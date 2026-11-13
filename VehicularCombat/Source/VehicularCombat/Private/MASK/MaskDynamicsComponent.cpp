#include "MASK/MaskDynamicsComponent.h"
#include "MASK/ThunderhawkPawn.h"
#include "MASK/MaskVehicleDefinition.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/HealthComponent.h"
#include "ChaosWheeledVehicleMovementComponent.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Net/UnrealNetwork.h"

UMaskDynamicsComponent::UMaskDynamicsComponent() { SetIsReplicatedByDefault(true); }
void UMaskDynamicsComponent::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
	Super::GetLifetimeReplicatedProps(OutLifetimeProps);DOREPLIFETIME(UMaskDynamicsComponent,TargetAirspeedMPS);DOREPLIFETIME(UMaskDynamicsComponent,GroundClearanceCM);
}
void UMaskDynamicsComponent::SetPilotInput(FVector Value) { if(!Value.ContainsNaN()) { PilotInput=Value.BoundToCube(1.f); } }
bool UMaskDynamicsComponent::IsAirborneMode() const
{
	const auto* Car=Cast<AThunderhawkPawn>(GetOwner());
	return Car && Car->Definition && Car->Definition->bSupportsFlight && (Car->IsNativeAircraft() || Car->Modes->GetMode()==EMaskVehicleMode::Flight || Car->Modes->GetMode()==EMaskVehicleMode::Landing);
}
float UMaskDynamicsComponent::KineticEnergyKJ() const
{
	const auto* Car=Cast<AThunderhawkPawn>(GetOwner());if(!Car) { return 0.f; }
	return .0005f*Car->GetMesh()->GetMass()*(Car->GetMesh()->GetPhysicsLinearVelocity()*.01f).SizeSquared();
}
void UMaskDynamicsComponent::ApplyAttitude(USkeletalMeshComponent* Body,const FQuat& Target,FVector DesiredAngularVelocity) const
{
	FQuat Error=Target*Body->GetComponentQuat().Inverse();if(Error.W<0) { Error=Error*-1.f; }Error.Normalize();
	FVector Axis;float Angle;Error.ToAxisAndAngle(Axis,Angle);
	const auto* Aircraft=Cast<AThunderhawkPawn>(GetOwner());const bool Native=Aircraft && Aircraft->IsNativeAircraft();
	const FVector Acceleration=(Axis*Angle*(Native?25.f:9.f)-(Body->GetPhysicsAngularVelocityInRadians()-DesiredAngularVelocity)*(Native?10.f:5.f)).GetClampedToMaxSize(Native?6.f:3.f);
	// Actual inertia tensor, not an instantaneous rotation assignment.
	const FVector Local=Body->GetComponentQuat().UnrotateVector(Acceleration)*Body->GetInertiaTensor();
	Body->AddTorqueInRadians(Body->GetComponentQuat().RotateVector(Local));
}
void UMaskDynamicsComponent::Simulate(float DeltaSeconds)
{
	auto* Car=Cast<AThunderhawkPawn>(GetOwner());if(!Car || !Car->Definition) { return; }
	auto* Body=Car->GetMesh();auto* Move=CastChecked<UChaosWheeledVehicleMovementComponent>(Car->GetVehicleMovement());
	const auto& Tune=Car->Definition->Dynamics;const auto Mode=Car->Modes->GetMode();const bool Air=IsAirborneMode();
	const bool Native=Car->IsNativeAircraft(),WasAir=bAirForces;
	if(Air!=bAirForces)
	{
		Move->EnableMechanicalSim(!Air && !Native);Move->EnableSuspension(!Air && !Native);Move->EnableWheelFriction(!Air && !Native);Move->EnableSelfRighting(!Air && !Native);
		bAirForces=Air;Body->WakeAllRigidBodies();
	}
	if(!Car->HasAuthority() && !Car->IsLocallyControlled()) { PreviousMode=Mode;return; }
	const FVector Velocity=Body->GetPhysicsLinearVelocity()*.01f;const float Mass=Body->GetMass();
	const bool Rotor=Native?Mode!=EMaskVehicleMode::Flight:Tune.FlightModel==EMaskFlightModel::Rotorcraft;
	const float Maximum=Rotor?Tune.RotorcraftMaximumAirspeedMPS:Tune.MaximumAirspeedMPS;
	if(Air && (!WasAir || (Native && Rotor!=bPreviousRotorModel)))
	{
		if(Car->HasAuthority()) { TargetAirspeedMPS=FMath::Clamp(static_cast<float>(Velocity.Size2D()),Rotor?0.f:Tune.MinimumAirspeedMPS,Maximum); }
		bTakeoffAssist=!Native;
	}
	bPreviousRotorModel=Rotor;
	PreviousMode=Mode;
	if(!Air)
	{
		// P = torque * angular speed. Finite engine power makes acceleration fall
		// with speed; tires/transmission/brake torques remain in Chaos.
		if(NominalEngineTorque<=0.f) { NominalEngineTorque=Move->EngineSetup.MaxTorque; }
		const float PowerKW=Tune.RoadPowerKW>0?Tune.RoadPowerKW:FMath::Clamp(Mass*.12f,90.f,420.f);
		const float RPM=FMath::Max(Move->GetEngineRotationSpeed(),900.f);
		// Chaos multiplies MaxTorque by its normalized curve afterwards. Apply
		// the shaft-power limit once, rather than reducing it a second time there.
		const float CurveFraction=Move->EngineSetup.MaxTorque>0.f?Move->EngineSetup.GetTorqueFromRPM(RPM)/Move->EngineSetup.MaxTorque:1.f;
		const float Torque=FMath::Min(NominalEngineTorque,PowerKW*1000.f*(Car->HasPhysicalPowerBoost()?1.5f:1.f)/(RPM*2.f*PI/60.f*FMath::Max(.05f,CurveFraction)));
		if(FMath::Abs(Torque-LastEngineTorque)>5.f) { Move->SetMaxEngineTorque(Torque);LastEngineTorque=Torque; }
		if(Car->HasAuthority() && Move->bMechanicalSimEnabled)
		{
			bool Contact=false;for(int32 I=0;I<Move->Wheels.Num();++I) { Contact|=Move->GetWheelState(I).bInContact; }
			if(Contact && Tune.bTwoWheelRoadBalance)
			{
				const FQuat Orientation=Body->GetComponentQuat();
				FRotator Balanced=Body->GetComponentRotation();
				Balanced.Roll=Move->GetSteeringInput()*8.f*FMath::Clamp(static_cast<float>(Velocity.Size2D())/8.f,0.f,1.f);
				// A narrow two-contact motorcycle needs a critically damped roll
				// controller, independent of the slower aircraft attitude response.
				// Unreal's positive FRotator roll is a NEGATIVE local-X
				// quaternion rotation. Match the physical torque convention.
				const float RollError=-FMath::DegreesToRadians(FMath::FindDeltaAngleDegrees(Body->GetComponentRotation().Roll,Balanced.Roll));
				const float RollRate=Orientation.UnrotateVector(Body->GetPhysicsAngularVelocityInRadians()).X;
				const float RollAcceleration=FMath::Clamp(RollError*36.f-RollRate*12.f,-20.f,20.f);
				Body->AddTorqueInRadians(Orientation.RotateVector(FVector(RollAcceleration*Body->GetInertiaTensor().X,0,0)));
			}
			if(Contact && Velocity.Size2D()>.1f)
			{
				const float Area=Tune.RoadDragAreaM2>0?Tune.RoadDragAreaM2:(Mass>4000.f?4.5f:.8f);
				const float Resistance=.5f*1.225f*Area*Velocity.SizeSquared()+Mass*9.81f*Tune.RollingResistance;
				Body->AddForce(-Velocity.GetSafeNormal()*Resistance*100.f);
			}
		}
		return;
	}
	if(!Car->HasAuthority()) { return; }
	if(const auto* Health=Car->FindComponentByClass<UHealthComponent>();Health && Health->CurrentHealth<=0.f) { return; }
	FCollisionQueryParams Query(SCENE_QUERY_STAT(MaskLandingGround),false,Car);TArray<AActor*> Attached;Car->GetAttachedActors(Attached,true,true);Query.AddIgnoredActors(Attached);
	// Terrain below other vehicles is the landing reference, not their roofs.
	for(TActorIterator<APawn> It(GetWorld());It;++It) { Query.AddIgnoredActor(*It); }
	FHitResult Ground;const bool FoundGround=GetWorld()->LineTraceSingleByChannel(Ground,Car->GetActorLocation()+FVector(0,0,50),Car->GetActorLocation()-FVector(0,0,50000),ECC_Vehicle,Query);
	GroundClearanceCM=FoundGround?Car->GetActorLocation().Z-Ground.ImpactPoint.Z:50000.f;
	const float Height=GroundClearanceCM*.01f;
	const bool Landing=Mode==EMaskVehicleMode::Landing;
	// Landed skids can sleep without a wheel tick; pilot lift must wake the actual rigid body.
	if(Native && (Mode!=EMaskVehicleMode::Road || PilotInput.SizeSquared()>.0025f || Height>.4f)) { Move->SetSleeping(false); }
	if(Native && Mode==EMaskVehicleMode::Road && FoundGround && Height<.4f && PilotInput.Z<=.05f && PilotInput.X<=.05f && Velocity.Z<.8f)
	{
		// Real skid collision supports the landed helicopter; no automatic hover on spawn.
		TargetAirspeedMPS=0.f;bTakeoffAssist=false;
		Body->AddForce(-FVector(Velocity.X,Velocity.Y,0)*Mass*4.f*100.f);
		const FVector Heading=Car->GetActorForwardVector().GetSafeNormal2D();
		ApplyAttitude(Body,FRotationMatrix::MakeFromZX(Ground.ImpactNormal,Heading).ToQuat(),FVector::ZeroVector);
		return;
	}
	if(Native && FoundGround && Height<.4f && (PilotInput.Z>.05f || PilotInput.X>.05f || Mode==EMaskVehicleMode::Deploying)) { bTakeoffAssist=true; }
	if(Height>=Tune.AutomaticTakeoffHeightM && Velocity.Z>=0.f) { bTakeoffAssist=false; }
	if(Landing) { bTakeoffAssist=false; }
	const float Minimum=Rotor?0.f:FMath::Max(5.f,Tune.MinimumAirspeedMPS);
	TargetAirspeedMPS=FMath::Clamp(TargetAirspeedMPS+(Landing?0.f:PilotInput.X)*Tune.SpeedCommandRateMPS2*DeltaSeconds,Minimum,FMath::Max(Minimum,Maximum));
	if(Native && Mode==EMaskVehicleMode::Deploying) { TargetAirspeedMPS=FMath::Max(TargetAirspeedMPS,Tune.MinimumAirspeedMPS*Car->Modes->GetDeployment()); }
	if(Native && Mode==EMaskVehicleMode::Retracting) { TargetAirspeedMPS=FMath::Max(0.f,TargetAirspeedMPS-FMath::Max(12.f,Tune.SpeedCommandRateMPS2)*DeltaSeconds); }
	if(Landing) { TargetAirspeedMPS=FMath::Max(Minimum,TargetAirspeedMPS-FMath::Max(10.f,Tune.SpeedCommandRateMPS2)*DeltaSeconds); }
	float DesiredVZ=Rotor?PilotInput.Z*Tune.RotorcraftClimbMPS:Velocity.Size2D()*FMath::Sin(FMath::DegreesToRadians(PilotInput.Z*Tune.MaximumPitchDegrees));
	if(bTakeoffAssist && FoundGround) { DesiredVZ=FMath::Max(DesiredVZ,FMath::Clamp((Tune.AutomaticTakeoffHeightM-Height)*2.f,.3f,2.5f)); }
	if(Landing)
	{
		// Descend decisively at height; a braking-distance profile reserves the
		// final metres for a continuous flare rather than a long slow crawl.
		const float BrakingAcceleration=Rotor?3.f:4.f;
		const float FlareSpeed=FMath::Sqrt(2.f*BrakingAcceleration*FMath::Max(0.f,Height-.06f));
		DesiredVZ=FoundGround?-FMath::Clamp(FlareSpeed,.4f,FMath::Max(.4f,Tune.LandingDescentMPS)):-FMath::Max(.4f,Tune.LandingDescentMPS);
	}
	// Powered lift/flight assistance is intentional for M.A.S.K. conversions.
	// All changes act through bounded forces: no SetVelocity/SetRotation in flight.
	const float Gravity=-GetWorld()->GetGravityZ()*.01f;
	const float VerticalAcceleration=FMath::Clamp((DesiredVZ-Velocity.Z)*1.6f,-Gravity*.8f,Gravity);
	const FVector Drag=-Velocity.GetSafeNormal()*(.5f*1.225f*Tune.AirDragAreaM2*Velocity.SizeSquared());
	FVector Force=Drag;
	FRotator Attitude=Car->GetActorRotation();float DesiredYawRate=0.f;FVector RotorThrustAxis=Car->GetActorUpVector();
	if(!Rotor)
	{
		const float ForwardSpeed=FVector::DotProduct(Velocity,Car->GetActorForwardVector());
		// Include the body's viscous damping so the steady speed reaches the
		// requested endpoints rather than settling a few km/h below the target.
		const float DragCompensation=.5f*1.225f*Tune.AirDragAreaM2*FMath::Square(ForwardSpeed)+Mass*Body->GetLinearDamping()*ForwardSpeed;
		const float AvailableThrust=FMath::Min(Tune.MaximumThrustN,Tune.FlightPowerKW*1000.f/FMath::Max(ForwardSpeed,8.f));
		const float Thrust=FMath::Clamp((TargetAirspeedMPS-ForwardSpeed)*Mass*.7f+DragCompensation,-Mass*(Landing?5.f:3.f),AvailableThrust);
		Force+=Car->GetActorForwardVector()*Thrust;
		// Assisted M.A.S.K. flight keeps a usable U-turn even at maximum speed.
		// The matching lateral force below turns the trajectory as well as the nose.
		const float SpeedAlpha=FMath::Clamp((static_cast<float>(Velocity.Size2D())-Minimum)/FMath::Max(1.f,Maximum-Minimum),0.f,1.f);
		DesiredYawRate=PilotInput.Y*FMath::DegreesToRadians(FMath::Lerp(Tune.LowSpeedTurnRateDegrees,Tune.HighSpeedTurnRateDegrees,SpeedAlpha));
		if(Landing && Height<3.f) { DesiredYawRate*=.15f; }
		float Pitch=PilotInput.Z*Tune.MaximumPitchDegrees;
		if(bTakeoffAssist || Landing) { Pitch=FMath::RadiansToDegrees(FMath::Atan2(DesiredVZ,FMath::Max(static_cast<float>(Velocity.Size2D()),Minimum))); }
		if(Landing && Height<3.f) { Pitch*=FMath::Clamp((Height-.3f)/2.7f,0.f,1.f); }
		const float BankLimit=Landing && Height<3.f?5.f:Tune.MaximumBankDegrees;
		// Unreal positive roll lowers the right wing (RightVector.Z < 0).
		Attitude.Pitch=Pitch;Attitude.Roll=PilotInput.Y*BankLimit;
		const FVector Side=Car->GetActorRightVector();Force-=Side*FVector::DotProduct(Velocity,Side)*Mass*.6f;
	}
	else
	{
		const FVector Heading=Car->GetActorForwardVector().GetSafeNormal2D();
		const FVector DesiredHorizontal=Heading*TargetAirspeedMPS;
		const bool Braking=Landing || (Native && (Mode==EMaskVehicleMode::Retracting || PilotInput.X<-.05f));
		const float TiltLimit=FMath::Max(.1f,Gravity+VerticalAcceleration)*FMath::Tan(FMath::DegreesToRadians(FMath::Clamp(Braking?30.f:Tune.MaximumPitchDegrees,1.f,35.f)));
		const FVector DampingCompensation=FVector(Velocity.X,Velocity.Y,0)*Body->GetLinearDamping();
		const FVector Acceleration=((DesiredHorizontal-FVector(Velocity.X,Velocity.Y,0))*(Native?1.f:2.f)+DampingCompensation).GetClampedToMaxSize(FMath::Min(Braking?6.f:4.5f,TiltLimit));
		FVector DesiredUp=FVector(Acceleration.X,Acceleration.Y,Gravity+VerticalAcceleration).GetSafeNormal();
		if(Landing && FoundGround && Height<2.5f && Ground.ImpactNormal.Z>.82f)
		{
			DesiredUp=FMath::Lerp(DesiredUp,Ground.ImpactNormal,FMath::Clamp((2.5f-Height)/2.f,0.f,1.f)).GetSafeNormal();
		}
		// Native cyclic thrust responds before the airframe catches up, avoiding a delayed hover feedback loop.
		if(Native) { RotorThrustAxis=DesiredUp; }
		// Preserve the rotor thrust axis first; prioritizing heading would flatten
		// the commanded forward tilt and prevent horizontal acceleration.
		Attitude=FRotationMatrix::MakeFromZX(DesiredUp,Heading).Rotator();DesiredYawRate=PilotInput.Y*FMath::DegreesToRadians(Tune.LowSpeedTurnRateDegrees);
	}
	const FVector ThrustAxis=Native && Rotor?RotorThrustAxis:Car->GetActorUpVector();
	const float Lift=Mass*FMath::Clamp((Gravity+VerticalAcceleration)/FMath::Max(ThrustAxis.Z,.4),0.,Gravity*2.5);
	Force+=ThrustAxis*Lift;
	if(!Rotor)
	{
		// Replace horizontal bank lift with the commanded centripetal force.
		// Vertical lift and all thrust/attitude limits remain physical forces.
		const FVector LiftForce=Car->GetActorUpVector()*Lift;
		Force-=FVector(LiftForce.X,LiftForce.Y,0);
		Force+=FVector::CrossProduct(FVector::UpVector,Velocity.GetSafeNormal2D())*Mass*Velocity.Size2D()*DesiredYawRate;
	}
	if(Native && PilotInput.Z>.5f && Height<.4f) { UE_LOG(LogTemp,Display,TEXT("SWITCHBLADE_LIFT input=%s mass=%.1f desired_vz=%.2f force=%s velocity=%s awake=%d"),*PilotInput.ToString(),Mass,DesiredVZ,*Force.ToString(),*Velocity.ToString(),Body->IsAnyRigidBodyAwake()); }
	Body->AddForce(Force*100.f);
	ApplyAttitude(Body,Attitude.Quaternion(),FVector::UpVector*DesiredYawRate);
	// A motorcycle remains balanced upright across a hillside rather than
	// laying its frame parallel to the slope. Requiring the latter can leave
	// a stopped, grounded Condor in Landing forever.
	const bool TouchdownAligned=Rotor?
		(Car->GetActorUpVector().Z>.94f && Ground.ImpactNormal.Z>.65f):
		FVector::DotProduct(Car->GetActorUpVector(),Ground.ImpactNormal)>.96f;
	if(Landing && FoundGround && Height<.12f && FMath::Abs(Velocity.Z)<2.f && TouchdownAligned)
	{ Car->Modes->NotifyTouchdown(); }
}
