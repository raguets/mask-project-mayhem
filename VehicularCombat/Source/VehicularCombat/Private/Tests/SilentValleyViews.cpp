#if !UE_BUILD_SHIPPING
#include "CoreMinimal.h"
#include "SilentValley/SilentValleyRoad.h"
#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "Components/DirectionalLightComponent.h"
#include "Engine/DirectionalLight.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/HUD.h"
#include "Containers/Ticker.h"
#include "HAL/IConsoleManager.h"
#include "HAL/FileManager.h"
#include "Misc/CommandLine.h"
#include "Misc/Paths.h"
#include "UnrealClient.h"
#include "ShaderCompiler.h"

namespace SilentValleyViews
{
int32 Index=-1;double Next=0;bool Captured=false;FString Folder;TWeakObjectPtr<ACameraActor> Camera;
const FVector Places[]={FVector(-134000,-109000,8600),FVector(-75000,-78000,9400),FVector(70000,25000,15900),FVector(65000,95000,10800),FVector(-55000,125000,16500)};
bool Tick(float)
{
    UWorld* World=nullptr;for(const auto& C:GEngine->GetWorldContexts()) { if(C.WorldType==EWorldType::Game) { World=C.World();break; } }
    if(!World || World->GetTimeSeconds()<5) { return true; }
    if(GShaderCompilingManager && GShaderCompilingManager->IsCompiling()) { Next=FPlatformTime::Seconds()+5;return true; }
    auto* PC=World->GetFirstPlayerController();if(!PC) { return true; }
    const double Now=FPlatformTime::Seconds();if(Now<Next) { return true; }
    if(Index>=0 && Index<10 && !Captured) { int32 Width=0,Height=0;PC->GetViewportSize(Width,Height);UE_LOG(LogTemp,Display,TEXT("SV_VIEW_CAPTURE index=%d width=%d height=%d"),Index,Width,Height);FScreenshotRequest::RequestScreenshot(Folder/FString::Printf(TEXT("%s-zone-%d.png"),Index<5?TEXT("day"):TEXT("golden"),Index%5),true,false);Captured=true;Next=Now+1;return true; }
    Captured=false;
    ++Index;if(Index>=10) { PC->ConsoleCommand(TEXT("quit"));return false; }
    if(!Camera.IsValid()) { Camera=World->SpawnActor<ACameraActor>();Camera->GetCameraComponent()->SetFieldOfView(65); }
    FVector Target=Places[Index%5];
    if(Index%5==1 && FParse::Param(FCommandLine::Get(),TEXT("SVShowcaseViews")))
    { for(TActorIterator<ASilentValleyRoad> It(World);It;++It) { Target=It->RouteLocation(60000)+FVector(0,0,400);break; } }
    const FVector Offset=Index%5==0?FVector(4500,4500,2000):FVector(-3000,-4500,1500);
    FVector CameraPosition=Target+Offset;
    if(FParse::Param(FCommandLine::Get(),TEXT("SVEnvironmentViews")))
    {
        const FVector Lake(-105000,-55000,5400);
        if(Index%5==1) { Target=Lake+FVector(0,0,300);CameraPosition=Lake+FVector(23000,-20000,7000); }
        else if(Index%5==2) { Target=Lake+FVector(-5000,2000,300);CameraPosition=Lake+FVector(18000,-2500,600); }
        else if(Index%5==4) { Target=Places[2]+FVector(0,0,300);CameraPosition=Places[2]+FVector(1500,-3500,300); }
        else
        {
            for(TActorIterator<ASilentValleyRoad> It(World);It;++It)
            {
                const float Distance=Index%5==0?65000.f:90000.f;const FVector P=It->RouteLocation(Distance);
                CameraPosition=P+It->RouteRotation(Distance).RotateVector(FVector(-500,1400,300));
                Target=It->RouteLocation(Distance+8000)+FVector(0,0,250);break;
            }
        }
        if(PC->GetHUD()) { PC->GetHUD()->bShowHUD=false; }
    }
    Camera->SetActorLocationAndRotation(CameraPosition,(Target-CameraPosition).Rotation());PC->SetViewTarget(Camera.Get());
    for(TActorIterator<ADirectionalLight> It(World);It;++It) { if(!It->ActorHasTag(TEXT("SV_AMBIENT_FILL"))) { It->SetActorRotation(Index<5?FRotator(-40,-35,0):FRotator(-12,-35,0)); } }
    // Real-time rendered evidence only, explicitly separate from physical drive tests.
    Next=Now+5;return true;
}
FAutoConsoleCommand Command(TEXT("MASK.SilentValleyViews"),TEXT("Capture the five blockout places in daylight and golden hour; no driving validation."),FConsoleCommandDelegate::CreateLambda([]()
{
    FParse::Value(FCommandLine::Get(),TEXT("MigrationReportDir="),Folder);if(Folder.IsEmpty()) { Folder=FPaths::ProjectSavedDir()/TEXT("SilentValley/views"); }
    IFileManager::Get().MakeDirectory(*Folder,true);FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateStatic(&Tick));
}));
}
#endif
