#pragma once
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "SilentValleyEditorLibrary.generated.h"

/** Only generates original assets in the SilentValley namespace and an empty new level. */
UCLASS()
class USilentValleyEditorLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable) static class UStaticMesh* CreateRoadRibbon(const FString& AssetPath);
    UFUNCTION(BlueprintCallable) static AActor* CreateBlockoutLandscape(class ASilentValleyRoad* Road,class UMaterialInterface* Material);
    /** Refine only generated terrain outside an 80 m road corridor and POIs.
     * Lake placement is an explicitly authorised interpretation, units cm.
     * Returns changed samples; -1 rejects an incompatible map/landscape. */
    UFUNCTION(BlueprintCallable) static int32 RefineNaturalLandscape(class ASilentValleyRoad* Road,FVector LakeCenter,FVector2D LakeRadii,float WaterHeight);
    /** Persistent native instances of imported scenery; no collision or source mutation. */
    UFUNCTION(BlueprintCallable) static AActor* PlaceSceneryInstances(const FString& Label,UObject* Mesh,const TArray<FTransform>& Transforms);
    /** Original, non-playable terrain ring joined to the saved landscape edge. */
    UFUNCTION(BlueprintCallable) static class UStaticMesh* CreateDistantTerrain(const FString& AssetPath);
};
