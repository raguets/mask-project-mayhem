#include "MASK/MaskDriverCharacter.h"
#include "MASK/MaskVehicleDefinition.h"
#include "MASK/MaskDriverAnimInstance.h"
#include "MASK/MaskDriverMovementComponent.h"
#include "SilentValley/SilentValleyMission.h"
#include "Pawns/PlayerWheeledVehiclePawn.h"
#include "Actors/WeaponPickupActor.h"
#include "Components/HealthComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "Camera/PlayerCameraManager.h"
#include "Components/InputComponent.h"
#include "Core/CustomGameMode.h"
#include "Core/OnlineGameInstance.h"
#include "UI/PlayerHUD.h"
#include "Kismet/GameplayStatics.h"
#include "Net/UnrealNetwork.h"
#include "TimerManager.h"

AMaskDriverCharacter::AMaskDriverCharacter(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer.SetDefaultSubobjectClass<UMaskDriverMovementComponent>(ACharacter::CharacterMovementComponentName))
{
    PrimaryActorTick.bCanEverTick=true;bReplicates=true;SetNetUpdateFrequency(60.f);SetMinNetUpdateFrequency(20.f);
    AutoPossessAI=EAutoPossessAI::Disabled;bUseControllerRotationYaw=true;
    GetCapsuleComponent()->InitCapsuleSize(34,88);GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    // The legacy vehicle project makes Pawn ignore bullets; this capsule is a damage target.
    GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_GameTraceChannel1,ECR_Block);
    GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_Visibility,ECR_Block);
    GetMesh()->SetCollisionEnabled(ECollisionEnabled::NoCollision);GetMesh()->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
    GetMesh()->SetRelativeLocation(FVector(0,0,-88));
    Hair=CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("DriverHair"));Hair->SetupAttachment(GetMesh());Hair->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Mask=CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("DriverMask"));Mask->SetupAttachment(GetMesh());Mask->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    CameraArm=CreateDefaultSubobject<USpringArmComponent>(TEXT("FootCameraArm"));CameraArm->SetupAttachment(GetCapsuleComponent());
    CameraArm->TargetArmLength=300;CameraArm->SetRelativeLocation(FVector(0,0,65));CameraArm->SocketOffset=FVector(0,45,0);CameraArm->bUsePawnControlRotation=true;
    Camera=CreateDefaultSubobject<UCameraComponent>(TEXT("FootCamera"));Camera->SetupAttachment(CameraArm);Camera->FieldOfView=85;
    GetCharacterMovement()->MaxWalkSpeed=240;GetCharacterMovement()->MaxAcceleration=1600;GetCharacterMovement()->BrakingDecelerationWalking=1600;
    GetCharacterMovement()->JumpZVelocity=450;GetCharacterMovement()->GravityScale=1.15f;GetCharacterMovement()->AirControl=.25f;
    GetCharacterMovement()->MaxStepHeight=45;GetCharacterMovement()->bOrientRotationToMovement=false;
    GetCharacterMovement()->NetworkSmoothingMode=ENetworkSmoothingMode::Exponential;
}
void AMaskDriverCharacter::InitializeDriver(APlayerWheeledVehiclePawn* Vehicle)
{
    SourceVehicle=Vehicle;Definition=Vehicle?Vehicle->GetDriverDefinition():nullptr;SetInstigator(this);
}
void AMaskDriverCharacter::BeginPlay()
{
    Super::BeginPlay();RefreshDriverState();
    if(HasAuthority()) { OnTakeAnyDamage.AddDynamic(this,&AMaskDriverCharacter::TakeDriverDamage); }
}
void AMaskDriverCharacter::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME(AMaskDriverCharacter,SourceVehicle);DOREPLIFETIME(AMaskDriverCharacter,Definition);DOREPLIFETIME(AMaskDriverCharacter,bOnFoot);
    DOREPLIFETIME(AMaskDriverCharacter,bMaskVisible);DOREPLIFETIME(AMaskDriverCharacter,bSprinting);DOREPLIFETIME(AMaskDriverCharacter,bReloading);
    DOREPLIFETIME(AMaskDriverCharacter,HandWeapon);DOREPLIFETIME(AMaskDriverCharacter,FleetTeamId);DOREPLIFETIME(AMaskDriverCharacter,Health);
}
void AMaskDriverCharacter::OnRep_DriverState() { RefreshDriverState(); }
void AMaskDriverCharacter::RefreshDriverState()
{
    if(!Definition) { GetMesh()->SetVisibility(false);return; }
    const bool NewMesh=GetMesh()->GetSkeletalMeshAsset()!=Definition->Driver;
    if(NewMesh)
    {
        GetMesh()->SetSkeletalMeshAsset(Definition->Driver);Hair->SetSkeletalMeshAsset(Definition->Hair);Mask->SetSkeletalMeshAsset(Definition->Mask);
        Hair->SetLeaderPoseComponent(GetMesh());Mask->SetLeaderPoseComponent(GetMesh());
    }
    GetMesh()->SetVisibility(Health>0.f);Hair->SetVisibility(Health>0.f && !bMaskVisible);Mask->SetVisibility(Health>0.f && bMaskVisible);
    Camera->SetActive(bOnFoot);SetReplicateMovement(bOnFoot);
    if(bOnFoot)
    {
        if(GetAttachParentActor()) { DetachFromActor(FDetachmentTransformRules::KeepWorldTransform); }
        GetCapsuleComponent()->SetCollisionEnabled(Health>0.f?ECollisionEnabled::QueryAndPhysics:ECollisionEnabled::NoCollision);
        if(Health>0.f && GetCharacterMovement()->MovementMode==MOVE_None) { GetCharacterMovement()->SetMovementMode(MOVE_Walking); }
        if(NewMesh || !bWasOnFoot) { GetMesh()->SetRelativeLocation(FVector(0,0,-88));GetMesh()->SetRelativeRotation(FRotator::ZeroRotator); }
        GetMesh()->SetOwnerNoSee(false);Hair->SetOwnerNoSee(false);Mask->SetOwnerNoSee(false);
        if(GetMesh()->GetAnimationMode()!=EAnimationMode::AnimationBlueprint || GetMesh()->GetAnimClass()!=UMaskDriverAnimInstance::StaticClass()) { GetMesh()->SetAnimInstanceClass(UMaskDriverAnimInstance::StaticClass()); }
    }
    else if(IsValid(SourceVehicle))
    {
        GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);GetCharacterMovement()->DisableMovement();
        if(GetAttachParentActor()!=SourceVehicle) { AttachToComponent(SourceVehicle->GetMesh(),FAttachmentTransformRules::KeepRelativeTransform); }
        SetActorRelativeTransform(FTransform::Identity);
        if(NewMesh || bWasOnFoot || !GetMesh()->GetSingleNodeInstance())
        { GetMesh()->SetRelativeLocation(Definition->DriverLocation);GetMesh()->SetRelativeRotation(FRotator::ZeroRotator);GetMesh()->PlayAnimation(Definition->DrivingPose,true); }
    }
    bWasOnFoot=bOnFoot;
    if(HandWeapon)
    {
        HandWeapon->SetActorHiddenInGame(!bOnFoot || Health<=0.f);
        FName Hand=TEXT("hand.R");if(GetMesh()->GetBoneIndex(Hand)==INDEX_NONE) { Hand=TEXT("hand_R"); }
        if(HandWeapon->GetAttachParentActor()!=this) { HandWeapon->AttachToComponent(GetMesh(),FAttachmentTransformRules::SnapToTargetNotIncludingScale,Hand);HandWeapon->SetActorScale3D(FVector(.45f)); }
        TArray<UPrimitiveComponent*> Parts;HandWeapon->GetComponents(Parts);for(auto* Part:Parts) { Part->SetCollisionEnabled(ECollisionEnabled::NoCollision); }
    }
}
void AMaskDriverCharacter::LeaveVehicle(const FTransform& Exit,APlayerController* Player)
{
    if(!HasAuthority() || !Player || !SourceVehicle || bOnFoot) { return; }
    FleetTeamId=SourceVehicle->FleetTeamId;bOnFoot=true;bSprinting=false;Status.Reset();
    if(auto* GM=Cast<ACustomGameMode>(GetWorld()->GetAuthGameMode())) { GM->RememberPlayerVehicle(Player,SourceVehicle); }
    DetachFromActor(FDetachmentTransformRules::KeepWorldTransform);SetActorTransform(Exit,false,nullptr,ETeleportType::TeleportPhysics);
    GetCharacterMovement()->StopMovementImmediately();RefreshDriverState();
    Player->Possess(this);SetOwner(Player);Player->SetControlRotation(Exit.Rotator());SourceVehicle->SetOwner(Player);
    if(!HandWeapon)
    {
        auto* WeaponClass=LoadClass<AWeaponPickupActor>(nullptr,TEXT("/Game/Blueprints/Pickups/Weapons/BP_Weapon_AssaultRifle.BP_Weapon_AssaultRifle_C"));
        FActorSpawnParameters Params;Params.Owner=this;Params.Instigator=this;Params.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
        HandWeapon=GetWorld()->SpawnActor<AWeaponPickupActor>(WeaponClass,GetActorTransform(),Params);
        if(HandWeapon) { HandWeapon->PickupState=EPickupState::PickedUp;HandWeapon->OnRep_PickupState(); }
    }
    RefreshDriverState();ForceNetUpdate();SourceVehicle->ForceNetUpdate();
}
void AMaskDriverCharacter::ServerEnterVehicle_Implementation()
{
    auto* PC=Cast<APlayerController>(GetController());
    if(auto* Mission=ASilentValleyMission::Find(GetWorld());Mission && Mission->IsTerminal()) { Mission->Retry(PC);return; }
    if(!PC || !bOnFoot || Health<=0.f || bPaused) { return; }
    if(!IsValid(SourceVehicle)) { ClientStatus(TEXT("Le vehicule a ete detruit"));return; }
    const auto* Life=SourceVehicle->FindComponentByClass<UHealthComponent>();
    if(!Life || Life->CurrentHealth<=0.f || SourceVehicle->GetController() || SourceVehicle->DriverCharacter!=this) { ClientStatus(TEXT("Vehicule indisponible"));return; }
    // A long truck's origin is not its door. Use the same access points as exit.
    float DoorDistance=BIG_NUMBER;
    for(const FVector Local:SourceVehicle->GetDriverExitOffsets())
    { DoorDistance=FMath::Min(DoorDistance,static_cast<float>(FVector::Dist2D(GetActorLocation(),SourceVehicle->GetActorTransform().TransformPosition(Local)))); }
    const float DoorHeight=SourceVehicle->GetActorTransform().TransformPosition(Definition?Definition->DriverLocation:FVector::ZeroVector).Z;
    const bool NearOriginalEntry=FVector::Dist(GetActorLocation(),SourceVehicle->GetActorLocation())<=400.f;
    if((DoorDistance>225.f && !NearOriginalEntry) || FMath::Abs(GetActorLocation().Z-DoorHeight)>250.f || !GetCharacterMovement()->IsMovingOnGround()) { ClientStatus(TEXT("Approchez d'une porte du vehicule au sol pour remonter"));return; }
    if(SourceVehicle->GetVelocity().Size()>15.f) { ClientStatus(TEXT("Le vehicule doit etre a l'arret"));return; }
    bFiring=false;bSprinting=false;bOnFoot=false;LookInput=FVector2D::ZeroVector;RefreshDriverState();
    PC->Possess(SourceVehicle);SetOwner(SourceVehicle);ForceNetUpdate();SourceVehicle->ForceNetUpdate();
}
void AMaskDriverCharacter::ToggleMaskFromVehicle() { if(HasAuthority()) { bMaskVisible=!bMaskVisible;RefreshDriverState();ForceNetUpdate(); } }
void AMaskDriverCharacter::ServerToggleMask_Implementation() { if(bOnFoot && Health>0.f) { ToggleMaskFromVehicle(); } }
void AMaskDriverCharacter::ServerSetSprint_Implementation(bool Value) { bSprinting=Value && bOnFoot && Health>0.f;GetCharacterMovement()->MaxWalkSpeed=bSprinting?400.f:240.f; }
void AMaskDriverCharacter::ServerSetFiring_Implementation(bool Value) { bFiring=Value && bOnFoot && Health>0.f; }
void AMaskDriverCharacter::ClientStatus_Implementation(const FString& Value) { Status=Value; }
void AMaskDriverCharacter::PossessedBy(AController* NewController) { Super::PossessedBy(NewController);bViewInitialized=false;InitializeLocalView(); }
void AMaskDriverCharacter::PawnClientRestart() { Super::PawnClientRestart();bViewInitialized=false;InitializeLocalView(); }
void AMaskDriverCharacter::InitializeLocalView()
{
    auto* PC=Cast<APlayerController>(GetController());if(!IsLocallyControlled() || !PC || bViewInitialized) { return; }
    PC->SetViewTarget(this);PC->PlayerCameraManager->ViewPitchMin=-65;PC->PlayerCameraManager->ViewPitchMax=65;
    PC->bShowMouseCursor=false;PC->SetInputMode(FInputModeGameOnly());
    if(auto* HUD=Cast<APlayerHUD>(PC->GetHUD())) { HUD->SetOnFootMode(true);bViewInitialized=true; }
}
void AMaskDriverCharacter::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);RefreshDriverState();if(!bOnFoot) { return; }
    if(IsLocallyControlled())
    {
        InitializeLocalView();if(!bPaused && Health>0.f) { AddControllerYawInput(LookInput.X*105.f*DeltaSeconds);AddControllerPitchInput(-LookInput.Y*75.f*DeltaSeconds); }
    }
    GetCharacterMovement()->MaxWalkSpeed=bSprinting?400.f:240.f;
    if(HandWeapon) { HandWeapon->SetActorRotation(GetBaseAimRotation()); }
    if(!HasAuthority() || Health<=0.f || !HandWeapon) { return; }
    const float Now=GetWorld()->GetTimeSeconds();
    if(bReloading && Now>=ReloadAt)
    {
        const int32 Add=FMath::Min(HandWeapon->MagazineSize-HandWeapon->CurrentMagazineAmmo,HandWeapon->CurrentAmmo);
        HandWeapon->CurrentMagazineAmmo+=Add;HandWeapon->CurrentAmmo-=Add;bReloading=false;HandWeapon->ForceNetUpdate();
    }
    if(bFiring && !bReloading && Now>=NextShotAt)
    {
        if(HandWeapon->CurrentMagazineAmmo<=0)
        { if(HandWeapon->CurrentAmmo>0) { bReloading=true;ReloadAt=Now+HandWeapon->ReloadTime; }return; }
        if(HandWeapon->FireFromDriver(this)) { --HandWeapon->CurrentMagazineAmmo;HandWeapon->ForceNetUpdate();NextShotAt=Now+FMath::Max(.1f,HandWeapon->TimeBetweenShots); }
    }
}
void AMaskDriverCharacter::MoveForward(float Value) { if(!bPaused && bOnFoot && Health>0.f) { AddMovementInput(FRotationMatrix(FRotator(0,GetControlRotation().Yaw,0)).GetUnitAxis(EAxis::X),Value); } }
void AMaskDriverCharacter::MoveRight(float Value) { if(!bPaused && bOnFoot && Health>0.f) { AddMovementInput(FRotationMatrix(FRotator(0,GetControlRotation().Yaw,0)).GetUnitAxis(EAxis::Y),Value); } }
void AMaskDriverCharacter::LookPitch(float Value) { LookInput.Y=bPaused?0.f:Value; }
void AMaskDriverCharacter::LookYaw(float Value) { LookInput.X=bPaused?0.f:Value; }
void AMaskDriverCharacter::LookPitchMouse(float Value) { if(!bPaused) { AddControllerPitchInput(-Value); } }
void AMaskDriverCharacter::LookYawMouse(float Value) { if(!bPaused) { AddControllerYawInput(Value); } }
void AMaskDriverCharacter::JumpOrResume() { if(bPaused) { TogglePause();return; }if(bOnFoot && Health>0.f) { Jump(); } }
void AMaskDriverCharacter::SprintPressed() { if(!bPaused) { bSprinting=true;ServerSetSprint(true); } }
void AMaskDriverCharacter::SprintReleased() { bSprinting=false;ServerSetSprint(false); }
void AMaskDriverCharacter::FirePressed() { if(!bPaused) { ServerSetFiring(true); } }
void AMaskDriverCharacter::FireReleased() { ServerSetFiring(false); }
void AMaskDriverCharacter::TogglePause()
{
    if(!IsLocallyControlled()) { return; }bPaused=!bPaused;
    if(bPaused) { ServerSetFiring(false);SprintReleased();LookInput=FVector2D::ZeroVector;GetCharacterMovement()->StopMovementImmediately(); }
    if(GetNetMode()==NM_Standalone) { UGameplayStatics::SetGamePaused(this,bPaused); }
}
void AMaskDriverCharacter::Resume() { if(bPaused) { TogglePause(); } }
void AMaskDriverCharacter::MaskOrMainMenu()
{
    if(bPaused) { if(auto* GI=Cast<UOnlineGameInstance>(GetGameInstance())) { GI->ReturnToMainMenu(); }return; }ServerToggleMask();
}
void AMaskDriverCharacter::EnterFromInput() { if(!bPaused) { ServerEnterVehicle(); } }
void AMaskDriverCharacter::MaskFromInput() { if(!bPaused) { ServerToggleMask(); } }
void AMaskDriverCharacter::ShowScores() { if(auto* PC=Cast<APlayerController>(GetController())) { if(auto* HUD=Cast<APlayerHUD>(PC->GetHUD())) { HUD->bShowPlayerScores=true; } } }
void AMaskDriverCharacter::HideScores() { if(auto* PC=Cast<APlayerController>(GetController())) { if(auto* HUD=Cast<APlayerHUD>(PC->GetHUD())) { HUD->bShowPlayerScores=false; } } }
void AMaskDriverCharacter::SetupPlayerInputComponent(UInputComponent* Input)
{
    Super::SetupPlayerInputComponent(Input);
    Input->BindKey(EKeys::F6,IE_Pressed,this,&AMaskDriverCharacter::EnterFromInput);
    Input->BindAxis(TEXT("OnFootForward"),this,&AMaskDriverCharacter::MoveForward);Input->BindAxis(TEXT("MoveRight"),this,&AMaskDriverCharacter::MoveRight);
    Input->BindAxis(TEXT("LookUpRate"),this,&AMaskDriverCharacter::LookPitch);Input->BindAxis(TEXT("LookRightRate"),this,&AMaskDriverCharacter::LookYaw);
    Input->BindAxis(TEXT("LookUp"),this,&AMaskDriverCharacter::LookPitchMouse);Input->BindAxis(TEXT("LookRight"),this,&AMaskDriverCharacter::LookYawMouse);
    Input->BindAction(TEXT("OnFootJump"),IE_Pressed,this,&AMaskDriverCharacter::JumpOrResume).bExecuteWhenPaused=true;Input->BindAction(TEXT("OnFootJump"),IE_Released,this,&ACharacter::StopJumping);
    Input->BindAction(TEXT("OnFootSprint"),IE_Pressed,this,&AMaskDriverCharacter::SprintPressed);Input->BindAction(TEXT("OnFootSprint"),IE_Released,this,&AMaskDriverCharacter::SprintReleased);
    Input->BindAction(TEXT("OnFootFire"),IE_Pressed,this,&AMaskDriverCharacter::FirePressed);Input->BindAction(TEXT("OnFootFire"),IE_Released,this,&AMaskDriverCharacter::FireReleased);
    Input->BindKey(EKeys::Gamepad_FaceButton_Left,IE_Pressed,this,&AMaskDriverCharacter::EnterFromInput);Input->BindKey(EKeys::E,IE_Pressed,this,&AMaskDriverCharacter::EnterFromInput);
    Input->BindKey(EKeys::Gamepad_FaceButton_Top,IE_Pressed,this,&AMaskDriverCharacter::MaskOrMainMenu).bExecuteWhenPaused=true;Input->BindKey(EKeys::M,IE_Pressed,this,&AMaskDriverCharacter::MaskFromInput);
    Input->BindKey(EKeys::Gamepad_Special_Right,IE_Pressed,this,&AMaskDriverCharacter::TogglePause).bExecuteWhenPaused=true;
    Input->BindKey(EKeys::Gamepad_FaceButton_Right,IE_Pressed,this,&AMaskDriverCharacter::Resume).bExecuteWhenPaused=true;
    Input->BindKey(EKeys::Gamepad_Special_Left,IE_Pressed,this,&AMaskDriverCharacter::ShowScores);Input->BindKey(EKeys::Gamepad_Special_Left,IE_Released,this,&AMaskDriverCharacter::HideScores);
}
void AMaskDriverCharacter::TakeDriverDamage(AActor*,float Amount,const UDamageType*,AController* InstigatedBy,AActor*)
{
    if(!HasAuthority() || !bOnFoot || Health<=0.f || Amount<=0.f) { return; }
    const auto* Car=InstigatedBy?Cast<APlayerWheeledVehiclePawn>(InstigatedBy->GetPawn()):nullptr;
    const auto* Other=InstigatedBy?Cast<AMaskDriverCharacter>(InstigatedBy->GetPawn()):nullptr;
    const int32 Team=Car?Car->FleetTeamId:Other?Other->FleetTeamId:0;if(Team && Team==FleetTeamId) { return; }
    Health=FMath::Max(0.f,Health-Amount);OnRep_Health();ForceNetUpdate();
    if(Health<=0.f) { GetWorldTimerManager().SetTimer(RespawnTimer,this,&AMaskDriverCharacter::RespawnDriver,3.f,false); }
}
void AMaskDriverCharacter::OnRep_Health() { if(Health<=0.f) { bFiring=false;GetCharacterMovement()->DisableMovement(); }RefreshDriverState(); }
void AMaskDriverCharacter::RespawnDriver()
{
    auto* PC=Cast<APlayerController>(GetController());if(!PC) { return; }
    const auto* Life=IsValid(SourceVehicle)?SourceVehicle->FindComponentByClass<UHealthComponent>():nullptr;
    if(Life && Life->CurrentHealth>0.f && !SourceVehicle->GetController())
    { Health=100;bOnFoot=false;bSprinting=false;bFiring=false;RefreshDriverState();PC->Possess(SourceVehicle);SetOwner(SourceVehicle);ForceNetUpdate();return; }
    if(auto* GM=Cast<ACustomGameMode>(GetWorld()->GetAuthGameMode())) { PC->UnPossess();GM->ServerStartRespawn(PC);Destroy(); }
}
void AMaskDriverCharacter::EndPlay(const EEndPlayReason::Type Reason)
{
    if(HasAuthority() && IsValid(HandWeapon)) { HandWeapon->Destroy(); }Super::EndPlay(Reason);
}
