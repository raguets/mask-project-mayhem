#if !UE_BUILD_SHIPPING
#include "Tests/DynamicsSmoke.h"
#include "MASK/MaskDriverCharacter.h"
#include "MASK/MaskDriverAnimInstance.h"
#include "MASK/MaskVehicleDefinition.h"
#include "MASK/MaskVehicleModeComponent.h"
#include "MASK/ThunderhawkPawn.h"
#include "MASK/RhinoPawn.h"
#include "MASK/HurricanePawn.h"
#include "SilentValley/SilentValleyRoad.h"
#include "Actors/WeaponPickupActor.h"
#include "AI/VehicleBotController.h"
#include "Components/HealthComponent.h"
#include "Components/BoxComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Camera/CameraActor.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "ChaosWheeledVehicleMovementComponent.h"
#include "Containers/Ticker.h"
#include "Dom/JsonObject.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "HAL/FileManager.h"
#include "HAL/IConsoleManager.h"
#include "InputKeyEventArgs.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonSerializer.h"
#include "UnrealClient.h"

namespace OnFootSmoke
{
constexpr float FloorZ=20000.f;
class FRun
{
    FString Directory,Role;bool Host=false,Network=false,Initialized=false,Terrain=false;
    bool LateLegMotion=false;FVector LateFootBone;
    int32 Phase=0,RosterIndex=0,AmmoBefore=0;double Started=FPlatformTime::Seconds(),StageTime=Started,SimTime=0,StageSimTime=0;
    FVector Start,FootBone,ExitPoint;float InitialHealth=0,InitialYaw=0,PeakJump=0,WalkSpeed=0,RunSpeed=0;
    TMap<FKey,float> Axes;TArray<TWeakObjectPtr<AActor>> Obstacles;
    TWeakObjectPtr<APlayerWheeledVehiclePawn> Original,Current,Enemy;
    TWeakObjectPtr<AMaskDriverCharacter> Driver;TWeakObjectPtr<USkeletalMeshComponent> Body;
    TSharedRef<FJsonObject> Checks=MakeShared<FJsonObject>(),Telemetry=MakeShared<FJsonObject>();
    void Check(const TCHAR* Name,bool Value) { Checks->SetBoolField(Name,Value); }
    void Stage(int32 Value) { Phase=Value;StageTime=FPlatformTime::Seconds();StageSimTime=SimTime;UE_LOG(LogTemp,Display,TEXT("MASK_ONFOOT_TEST %s phase=%d"),*Role,Phase); }
    FString Path(const TCHAR* Name) const { return Directory/Name; }
    bool Has(const TCHAR* Name) const { return IFileManager::Get().FileExists(*Path(Name)); }
    void Signal(const TCHAR* Name) const { FFileHelper::SaveStringToFile(TEXT("ready"),*Path(Name)); }
    void Key(APlayerController* PC,FKey Value,bool Down) { PC->InputKey(FInputKeyEventArgs::CreateSimulated(Value,Down?IE_Pressed:IE_Released,Down?1.f:0.f,-1,FInputDeviceId::CreateFromInternalId(0))); }
    void Button(APlayerController* PC,FKey Value) { Key(PC,Value,true);Key(PC,Value,false); }
    void Shot(const TCHAR* Name) { if(!FParse::Param(FCommandLine::Get(),TEXT("NullRHI"))) { FScreenshotRequest::RequestScreenshot(Path(Name),true,false); } }
    void Portrait(APlayerController* PC,AMaskDriverCharacter* D)
    {
        if(FParse::Param(FCommandLine::Get(),TEXT("NullRHI"))) { return; }
        FVector Location;FCollisionQueryParams Query(SCENE_QUERY_STAT(DriverReviewCamera),false,D);
        TArray<AActor*> Attached;D->GetAttachedActors(Attached,true,true);Query.AddIgnoredActors(Attached);
        for(const float Angle:{30.f,-30.f,60.f,-60.f,120.f,-120.f,180.f})
        {
            Location=D->GetActorLocation()+D->GetActorForwardVector().RotateAngleAxis(Angle,FVector::UpVector)*330+FVector(0,0,10);
            FHitResult Hit;if(!D->GetWorld()->LineTraceSingleByChannel(Hit,D->GetActorLocation(),Location,ECC_Visibility,Query)) { break; }
        }
        auto* Camera=D->GetWorld()->SpawnActor<ACameraActor>(Location,(D->GetActorLocation()-Location).Rotation());Camera->SetLifeSpan(3);PC->SetViewTarget(Camera);
    }
    void Place(APlayerWheeledVehiclePawn* Car,FVector Location)
    {
        Car->SetActorLocationAndRotation(Location,FRotator::ZeroRotator,false,nullptr,ETeleportType::TeleportPhysics);
        Car->GetMesh()->SetPhysicsLinearVelocity(FVector::ZeroVector);Car->GetMesh()->SetPhysicsAngularVelocityInRadians(FVector::ZeroVector);
    }
    void Snapshot(AMaskDriverCharacter* D,const TCHAR* Name)
    {
        auto R=MakeShared<FJsonObject>();R->SetStringField(TEXT("location"),D->GetActorLocation().ToString());R->SetStringField(TEXT("velocity"),D->GetVelocity().ToString());
        R->SetNumberField(TEXT("health"),D->Health);R->SetBoolField(TEXT("on_foot"),D->IsOnFoot());R->SetBoolField(TEXT("masked"),D->IsMasked());
        R->SetStringField(TEXT("animation_class"),GetNameSafe(D->GetMesh()->GetAnimInstance()));R->SetStringField(TEXT("mesh_bounds_cm"),D->GetMesh()->Bounds.BoxExtent.ToString());
        const auto* Movement=D->GetCharacterMovement();
        R->SetNumberField(TEXT("movement_mode"),Movement->MovementMode);R->SetBoolField(TEXT("floor_walkable"),Movement->CurrentFloor.IsWalkableFloor());
        R->SetStringField(TEXT("floor_actor"),GetNameSafe(Movement->CurrentFloor.HitResult.GetActor()));R->SetStringField(TEXT("floor_normal"),Movement->CurrentFloor.HitResult.ImpactNormal.ToString());
        R->SetStringField(TEXT("status"),D->Status);
        FFindFloorResult NearbyFloor;Movement->FindFloor(D->GetActorLocation(),NearbyFloor,false);
        R->SetBoolField(TEXT("nearby_floor_walkable"),NearbyFloor.IsWalkableFloor());R->SetNumberField(TEXT("nearby_floor_distance_cm"),NearbyFloor.GetDistanceToFloor());
        R->SetStringField(TEXT("right_hand"),D->GetMesh()->GetBoneLocation(TEXT("hand_R")).ToString());
        if(D->HandWeapon) { R->SetStringField(TEXT("weapon"),D->HandWeapon->GetActorLocation().ToString());R->SetNumberField(TEXT("ammo"),D->HandWeapon->CurrentMagazineAmmo); }
        Telemetry->SetObjectField(Name,R);
    }
    void Save(bool Complete)
    {
        bool Passed=Complete;for(const auto& Pair:Checks->Values) { Passed&=Pair.Value->AsBool(); }
        auto R=MakeShared<FJsonObject>();R->SetStringField(TEXT("role"),Role);R->SetBoolField(TEXT("passed"),Passed);R->SetBoolField(TEXT("complete"),Complete);
        R->SetNumberField(TEXT("phase"),Phase);R->SetNumberField(TEXT("elapsed_seconds"),FPlatformTime::Seconds()-Started);R->SetObjectField(TEXT("checks"),Checks);R->SetObjectField(TEXT("telemetry"),Telemetry);
        R->SetStringField(TEXT("fixture"),Terrain?TEXT("Silent Valley actual Pinewood terrain; explicit vehicle placement at route metre 800, no platform; 12-second walk, sprint, jump and return to the exit point. Injected Xbox inputs; not a driven route or manual validation."):TEXT("Opt-in flat platform at 200m, existing playable pawns, injected Xbox inputs. Solo roster possession/obstacles and enemy placement are explicit fixtures. No physical gamepad/manual play claimed."));
        FString Json;FJsonSerializer::Serialize(R,TJsonWriterFactory<>::Create(&Json));FFileHelper::SaveStringToFile(Json,*(Directory/(Role+TEXT(".json"))));
    }
    bool Finish(bool Timeout=false) { Check(TEXT("no_timeout"),!Timeout);Save(true);Signal(Host?TEXT("host.done"):TEXT("client.done"));FPlatformMisc::RequestExit(false);return false; }
public:
    explicit FRun(FString InRole):Role(InRole),Host(InRole==TEXT("host")),Network(InRole!=TEXT("solo"))
    { Terrain=FParse::Param(FCommandLine::Get(),TEXT("OnFootTerrain"));FParse::Value(FCommandLine::Get(),TEXT("MigrationReportDir="),Directory);if(Directory.IsEmpty()) { Directory=FPaths::ProjectSavedDir()/TEXT("Migration/onfoot-smoke"); }IFileManager::Get().MakeDirectory(*Directory,true); }
    bool Tick(float)
    {
        if(FPlatformTime::Seconds()-Started>180.) { return Finish(true); }
        UWorld* World=nullptr;for(const auto& C:GEngine->GetWorldContexts()) { if(C.WorldType==EWorldType::Game) { World=C.World();break; } }
        if(!World) { return true; }SimTime=World->GetTimeSeconds();auto* PC=World->GetFirstPlayerController();if(!PC) { return true; }
        if(!Initialized)
        {
            auto* Car=Cast<APlayerWheeledVehiclePawn>(PC->GetPawn());if(!Car || !Car->DriverCharacter || World->GetTimeSeconds()<3.f) { return true; }
            Initialized=true;Original=Car;Current=Car;Driver=Car->DriverCharacter;Body=Driver->GetMesh();
            if(Terrain)
            {
                Check(TEXT("actual_silent_valley_map"),World->GetMapName().Contains(TEXT("SilentValley")));
                for(TActorIterator<ASilentValleyRoad> It(World);It;++It)
                {
                    Place(Car,It->RouteLocation(80000)+FVector(0,0,20));Car->SetActorLocationAndRotation(Car->GetActorLocation(),It->RouteRotation(80000),false,nullptr,ETeleportType::TeleportPhysics);break;
                }
                Stage(4);
            }
            else if(!Network || Host)
            {
                World->SpawnActor<ADynamicsTestFloor>(FVector(0,0,FloorZ-50),FRotator::ZeroRotator);Car->FleetTeamId=Host?2:1;
                Place(Car,FVector(Host?4000:0,Host?-180:0,FloorZ+15));
                if(Host) { Signal(TEXT("host.ready")); }
                else
                {
                    auto* Target=World->SpawnActor<AThunderhawkPawn>(Car->GetClass(),FVector(4000,-180,FloorZ+15),FRotator::ZeroRotator);Enemy=Target;Target->FleetTeamId=2;
                    auto* Bot=World->SpawnActor<AVehicleBotController>();Bot->Possess(Target);Bot->SetActorTickEnabled(false);Stage(1);
                }
            }
        }
        if(Host)
        {
            APlayerController* RemotePC=nullptr;for(FConstPlayerControllerIterator It=World->GetPlayerControllerIterator();It;++It) { if(It->Get()!=PC) { RemotePC=It->Get();break; } }
            if(Phase==0 && RemotePC && RemotePC->GetPawn())
            {
                auto* Remote=Cast<APlayerWheeledVehiclePawn>(RemotePC->GetPawn());if(!Remote || !Remote->DriverCharacter) { return true; }
                Place(Remote,FVector(0,0,FloorZ+15));Remote->FleetTeamId=1;Current=Remote;Driver=Remote->DriverCharacter;Body=Driver->GetMesh();
                Signal(TEXT("drive.ready"));Stage(1);InitialHealth=Original->FindComponentByClass<UHealthComponent>()->CurrentHealth;
            }
            if(Driver.IsValid())
            {
                auto* D=Driver.Get();if(D->IsOnFoot())
                {
                    Check(TEXT("remote_exit_authority"),RemotePC && RemotePC->GetPawn()==D && !Current->GetController());
                    if(D->GetVelocity().Size2D()>120.f) { Check(TEXT("remote_walking_authority"),true); }
                    if(D->GetVelocity().Size2D()>350.f) { Check(TEXT("remote_running_authority"),true); }
                    if(D->GetCharacterMovement()->IsFalling() && D->GetActorLocation().Z>FloorZ+150.f) { Check(TEXT("remote_jump_authority"),true); }
                    if(!D->IsMasked()) { Check(TEXT("remote_mask_hidden_authority"),true); }
                    if(D->HandWeapon && D->HandWeapon->CurrentMagazineAmmo<D->HandWeapon->MagazineSize) { Check(TEXT("remote_fire_authority"),true); }
                    Check(TEXT("same_remote_body_authority"),D->GetMesh()==Body.Get());
                }
                if(Has(TEXT("returned"))) { Check(TEXT("remote_return_authority"),RemotePC && RemotePC->GetPawn()==Current.Get() && !D->IsOnFoot() && D->GetAttachParentActor()==Current.Get()); }
            }
            if(Original.IsValid() && Original->FindComponentByClass<UHealthComponent>()->CurrentHealth<InitialHealth) { Check(TEXT("remote_projectile_damage_authority"),true); }
            if(Has(TEXT("client.done")))
            {
                for(const TCHAR* Name:{TEXT("remote_exit_authority"),TEXT("remote_walking_authority"),TEXT("remote_running_authority"),TEXT("remote_jump_authority"),TEXT("remote_mask_hidden_authority"),TEXT("remote_fire_authority"),TEXT("same_remote_body_authority"),TEXT("remote_return_authority"),TEXT("remote_projectile_damage_authority")}) { if(!Checks->HasField(Name)) { Check(Name,false); } }
                return Finish();
            }
            Save(false);return true;
        }
        auto* Car=Current.Get();auto* D=Driver.Get();if(!Car || !D) { Check(TEXT("driver_survives"),false);return Finish(); }
        if(Phase==0)
        {
            if(!Has(TEXT("drive.ready"))) { Save(false);return true; }Place(Car,FVector(0,0,FloorZ+15));
            for(TActorIterator<APlayerWheeledVehiclePawn> It(World);It;++It) { if(*It!=Car && It->GetController() && It->FleetTeamId==2) { Enemy=*It;break; } }Stage(1);
        }
        const double Age=Phase==21?FPlatformTime::Seconds()-StageTime:SimTime-StageSimTime;
        if(Phase==1 && Age>1.) { Check(TEXT("persistent_seated_driver"),D->GetAttachParentActor()==Car && !D->IsOnFoot());Axes.Add(EKeys::Gamepad_RightTriggerAxis,1);Stage(2); }
        else if(Phase==2 && Age>2.) { Check(TEXT("moving_before_exit_attempt"),Car->GetVelocity().Size2D()>300);Button(PC,EKeys::Gamepad_FaceButton_Bottom);Stage(3); }
        else if(Phase==3 && Age>.5)
        { Check(TEXT("exit_rejected_while_moving"),PC->GetPawn()==Car && !D->IsOnFoot());Axes.Add(EKeys::Gamepad_RightTriggerAxis,0);Axes.Add(EKeys::Gamepad_LeftTriggerAxis,1);Key(PC,EKeys::Gamepad_LeftShoulder,true);Stage(4); }
        else if(Phase==4 && Age>4. && Car->GetVelocity().Size()<15)
        {
            Axes.Add(EKeys::Gamepad_LeftTriggerAxis,0);
            if(!Network && !Terrain)
            {
                for(const FVector Local:Car->GetDriverExitOffsets())
                {
                    auto* Obstacle=World->SpawnActor<AActor>();auto* Box=NewObject<UBoxComponent>(Obstacle);Obstacle->SetRootComponent(Box);Box->SetBoxExtent(FVector(65,65,150));Box->SetCollisionProfileName(TEXT("BlockAll"));Box->RegisterComponent();
                    auto P=Car->GetActorTransform().TransformPosition(Local);P.Z=FloorZ+150;Obstacle->SetActorLocation(P);Obstacles.Add(Obstacle);
                }
                Button(PC,EKeys::Gamepad_FaceButton_Bottom);Stage(5);
            }
            else { Button(PC,EKeys::Gamepad_FaceButton_Bottom);Stage(6); }
        }
        else if(Phase==5 && Age>.5)
        { Check(TEXT("exit_rejected_when_both_sides_blocked"),PC->GetPawn()==Car && !D->IsOnFoot());for(auto Obstacle:Obstacles) { if(Obstacle.IsValid()) { Obstacle->Destroy(); } }Obstacles.Empty();Button(PC,EKeys::Gamepad_FaceButton_Bottom);Stage(6); }
        else if(Phase==6 && Age>1.)
        {
            Check(TEXT("a_exits_and_possesses_same_driver"),PC->GetPawn()==D && D->IsOnFoot() && D->GetMesh()==Body.Get() && D->Mask->IsVisible());
            if(!D->IsOnFoot()) { return Finish(); }
            Check(TEXT("parked_vehicle_reserved_without_ai"),!Car->GetController() && !Car->IsAvailableToSwitch());
            Check(TEXT("locomotion_loaded"),D->Definition->DriverLocomotion && D->Definition->DriverJump && Cast<UMaskDriverAnimInstance>(D->GetMesh()->GetAnimInstance()));
            Check(TEXT("body_human_scale"),D->GetMesh()->Bounds.BoxExtent.Z>65 && D->GetMesh()->Bounds.BoxExtent.Z<110);
            Snapshot(D,TEXT("idle"));Shot(TEXT("foot-idle.png"));Start=ExitPoint=D->GetActorLocation();FootBone=D->GetMesh()->GetBoneLocation(TEXT("foot_L"),EBoneSpaces::ComponentSpace);Axes.Add(EKeys::Gamepad_LeftY,1);Stage(7);
        }
        else if(Phase==7)
        {
            WalkSpeed=FMath::Max(WalkSpeed,static_cast<float>(D->GetVelocity().Size2D()));
            if(FVector::Dist(FootBone,D->GetMesh()->GetBoneLocation(TEXT("foot_L"),EBoneSpaces::ComponentSpace))>5) { Check(TEXT("walking_animates_legs"),true); }
            if(Age>8. && Age<8.2) { LateFootBone=D->GetMesh()->GetBoneLocation(TEXT("foot_L"),EBoneSpaces::ComponentSpace); }
            if(Age>9. && FVector::Dist(LateFootBone,D->GetMesh()->GetBoneLocation(TEXT("foot_L"),EBoneSpaces::ComponentSpace))>5) { LateLegMotion=true; }
            if(Age>12.)
            {
                Check(TEXT("left_stick_walks"),FVector::Dist2D(Start,D->GetActorLocation())>1500 && WalkSpeed>230 && WalkSpeed<250);
                Check(TEXT("walking_still_animates_after_12_seconds"),LateLegMotion && Cast<UMaskDriverAnimInstance>(D->GetMesh()->GetAnimInstance()));
                Check(TEXT("walking_still_grounded_after_12_seconds"),D->GetCharacterMovement()->IsMovingOnGround());
                Telemetry->SetNumberField(TEXT("walking_cm_s"),WalkSpeed);Snapshot(D,TEXT("walking"));Shot(TEXT("foot-walk.png"));Key(PC,EKeys::Gamepad_LeftThumbstick,true);Start=D->GetActorLocation();Stage(8);
            }
        }
        else if(Phase==8)
        {
            RunSpeed=FMath::Max(RunSpeed,static_cast<float>(D->GetVelocity().Size2D()));
            if(Age>1.5) { Check(TEXT("l3_runs"),D->IsSprinting() && FVector::Dist2D(Start,D->GetActorLocation())>430 && RunSpeed>380 && RunSpeed<420);Telemetry->SetNumberField(TEXT("running_cm_s"),RunSpeed);Snapshot(D,TEXT("running"));Shot(TEXT("foot-run.png"));Axes.Add(EKeys::Gamepad_LeftY,0);Key(PC,EKeys::Gamepad_LeftThumbstick,false);Start=D->GetActorLocation();Key(PC,EKeys::Gamepad_FaceButton_Bottom,true);Stage(9); }
        }
        else if(Phase==9)
        {
            PeakJump=FMath::Max(PeakJump,static_cast<float>(D->GetActorLocation().Z-Start.Z));if(Age>.18) { Key(PC,EKeys::Gamepad_FaceButton_Bottom,false); }
            if(D->GetActorLocation().Z>Start.Z+40) { Check(TEXT("jump_stays_airborne_above_ground"),D->GetCharacterMovement()->IsFalling()); }
            if(Age>1.5) { Check(TEXT("a_jumps_and_lands"),PeakJump>60 && D->GetCharacterMovement()->IsMovingOnGround());Telemetry->SetNumberField(TEXT("jump_height_cm"),PeakJump);InitialYaw=PC->GetControlRotation().Yaw;Axes.Add(EKeys::Gamepad_RightX,.6f);Button(PC,EKeys::Gamepad_FaceButton_Top);Stage(10); }
        }
        else if(Phase==10 && Age>1.)
        {
            Check(TEXT("right_stick_rotates_camera_and_aim"),FMath::Abs(FMath::FindDeltaAngleDegrees(InitialYaw,PC->GetControlRotation().Yaw))>30);
            Check(TEXT("y_removes_same_mask_keeps_face"),!D->IsMasked() && !D->Mask->IsVisible() && D->GetMesh()==Body.Get());Snapshot(D,TEXT("unmasked"));Portrait(PC,D);Shot(TEXT("foot-face.png"));Axes.Add(EKeys::Gamepad_RightX,0);
            if(Terrain) { Axes.Add(EKeys::Gamepad_LeftY,1);Key(PC,EKeys::Gamepad_LeftThumbstick,true);Stage(15); }
            else { Button(PC,EKeys::Gamepad_FaceButton_Left);Stage(11); }
        }
        else if(Phase==11 && Age>.5)
        {
            PC->SetViewTarget(D);Check(TEXT("cannot_enter_from_far_away"),D->IsOnFoot() && PC->GetPawn()==D);Button(PC,EKeys::Gamepad_FaceButton_Top);
            if(!Enemy.IsValid() && Network) { for(TActorIterator<APlayerWheeledVehiclePawn> It(World);It;++It) { if(*It!=Car && It->FleetTeamId==2) { Enemy=*It;break; } } }
            if(!Enemy.IsValid() || !D->HandWeapon) { Check(TEXT("enemy_and_rifle_available"),false);return Finish(); }
            InitialHealth=Enemy->FindComponentByClass<UHealthComponent>()->CurrentHealth;AmmoBefore=D->HandWeapon->CurrentMagazineAmmo;
            PC->SetControlRotation((Enemy->GetActorLocation()+FVector(0,0,50)-D->GetPawnViewLocation()).Rotation());Stage(12);
        }
        else if(Phase==12 && Age>.6) { Key(PC,EKeys::Gamepad_RightShoulder,true);Stage(13); }
        else if(Phase==13 && Age>1.) { Key(PC,EKeys::Gamepad_RightShoulder,false);Snapshot(D,TEXT("firing"));Shot(TEXT("foot-fire.png"));Stage(14); }
        else if(Phase==14 && Age>1.)
        {
            Check(TEXT("rb_fires_and_consumes_ammo"),D->HandWeapon && D->HandWeapon->CurrentMagazineAmmo<AmmoBefore);
            Check(TEXT("rifle_projectiles_damage_enemy"),Enemy.IsValid() && Enemy->FindComponentByClass<UHealthComponent>()->CurrentHealth<InitialHealth);
            Telemetry->SetNumberField(TEXT("enemy_health_after_fire"),Enemy.IsValid()?Enemy->FindComponentByClass<UHealthComponent>()->CurrentHealth:-1);
            Check(TEXT("mask_reenabled"),D->IsMasked() && D->Mask->IsVisible());Axes.Add(EKeys::Gamepad_LeftY,1);Key(PC,EKeys::Gamepad_LeftThumbstick,true);Stage(15);
        }
        else if(Phase==15)
        {
            const FVector ReturnPoint=Terrain?ExitPoint:Car->GetActorLocation();
            PC->SetControlRotation(FRotator(0,(ReturnPoint-D->GetActorLocation()).Rotation().Yaw,0));
            if(Terrain)
            {
                Snapshot(D,TEXT("returning"));Telemetry->SetStringField(TEXT("return_point"),ReturnPoint.ToString());
                Telemetry->SetNumberField(TEXT("return_distance_cm"),FVector::Dist2D(ReturnPoint,D->GetActorLocation()));
                Telemetry->SetNumberField(TEXT("parked_vehicle_speed_cm_s"),Car->GetVelocity().Size());
                if(Age>12 && D->GetVelocity().Size2D()<10)
                {
                    FCollisionQueryParams Query(SCENE_QUERY_STAT(FootReturnBlockage),false,D);TArray<AActor*> Attached;D->GetAttachedActors(Attached,true,true);Query.AddIgnoredActors(Attached);
                    FHitResult Hit;
                    if(World->SweepSingleByProfile(Hit,D->GetActorLocation(),D->GetActorLocation()+(ReturnPoint-D->GetActorLocation()).GetSafeNormal2D()*100,FQuat::Identity,TEXT("Pawn"),FCollisionShape::MakeCapsule(34,88),Query))
                    { Telemetry->SetStringField(TEXT("return_blocking_actor"),GetNameSafe(Hit.GetActor()));Telemetry->SetStringField(TEXT("return_blocking_component"),GetNameSafe(Hit.GetComponent())); }
                    Check(TEXT("return_path_not_stuck"),false);return Finish();
                }
            }
            if(FVector::Dist2D(ReturnPoint,D->GetActorLocation())<(Terrain?80.f:270.f)) { Axes.Add(EKeys::Gamepad_LeftY,0);Key(PC,EKeys::Gamepad_LeftThumbstick,false);Stage(16); }
        }
        else if(Phase==16 && Age>.7) { Button(PC,EKeys::Gamepad_FaceButton_Left);Stage(17); }
        else if(Phase==17 && Age>1.)
        {
            Check(TEXT("x_returns_to_same_car_and_body"),PC->GetPawn()==Car && !D->IsOnFoot() && D->GetMesh()==Body.Get() && D->GetAttachParentActor()==Car);
            Check(TEXT("rifle_hidden_in_vehicle"),D->HandWeapon && D->HandWeapon->IsHidden());Snapshot(D,TEXT("returned"));Signal(TEXT("returned"));
            if(Terrain) { return Finish(); }
            if(Network) { Stage(18); }else { Button(PC,EKeys::Gamepad_FaceButton_Bottom);Stage(20); }
        }
        else if(Phase==18 && Age>1.) { return Finish(); }
        else if(Phase==20 && Age>1.)
        {
            Check(TEXT("second_exit_restores_animator"),D->IsOnFoot() && D->GetMesh()->GetAnimationMode()==EAnimationMode::AnimationBlueprint && Cast<UMaskDriverAnimInstance>(D->GetMesh()->GetAnimInstance()));
            Button(PC,EKeys::Gamepad_Special_Right);Stage(21);
        }
        else if(Phase==21 && Age>.5) { Check(TEXT("foot_pause_opens"),D->IsPauseMenuOpen());Button(PC,EKeys::Gamepad_FaceButton_Bottom);Stage(22); }
        else if(Phase==22 && Age>.6)
        {
            Check(TEXT("a_resumes_without_jump"),!D->IsPauseMenuOpen() && D->GetCharacterMovement()->IsMovingOnGround());
            // Explicit hostile rifle fixture: exercise real bullet/capsule contact,
            // independently from bot cadence and navigation tested elsewhere.
            FActorSpawnParameters Params;Params.Owner=Enemy.Get();Params.Instigator=Enemy.Get();
            auto* Rifle=World->SpawnActor<AWeaponPickupActor>(LoadClass<AWeaponPickupActor>(nullptr,TEXT("/Game/Blueprints/Pickups/Weapons/BP_Weapon_AssaultRifle.BP_Weapon_AssaultRifle_C")),D->GetActorLocation()+FVector(1000,0,0),FRotator::ZeroRotator,Params);
            Rifle->PickupState=EPickupState::PickedUp;Rifle->OnRep_PickupState();Rifle->SetActorScale3D(FVector(.45f));Rifle->SetActorEnableCollision(false);Rifle->SetLifeSpan(3);
            auto* Mesh=Rifle->FindComponentByClass<USkeletalMeshComponent>();
            for(int32 I=0;I<2;++I) { const auto Muzzle=Mesh->GetSocketTransform(TEXT("MuzzleSocket"));const FQuat Relative=Rifle->GetActorQuat().Inverse()*Muzzle.GetRotation();Rifle->SetActorRotation((D->GetActorLocation()-Muzzle.GetLocation()).ToOrientationQuat()*Relative.Inverse()); }
            InitialHealth=D->Health;Rifle->ServerSpawnProjectile(FTransform::Identity);Stage(23);
        }
        else if(Phase==23 && Age>1.)
        {
            Check(TEXT("hostile_bullet_hits_driver_capsule"),D->Health<InitialHealth && D->Health>0);InitialHealth=D->Health;
            UGameplayStatics::ApplyDamage(D,10,PC,Enemy.Get(),nullptr);Check(TEXT("allied_damage_filtered"),D->Health==InitialHealth);
            UGameplayStatics::ApplyDamage(D,200,Enemy->GetController(),Enemy.Get(),nullptr);Check(TEXT("driver_death_disables_body"),D->Health<=0 && !D->GetMesh()->IsVisible());Stage(24);
        }
        else if(Phase==24 && Age>4.) { Check(TEXT("death_returns_to_same_healthy_car"),PC->GetPawn()==Car && !D->IsOnFoot() && D->Health==100 && D->GetMesh()==Body.Get());Stage(30); }
        else if(Phase==30 && Age>1.)
        {
            if(RosterIndex>=6) { return Finish(); }
            APlayerWheeledVehiclePawn* Next=nullptr;const FVector P(0,4000+RosterIndex*3500,FloorZ+15);
            if(RosterIndex==0) { Next=World->SpawnActor<ARhinoPawn>(P,FRotator::ZeroRotator); }
            if(RosterIndex==1) { auto* Module=World->SpawnActor<ARhinoRearModule>(P,FRotator::ZeroRotator);Module->SetDetached(true);Next=Module; }
            if(RosterIndex==2) { Next=World->SpawnActor<AHurricanePawn>(P,FRotator::ZeroRotator); }
            if(RosterIndex==3) { Next=World->SpawnActor<APlayerWheeledVehiclePawn>(LoadClass<APlayerWheeledVehiclePawn>(nullptr,TEXT("/Game/Blueprints/Pawns/BP_PlayerVehicle.BP_PlayerVehicle_C")),P,FRotator::ZeroRotator); }
            if(RosterIndex==4) { Next=World->SpawnActor<ARhinoPawn>(P,FRotator::ZeroRotator); }
            if(RosterIndex==5) { Next=World->SpawnActor<AHurricanePawn>(P,FRotator::ZeroRotator); }
            if(!Next) { Check(TEXT("roster_fixture_spawn"),false);return Finish(); }
            PC->Possess(Next);Next->FleetTeamId=1;Current=Next;Stage(31);
        }
        else if(Phase==31 && Age>2.)
        {
            if(!Car->DriverCharacter) { return true; }Driver=Car->DriverCharacter;Body=Driver->GetMesh();
            if(RosterIndex>=4) { Button(PC,EKeys::Gamepad_FaceButton_Left);Stage(35); }else { Button(PC,EKeys::Gamepad_FaceButton_Bottom);Stage(32); }
        }
        else if(Phase==32 && Age>1.)
        {
            Check(*FString::Printf(TEXT("roster_%d_exit_same_masked_driver"),RosterIndex),PC->GetPawn()==D && D->IsOnFoot() && D->IsMasked() && D->Definition && D->GetMesh()->GetSkeletalMeshAsset()==D->Definition->Driver);
            Snapshot(D,*FString::Printf(TEXT("roster_%d"),RosterIndex));Portrait(PC,D);Shot(*FString::Printf(TEXT("roster-%d.png"),RosterIndex));Stage(34);
        }
        else if(Phase==34 && Age>.6) { PC->SetViewTarget(D);Button(PC,EKeys::Gamepad_FaceButton_Left);Stage(33); }
        else if(Phase==35 && Age>3. && CastChecked<AThunderhawkPawn>(Car)->Modes->GetMode()==EMaskVehicleMode::Combat) { Button(PC,EKeys::Gamepad_FaceButton_Bottom);Stage(32); }
        else if(Phase==33 && Age>1.) { Check(*FString::Printf(TEXT("roster_%d_reenter"),RosterIndex),PC->GetPawn()==Car && !D->IsOnFoot());++RosterIndex;Stage(30); }
        for(const auto& A:Axes) { PC->InputKey(FInputKeyEventArgs::CreateSimulated(A.Key,IE_Axis,A.Value,1,FInputDeviceId::CreateFromInternalId(0))); }
        Save(false);return true;
    }
};
TUniquePtr<FRun> Runner;
FAutoConsoleCommand Command(TEXT("MASK.OnFootSmoke"),TEXT("Persistent driver exit, Xbox locomotion/combat and replication probe."),FConsoleCommandWithArgsDelegate::CreateLambda([](const TArray<FString>& Args)
{
    if(Runner) { return; }Runner=MakeUnique<FRun>(Args.IsEmpty()?TEXT("solo"):Args[0]);
    FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda([](float Delta){return Runner->Tick(Delta);}));
}));
}
#endif
