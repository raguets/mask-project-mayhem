#include "SilentValley/SilentValleyRoad.h"
#include "Components/SplineComponent.h"
#include "Components/SplineMeshComponent.h"
#include "Engine/StaticMesh.h"

ASilentValleyRoad::ASilentValleyRoad()
{
    Spline=CreateDefaultSubobject<USplineComponent>(TEXT("Route"));SetRootComponent(Spline);
    Spline->SetMobility(EComponentMobility::Static);PrimaryActorTick.bCanEverTick=false;
}
void ASilentValleyRoad::RebuildRoad()
{
    Modify();for(USplineMeshComponent* Segment:Segments) { if(IsValid(Segment)) { RemoveInstanceComponent(Segment);Segment->DestroyComponent(); } }Segments.Empty();
    Spline->ClearSplinePoints(false);
    for(const auto& Point:Waypoints) { Spline->AddSplinePoint(Point,ESplineCoordinateSpace::Local,false); }
    for(int32 I=0;I<Waypoints.Num();++I) { Spline->SetSplinePointType(I,ESplinePointType::Curve,false); }
    Spline->SetClosedLoop(bClosedRoute,false);Spline->UpdateSpline();
    // Preserve smooth plan-view curves while bounding the vertical profile.
    // Auto tangents can overshoot near a short, level turnout after a long hill.
    for(int32 I=0;I<Waypoints.Num();++I)
    {
        FVector Tangent=Spline->GetTangentAtSplinePoint(I,ESplineCoordinateSpace::Local);Tangent.Z=0;
        Spline->SetTangentAtSplinePoint(I,Tangent,ESplineCoordinateSpace::Local,false);
    }
    Spline->UpdateSpline();
    if(!RoadMesh || Waypoints.Num()<2) { return; }
    const float Length=Spline->GetSplineLength();const int32 Count=FMath::CeilToInt((Length-VisibleStartCM)/2000.f);
    for(int32 I=0;I<Count;++I)
    {
        const float A=VisibleStartCM+(Length-VisibleStartCM)*I/Count,B=VisibleStartCM+(Length-VisibleStartCM)*(I+1)/Count;
        auto* Segment=NewObject<USplineMeshComponent>(this,NAME_None,RF_Transactional);AddInstanceComponent(Segment);Segment->SetupAttachment(Spline);
        Segment->SetMobility(EComponentMobility::Static);Segment->SetStaticMesh(RoadMesh);Segment->SetForwardAxis(ESplineMeshAxis::X,false);
        Segment->SetStartAndEnd(Spline->GetLocationAtDistanceAlongSpline(A,ESplineCoordinateSpace::Local),Spline->GetDirectionAtDistanceAlongSpline(A,ESplineCoordinateSpace::Local)*(B-A),
            Spline->GetLocationAtDistanceAlongSpline(B,ESplineCoordinateSpace::Local),Spline->GetDirectionAtDistanceAlongSpline(B,ESplineCoordinateSpace::Local)*(B-A),false);
        Segment->SetStartScale(FVector2D(WidthCM/100.f,1.f),false);Segment->SetEndScale(FVector2D(WidthCM/100.f,1.f),false);
        if(RoadMaterial) { Segment->SetMaterial(0,RoadMaterial); }
        Segment->SetCollisionProfileName(TEXT("BlockAll"));Segment->bCastDynamicShadow=false;Segment->RegisterComponent();Segment->UpdateMesh();Segments.Add(Segment);
    }
    MarkPackageDirty();
}
float ASilentValleyRoad::RouteLengthCM() const { return Spline->GetSplineLength(); }
FVector ASilentValleyRoad::RouteLocation(float DistanceCM) const { return Spline->GetLocationAtDistanceAlongSpline(DistanceCM,ESplineCoordinateSpace::World); }
FRotator ASilentValleyRoad::RouteRotation(float DistanceCM) const { return Spline->GetRotationAtDistanceAlongSpline(DistanceCM,ESplineCoordinateSpace::World); }
float ASilentValleyRoad::ClosestDistance(const FVector& Position) const { return Spline->GetDistanceAlongSplineAtLocation(Position,ESplineCoordinateSpace::World); }
