#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "MaskAssetEditorLibrary.generated.h"

/** Narrow editor bridge for PhysicsAsset data not exposed by the Python API. */
UCLASS()
class UMaskAssetEditorLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()
public:
	UFUNCTION(BlueprintCallable, Category="MASK|Editor")
	static class UBlendSpace* CreateDriverLocomotion(const FString& AssetPath,class USkeleton* Skeleton,const TArray<class UAnimSequence*>& Animations,const TArray<FVector>& Positions);
	UFUNCTION(BlueprintCallable, Category="MASK|Editor")
	static bool ConfigureThunderhawkChassis(class USkeletalMesh* Mesh);
	UFUNCTION(BlueprintCallable, Category="MASK|Editor")
	static bool ConfigureRhinoChassis(class USkeletalMesh* Mesh);
	UFUNCTION(BlueprintCallable, Category="MASK|Editor")
	static bool ConfigureRhinoRearChassis(class USkeletalMesh* Mesh);
	UFUNCTION(BlueprintCallable, Category="MASK|Editor")
	static bool ConfigureHurricaneChassis(class USkeletalMesh* Mesh);
	UFUNCTION(BlueprintCallable, Category="MASK|Editor")
	static bool ConfigureRavenChassis(class USkeletalMesh* Mesh);
	UFUNCTION(BlueprintCallable, Category="MASK|Editor")
	static bool ConfigureMantaChassis(class USkeletalMesh* Mesh);
	UFUNCTION(BlueprintCallable, Category="MASK|Editor")
	static bool ConfigureCondorChassis(class USkeletalMesh* Mesh);
	UFUNCTION(BlueprintCallable, Category="MASK|Editor")
	static bool ConfigureSwitchbladeChassis(class USkeletalMesh* Mesh);
};
