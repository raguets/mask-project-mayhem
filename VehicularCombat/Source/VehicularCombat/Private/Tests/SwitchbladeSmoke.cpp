#include "CoreMinimal.h"
#if !UE_BUILD_SHIPPING
#include "MASK/SwitchbladePawn.h"
#include "MASK/RhinoPawn.h"
#include "MASK/MaskDriverCharacter.h"
#include "MASK/MaskVehicleDefinition.h"
#include "MASK/MaskVehicleModeComponent.h"
#include "MASK/MaskDynamicsComponent.h"
#include "Core/CustomGameMode.h"
#include "SilentValley/SilentValleyRoad.h"
#include "AI/VehicleBotController.h"
#include "ChaosWheeledVehicleMovementComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Components/HealthComponent.h"
#include "Containers/Ticker.h"
#include "Dom/JsonObject.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "HAL/IConsoleManager.h"
#include "HAL/FileManager.h"
#include "InputKeyEventArgs.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonSerializer.h"
#include "UnrealClient.h"

namespace SwitchbladeSmoke {
class FRun {
 int32 Stage=0;double Started=FPlatformTime::Seconds(),Since=Started;FString Directory;TWeakObjectPtr<ASwitchbladePawn> Car;float Height=0;bool SawLanding=false;FVector HoverStart;float HoverYaw=0;TMap<FKey,float> Axes;
 TSharedRef<FJsonObject> Checks=MakeShared<FJsonObject>(),Data=MakeShared<FJsonObject>();
 void Check(const TCHAR* N,bool V){Checks->SetBoolField(N,V);}
 void Next(int32 S){Stage=S;Since=FPlatformTime::Seconds();UE_LOG(LogTemp,Display,TEXT("SWITCHBLADE_TEST stage=%d"),S);}
 void Key(APlayerController* PC,FKey K,bool Down){if(K==EKeys::R || K==EKeys::F){Axes.Add(EKeys::Gamepad_LeftY,Down?(K==EKeys::R?1.f:-1.f):0.f);return;}if(K==EKeys::D){Axes.Add(EKeys::Gamepad_LeftX,Down?1.f:0.f);return;}if(K==EKeys::S || K==EKeys::W){Axes.Add(K==EKeys::S?EKeys::Gamepad_LeftTriggerAxis:EKeys::Gamepad_RightTriggerAxis,Down?1.f:0.f);return;}PC->InputKey(FInputKeyEventArgs::CreateSimulated(K,Down?IE_Pressed:IE_Released,Down?1.f:0.f,-1,FInputDeviceId::CreateFromInternalId(0)));}
 void Shot(const TCHAR* Name){if(!FParse::Param(FCommandLine::Get(),TEXT("NullRHI"))){FScreenshotRequest::RequestScreenshot(Directory/Name,true,false);}}
 bool Finish(bool Timeout=false){Check(TEXT("no_timeout"),!Timeout);bool Pass=!Timeout;for(const auto& I:Checks->Values){Pass&=I.Value->AsBool();}auto R=MakeShared<FJsonObject>();R->SetBoolField(TEXT("passed"),Pass);R->SetObjectField(TEXT("checks"),Checks);R->SetObjectField(TEXT("telemetry"),Data);R->SetNumberField(TEXT("stage"),Stage);FString T;FJsonSerializer::Serialize(R,TJsonWriterFactory<>::Create(&T));FFileHelper::SaveStringToFile(T,*(Directory/TEXT("switchblade.json")));FPlatformMisc::RequestExit(false);return false;}
public:
 FRun(){FParse::Value(FCommandLine::Get(),TEXT("MigrationReportDir="),Directory);IFileManager::Get().MakeDirectory(*Directory,true);}
 bool Tick(float){if(FPlatformTime::Seconds()-Started>150){return Finish(true);}UWorld* W=nullptr;for(const auto& C:GEngine->GetWorldContexts()){if(C.WorldType==EWorldType::Game){W=C.World();break;}}auto* PC=W?W->GetFirstPlayerController():nullptr;if(!PC){return true;}double E=FPlatformTime::Seconds()-Since;for(const auto& A:Axes){PC->InputKey(FInputKeyEventArgs::CreateSimulated(A.Key,IE_Axis,A.Value,1,FInputDeviceId::CreateFromInternalId(0)));}
 if(Car.IsValid()){auto S=MakeShared<FJsonObject>();S->SetNumberField(TEXT("stage"),Stage);S->SetStringField(TEXT("pilot_input"),Car->GetPilotInput().ToString());S->SetNumberField(TEXT("linear_damping"),Car->GetMesh()->GetLinearDamping());S->SetStringField(TEXT("position"),Car->GetActorLocation().ToString());S->SetStringField(TEXT("rotation"),Car->GetActorRotation().ToString());S->SetStringField(TEXT("velocity"),Car->GetVelocity().ToString());S->SetNumberField(TEXT("height"),Car->Dynamics->GroundClearanceCM);S->SetNumberField(TEXT("mode"),int(Car->Modes->GetMode()));S->SetNumberField(TEXT("target"),Car->Dynamics->GetTargetAirspeedMPS());Data->SetObjectField(TEXT("last"),S);FString T;FJsonSerializer::Serialize(S,TJsonWriterFactory<>::Create(&T));FFileHelper::SaveStringToFile(T,*(Directory/TEXT("progress.json")));}
 if(Stage==0 && W->GetTimeSeconds()>6){TMap<FString,int32> Counts;for(TActorIterator<AThunderhawkPawn> I(W);I;++I){if(I->Definition && !Cast<ARhinoRearModule>(*I)){Counts.FindOrAdd(I->Definition->VehicleName)++;}if(auto* S=Cast<ASwitchbladePawn>(*I)){Car=S;}}bool Unique=Counts.Num()==6;auto Fleet=MakeShared<FJsonObject>();for(const auto& I:Counts){Unique&=I.Value==1;Fleet->SetNumberField(I.Key,I.Value);}Data->SetObjectField(TEXT("fleet"),Fleet);Check(TEXT("six_unique_families"),Unique);Check(TEXT("switchblade_spawned"),Car.IsValid());if(!Car.IsValid()){return Finish();}auto* GM=Cast<ACustomGameMode>(W->GetAuthGameMode());Check(TEXT("switch_control"),PC->GetPawn()==Car.Get() || (GM && GM->SwitchPlayerVehicleTo(PC,Car.Get())));for(TActorIterator<AVehicleBotController> I(W);I;++I){I->SetActorTickEnabled(false);if(auto* V=Cast<AThunderhawkPawn>(I->GetPawn())){V->SetAIPilotInput(FVector::ZeroVector);auto* M=CastChecked<UChaosWheeledVehicleMovementComponent>(V->GetVehicleMovement());M->SetThrottleInput(0);M->SetBrakeInput(1);M->SetHandbrakeInput(true);}}auto* D=Car->Definition.Get();Check(TEXT("native_venom"),Car->IsNativeAircraft() && D->Faction==EMaskFaction::Venom);Check(TEXT("miles_viper"),D->DriverName==TEXT("Miles Mayhem") && D->MaskName==TEXT("Viper") && D->Driver && D->Mask && D->DriverLocomotion);Check(TEXT("no_wheels"),D->Wheels.IsEmpty() && CastChecked<UChaosWheeledVehicleMovementComponent>(Car->GetVehicleMovement())->Wheels.IsEmpty());Check(TEXT("starts_helicopter"),Car->Modes->GetMode()==EMaskVehicleMode::Road);bool Outside=true;for(TActorIterator<AActor> I(W);I;++I){TArray<UStaticMeshComponent*> M;I->GetComponents(M);for(auto* C:M){if(C->GetStaticMesh() && C->GetStaticMesh()->GetPathName().Contains(TEXT("BoulderHill"))){FVector O,X;I->GetActorBounds(true,O,X);const FVector P=Car->GetActorLocation();Outside&=FMath::Abs(P.X-O.X)>X.X+500 || FMath::Abs(P.Y-O.Y)>X.Y+500;}}}Check(TEXT("outside_boulder_hill"),Outside);Shot(TEXT("01-helicopter.png"));Next(FParse::Param(FCommandLine::Get(),TEXT("SwitchbladeFleetOnly"))?99:1);}
 else if(Stage==99 && E>2){return Finish();}
 else if(Stage==1 && E>2){Check(TEXT("landed_stable"),FMath::Abs(Car->GetActorRotation().Roll)<8 && Car->GetVelocity().Size()<100);Key(PC,EKeys::R,true);Next(2);}
 else if(Stage==2 && E>8){Data->SetNumberField(TEXT("takeoff_height_cm"),Car->Dynamics->GroundClearanceCM);Key(PC,EKeys::R,false);Check(TEXT("takes_off"),Car->Dynamics->GroundClearanceCM>300);if(Car->Dynamics->GroundClearanceCM<300){return Finish();}Next(3);}
 else if(Stage==3 && E>4){Data->SetStringField(TEXT("hover_velocity"),Car->GetVelocity().ToString());Check(TEXT("helicopter_hovers"),Car->GetVelocity().Size()<100);HoverStart=Car->GetActorLocation();HoverYaw=Car->GetActorRotation().Yaw;Shot(TEXT("02-hover.png"));Key(PC,EKeys::D,true);Next(4);}
 else if(Stage==4 && E>2){Key(PC,EKeys::D,false);Check(TEXT("turns_in_place"),FVector::Dist2D(HoverStart,Car->GetActorLocation())<200 && FMath::Abs(FMath::FindDeltaAngleDegrees(HoverYaw,Car->GetActorRotation().Yaw))>40);Next(40);}
 else if(Stage==40){const float Error=FMath::FindDeltaAngleDegrees(Car->GetActorRotation().Yaw,HoverYaw);Axes.Add(EKeys::Gamepad_LeftX,FMath::Clamp(Error/30.f,-1.f,1.f));if(FMath::Abs(Error)<8 && Car->GetMesh()->GetPhysicsAngularVelocityInRadians().Size()<.15f){Axes.Add(EKeys::Gamepad_LeftX,0);Next(41);}else if(E>15){Check(TEXT("restores_valley_heading"),false);return Finish();}}
 else if(Stage==41 && E>1){Check(TEXT("restores_valley_heading"),true);Car->Modes->ServerToggleMode();Check(TEXT("deploys"),Car->Modes->GetMode()==EMaskVehicleMode::Deploying);Next(5);}
 else if(Stage==5 && E>8){Check(TEXT("airplane_mode"),Car->Modes->GetMode()==EMaskVehicleMode::Flight);Key(PC,EKeys::S,true);Next(6);}
 else if(Stage==6 && E>6){Check(TEXT("airplane_cannot_hover"),Car->Dynamics->GetTargetAirspeedMPS()>=13.9f && Car->GetVelocity().Size2D()>1000);Data->SetNumberField(TEXT("airplane_min_speed_mps"),Car->GetVelocity().Size2D()*.01);Shot(TEXT("03-airplane.png"));Height=Car->GetActorLocation().Z;Next(60);}
 else if(Stage==60 && E>1){Car->Modes->ServerToggleMode();Next(7);}
 else if(Stage==7){SawLanding|=Car->Modes->GetMode()==EMaskVehicleMode::Landing;if(E>10){Check(TEXT("returns_helicopter_in_air"),Car->Modes->GetMode()==EMaskVehicleMode::Road && !SawLanding && Car->Dynamics->GroundClearanceCM>500);Data->SetStringField(TEXT("return_hover_velocity"),Car->GetVelocity().ToString());Check(TEXT("return_hovers"),Car->GetVelocity().Size2D()<100);Key(PC,EKeys::S,false);Key(PC,EKeys::F,true);Shot(TEXT("04-return-hover.png"));Next(8);}}
 else if(Stage==8 && E>10){Key(PC,EKeys::F,false);Next(9);}
 else if(Stage==9 && E>3){Check(TEXT("lands_on_skids"),Car->Dynamics->GroundClearanceCM<40 && Car->GetVelocity().Size()<100 && Car->GetActorUpVector().Z>.9f);FString Reason;Check(TEXT("can_exit_landed"),Car->CanDriverExit(Reason));Shot(TEXT("05-landed.png"));Next(90);}
 else if(Stage==90 && E>1){Key(PC,EKeys::Gamepad_FaceButton_Bottom,true);Key(PC,EKeys::Gamepad_FaceButton_Bottom,false);Next(10);}
 else if(Stage==10 && E>2){auto* D=Cast<AMaskDriverCharacter>(PC->GetPawn());Check(TEXT("miles_exits"),D && D->IsOnFoot() && D->Definition==Car->Definition);if(!D || !D->IsOnFoot()){return Finish();}Shot(TEXT("06-miles.png"));PC->SetViewTarget(D?static_cast<AActor*>(D):Car.Get());Next(101);}
 else if(Stage==101 && E>1){Key(PC,EKeys::Gamepad_FaceButton_Left,true);Key(PC,EKeys::Gamepad_FaceButton_Left,false);Next(11);}
 else if(Stage==11 && E>2){Check(TEXT("miles_reenters"),PC->GetPawn()==Car.Get() && !Car->IsDriverOnFoot());return Finish();}
 return true;}
};TUniquePtr<FRun> Run;FAutoConsoleCommand Command(TEXT("MASK.SwitchbladeSmoke"),TEXT("Six-family Pinewoods fleet and actual helicopter/airplane controls, no airborne teleport."),FConsoleCommandDelegate::CreateLambda([](){if(!Run){Run=MakeUnique<FRun>();FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda([](float D){return Run->Tick(D);}));}}));
}
#endif
