#if !UE_BUILD_SHIPPING
#include "SilentValley/SilentValleyMission.h"
#include "SilentValley/SilentValleyCheckpoint.h"
#include "MASK/ThunderhawkPawn.h"
#include "AI/VehicleBotController.h"
#include "Actors/ProjectileActor.h"
#include "Actors/WeaponPickupActor.h"
#include "Core/CustomPlayerState.h"
#include "Components/HealthComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "ChaosWheeledVehicleMovementComponent.h"
#include "Containers/Ticker.h"
#include "Dom/JsonObject.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "HAL/FileManager.h"
#include "HAL/IConsoleManager.h"
#include "InputKeyEventArgs.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonSerializer.h"
#include "UnrealClient.h"

namespace SVMissionSmoke
{
class FRun
{
    FString Directory,Slot;int32 Stage=0,Shots=0;double Started=FPlatformTime::Seconds();float StageAt=0,EnemyHealth=0;
    TArray<FVector> Zones;FGuid FirstRun;bool bFire=false;
    TSharedRef<FJsonObject> Checks=MakeShared<FJsonObject>(),Telemetry=MakeShared<FJsonObject>();
    void Check(const TCHAR* Name,bool Value){Checks->SetBoolField(Name,Value);}
    void Save(bool Complete)
    {
        bool Passed=Complete && Checks->Values.Num()>=12;for(const auto& P:Checks->Values){Passed&=P.Value->AsBool();}
        auto R=MakeShared<FJsonObject>();R->SetBoolField(TEXT("passed"),Passed);R->SetBoolField(TEXT("complete"),Complete);R->SetNumberField(TEXT("stage"),Stage);R->SetObjectField(TEXT("checks"),Checks);R->SetObjectField(TEXT("telemetry"),Telemetry);
        R->SetStringField(TEXT("method"),TEXT("Actual mission on saved map. Explicit player placement and weapon aim between fixtures, not driven route/manual aim. Xbox fire pulses retain ammo/cooldown/projectile/health code. Enemy navigation frozen only during ballistic aim. Save slot isolated by CLI. Timers, ordering, pickup, extraction, death and retry use production code."));
        FString Json;FJsonSerializer::Serialize(R,TJsonWriterFactory<>::Create(&Json));FFileHelper::SaveStringToFile(Json,*(Directory/TEXT("mission.json")));
    }
    bool Finish(){Save(true);FPlatformMisc::RequestExit(false);return false;}
    void Move(AThunderhawkPawn* Car,FVector P,FRotator R=FRotator::ZeroRotator)
    { Car->SetActorLocationAndRotation(P+FVector(0,0,25),R,false,nullptr,ETeleportType::TeleportPhysics);Car->GetMesh()->SetPhysicsLinearVelocity(FVector::ZeroVector);Car->GetMesh()->SetPhysicsAngularVelocityInRadians(FVector::ZeroVector); }
    void Next(int32 Value,UWorld* World){Stage=Value;StageAt=World->GetTimeSeconds();Save(false);}
    void Key(APlayerController* PC,FKey K,bool Down){PC->InputKey(FInputKeyEventArgs::CreateSimulated(K,Down?IE_Pressed:IE_Released,Down?1.f:0.f,-1,FInputDeviceId::CreateFromInternalId(0)));}
    void Shot(const TCHAR* Name)
    {
        if(FParse::Param(FCommandLine::Get(),TEXT("NullRHI"))){return;}const FString Path=Directory/Name;
        FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda([Path](float){FScreenshotRequest::RequestScreenshot(Path,true,false);return false;}),.6f);
    }
    void Aim(AThunderhawkPawn* Car,APlayerWheeledVehiclePawn* Target)
    {
        if(!IsValid(Target)){return;}
        const auto* PC=Cast<APlayerController>(Car->GetController());const auto* State=PC?Cast<ACustomPlayerState>(PC->PlayerState):nullptr;
        AWeaponPickupActor* Weapon=State?State->PrimaryWeapon:nullptr;
        if(!Weapon){return;}auto* Mesh=Weapon->FindComponentByClass<USkeletalMeshComponent>();if(!Mesh){return;}
        const FVector Center=Target->GetMesh()->Bounds.Origin;
        for(int32 I=0;I<2;++I)
        { const auto Muzzle=Mesh->GetSocketTransform(TEXT("MuzzleSocket"));const FQuat Relative=Weapon->GetActorQuat().Inverse()*Muzzle.GetRotation();Weapon->SetActorRotation((Center-Muzzle.GetLocation()).ToOrientationQuat()*Relative.Inverse()); }
        Telemetry->SetStringField(TEXT("aim_weapon"),Weapon->GetName());Telemetry->SetStringField(TEXT("muzzle"),Mesh->GetSocketLocation(TEXT("MuzzleSocket")).ToString());Telemetry->SetStringField(TEXT("target"),Center.ToString());
        Telemetry->SetNumberField(TEXT("aim_dot"),FVector::DotProduct(Mesh->GetSocketRotation(TEXT("MuzzleSocket")).Vector(),(Center-Mesh->GetSocketLocation(TEXT("MuzzleSocket"))).GetSafeNormal()));
    }
public:
    FRun()
    { FParse::Value(FCommandLine::Get(),TEXT("MigrationReportDir="),Directory);FParse::Value(FCommandLine::Get(),TEXT("SVMissionSaveSlot="),Slot);IFileManager::Get().MakeDirectory(*Directory,true); }
    bool Tick(float)
    {
        if(FPlatformTime::Seconds()-Started>120){Check(TEXT("no_timeout"),false);return Finish();}
        UWorld* W=nullptr;for(const auto& C:GEngine->GetWorldContexts()){if(C.WorldType==EWorldType::Game){W=C.World();break;}}
        auto* M=ASilentValleyMission::Find(W);auto* PC=W?W->GetFirstPlayerController():nullptr;auto* Car=PC?Cast<AThunderhawkPawn>(PC->GetPawn()):nullptr;
        if(!M || !PC || !Car){return true;}const float Age=W->GetTimeSeconds()-StageAt;
        if(Stage==0 && M->Phase==ESVPhase::Departure)
        {
            Check(TEXT("authority_and_real_map"),M->HasAuthority() && W->GetMapName().Contains(TEXT("SilentValley")));Zones.Init(FVector::ZeroVector,5);
            for(TActorIterator<ASilentValleyCheckpoint> It(W);It;++It){if(Zones.IsValidIndex(It->ZoneIndex)){Zones[It->ZoneIndex]=It->GetActorLocation();}}
            FirstRun=M->RunId;Move(Car,Zones[4]);Next(1,W);
        }
        else if(Stage==1 && Age>.5){Check(TEXT("out_of_order_extraction_ignored"),M->Phase==ESVPhase::Departure);Move(Car,Zones[0]);Next(2,W);}
        else if(Stage==2 && Age>.5){Check(TEXT("departure_advances_once"),M->Phase==ESVPhase::Travel && M->TargetZone==1);Move(Car,Zones[1]);Next(3,W);}
        else if(Stage==3 && Age>.5){Check(TEXT("pinewood_targets_eagle"),M->Phase==ESVPhase::Travel && M->TargetZone==2);Move(Car,Zones[2]);Next(4,W);}
        else if(Stage==4 && M->Phase==ESVPhase::Intercept)
        {
            Check(TEXT("recon_spawns_existing_escort"),IsValid(M->Enemy) && M->Enemy->GetController());
            if(!IsValid(M->Enemy)){return Finish();}EnemyHealth=M->Enemy->FindComponentByClass<UHealthComponent>()->CurrentHealth;
            Move(Car,Zones[3]);Next(5,W);
        }
        else if(Stage==5 && M->Phase==ESVPhase::Combat)
        {
            Check(TEXT("quarry_activates_ai"),M->Enemy->GetController()->IsActorTickEnabled());
            const FVector P=M->Enemy->GetActorLocation()+FVector(0,-2200,0);const FRotator R=(M->Enemy->GetActorLocation()-P).Rotation();
            Move(Car,P,R);PC->SetControlRotation(R);Key(PC,EKeys::Gamepad_LeftThumbstick,true);Key(PC,EKeys::Gamepad_LeftThumbstick,false);Key(PC,EKeys::Gamepad_LeftShoulder,true);Shot(TEXT("combat.png"));Next(6,W);
        }
        else if(Stage==6 && Age>2)
        {
            // Freeze only navigation for reproducible ballistic aim; retain the
            // actual weapon, projectile, collision, damage and mission logic.
            M->Enemy->GetController()->SetActorTickEnabled(false);
            M->Enemy->GetVehicleMovementComponent()->SetThrottleInput(0);M->Enemy->GetVehicleMovementComponent()->SetHandbrakeInput(true);
            M->Enemy->GetMesh()->SetPhysicsLinearVelocity(FVector::ZeroVector);M->Enemy->GetMesh()->SetPhysicsAngularVelocityInRadians(FVector::ZeroVector);
            M->Enemy->GetMesh()->SetSimulatePhysics(false);
            // Input actions are processed after this core ticker. Prevent the
            // vehicle's camera aim tick replacing the explicit fixture aim.
            Car->SetActorTickEnabled(false);
            Aim(Car,M->Enemy);Key(PC,EKeys::Gamepad_RightShoulder,true);bFire=true;Shots=1;Next(7,W);
        }
        else if(Stage==7)
        {
            Aim(Car,M->Enemy);
            const auto* CurrentLife=IsValid(M->Enemy)?M->Enemy->FindComponentByClass<UHealthComponent>():nullptr;
            Telemetry->SetNumberField(TEXT("enemy_health"),CurrentLife?CurrentLife->CurrentHealth:0);
            if(Age>Shots*3.f) { Key(PC,EKeys::Gamepad_RightShoulder,false);Aim(Car,M->Enemy);Key(PC,EKeys::Gamepad_RightShoulder,true);++Shots; }
            if(M->Phase==ESVPhase::Recover)
            { Check(TEXT("real_projectiles_neutralize_escort"),true);Key(PC,EKeys::Gamepad_RightShoulder,false);bFire=false;Car->SetActorTickEnabled(true);Move(Car,M->TargetLocation);Shot(TEXT("recovery.png"));Next(8,W); }
            else if(Age>20)
            {
                const auto* Life=IsValid(M->Enemy)?M->Enemy->FindComponentByClass<UHealthComponent>():nullptr;
                Check(TEXT("real_projectiles_neutralize_escort"),false);Check(TEXT("projectiles_damage_escort"),Life && Life->CurrentHealth<EnemyHealth);
                Key(PC,EKeys::Gamepad_RightShoulder,false);return Finish();
            }
        }
        else if(Stage==8 && M->Phase==ESVPhase::Extract){Check(TEXT("stationary_pickup_advances_to_extract"),true);Move(Car,Zones[4]);Next(9,W);}
        else if(Stage==9 && M->Phase==ESVPhase::Success && M->bRewardSaved)
        {
            Check(TEXT("extraction_success_and_save"),true);auto* Data=Cast<USilentValleyProgress>(UGameplayStatics::LoadGameFromSlot(Slot,0));
            Check(TEXT("one_local_reward"),Data && Data->TechComponents==M->Reward && Data->RewardedRuns.Num()==1);Shot(TEXT("success.png"));Next(10,W);
        }
        else if(Stage==10 && Age>2)
        {
            auto* Data=Cast<USilentValleyProgress>(UGameplayStatics::LoadGameFromSlot(Slot,0));Check(TEXT("reward_not_repeated"),Data && Data->RewardedRuns.Num()==1 && Data->TechComponents==M->Reward);
            Car->ServerRetryMission();Next(11,W);
        }
        else if(Stage==11 && M->RunId!=FirstRun)
        {
            Check(TEXT("retry_rebuilds_clean_mission"),!IsValid(M->Enemy) && M->Phase!=ESVPhase::Success);
            UGameplayStatics::ApplyDamage(Car,100000,PC,Car,nullptr);Next(12,W);
        }
        else if(Stage==12 && M->Phase==ESVPhase::Failed){Check(TEXT("all_players_down_fails"),true);Check(TEXT("no_timeout"),true);return Finish();}
        return true;
    }
};
TUniquePtr<FRun> Run;
FAutoConsoleCommand Command(TEXT("MASK.SilentValleyMissionTest"),TEXT("Ordered mission/combat/reward/retry fixture, isolated save required."),FConsoleCommandDelegate::CreateLambda([]()
{
    FString Slot;FParse::Value(FCommandLine::Get(),TEXT("SVMissionSaveSlot="),Slot);
    if(!Slot.StartsWith(TEXT("SV_MissionTest_"))) { UE_LOG(LogTemp,Error,TEXT("Mission fixture requires an isolated SV_MissionTest_ save slot"));return; }
    if(!Run){Run=MakeUnique<FRun>();FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda([](float D){return Run->Tick(D);}));}
}));
}
#endif
