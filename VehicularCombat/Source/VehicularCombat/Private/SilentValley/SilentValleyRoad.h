#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SilentValleyRoad.generated.h"

/** Authored route and static colliding spline meshes; isolated to the new level. */
UCLASS()
class ASilentValleyRoad : public AActor
{
    GENERATED_BODY()
public:
    ASilentValleyRoad();
    UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<class USplineComponent> Spline;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) TArray<FVector> Waypoints;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) TObjectPtr<class UStaticMesh> RoadMesh;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) TObjectPtr<class UMaterialInterface> RoadMaterial;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float WidthCM=1000.f;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) float VisibleStartCM=4500.f;
    UPROPERTY(EditAnywhere,BlueprintReadWrite) bool bClosedRoute=false;
    UPROPERTY(VisibleAnywhere) TArray<TObjectPtr<class USplineMeshComponent>> Segments;
    UFUNCTION(BlueprintCallable,CallInEditor) void RebuildRoad();
    UFUNCTION(BlueprintPure) float RouteLengthCM() const;
    UFUNCTION(BlueprintPure) FVector RouteLocation(float DistanceCM) const;
    UFUNCTION(BlueprintPure) FRotator RouteRotation(float DistanceCM) const;
    float ClosestDistance(const FVector& Position) const;
};
