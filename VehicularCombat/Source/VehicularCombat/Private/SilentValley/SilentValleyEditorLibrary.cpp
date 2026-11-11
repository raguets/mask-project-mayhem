#include "SilentValley/SilentValleyEditorLibrary.h"
#include "SilentValley/SilentValleyRoad.h"
#if WITH_EDITOR
#include "Landscape.h"
#include "LandscapeInfo.h"
#include "LandscapeEdit.h"
#include "LandscapeComponent.h"
#include "Engine/Texture2D.h"
#include "Misc/Crc.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Engine/StaticMesh.h"
#include "StaticMeshAttributes.h"
#include "MeshDescription.h"
#include "PhysicsEngine/BodySetup.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "Misc/PackageName.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Components/HierarchicalInstancedStaticMeshComponent.h"
#include "Components/InstancedSkinnedMeshComponent.h"
#include "Engine/SkinnedAsset.h"
#include "Editor.h"

// UE 5.8 SetHeightData queues an editor-layer update and writes mip zero.
// A commandlet does not run the interactive layer-update tick. Rebuild the
// render mips explicitly, as Landscape import does, without changing mip zero.
static int32 RebuildSilentValleyHeightmapMips(ALandscape* Landscape)
{
    TMap<UTexture2D*,TArray<FColor*>> TextureMips;
    TMap<UTexture2D*,uint32> BaseCRCs;
    TMap<UTexture2D*,int32> GeometryMipCounts;
    for(ULandscapeComponent* Component:Landscape->LandscapeComponents)
    {
        UTexture2D* Texture=Component->GetHeightmap();
        if(!Texture || TextureMips.Contains(Texture)) { continue; }
        Texture->Modify();TArray<FColor*>& Mips=TextureMips.Add(Texture);
        for(int32 Mip=0;Mip<Texture->Source.GetNumMips();++Mip) { Mips.Add(reinterpret_cast<FColor*>(Texture->Source.LockMip(Mip))); }
        BaseCRCs.Add(Texture,FCrc::MemCrc32(Mips[0],Texture->Source.GetSizeX()*Texture->Source.GetSizeY()*sizeof(FColor)));
        GeometryMipCounts.Add(Texture,FMath::CeilLogTwo(Component->SubsectionSizeQuads+1));
    }
    for(ULandscapeComponent* Component:Landscape->LandscapeComponents)
    {
        UTexture2D* Texture=Component->GetHeightmap();auto* Mips=TextureMips.Find(Texture);if(!Mips) { continue; }
        // Landscape's mip generator is not DLL-exported. Resample each
        // subsection with shared endpoints, decoding height as 16 bits.
        const int32 Width=Texture->Source.GetSizeX(),Height=Texture->Source.GetSizeY(),Quads=Component->SubsectionSizeQuads;
        const int32 OffsetX=FMath::RoundToInt(Component->HeightmapScaleBias.Z*Width),OffsetY=FMath::RoundToInt(Component->HeightmapScaleBias.W*Height);
        for(int32 Mip=1;Mip<FMath::Min(Mips->Num(),GeometryMipCounts[Texture]);++Mip)
        {
            const int32 Vertices=(Quads+1)>>Mip,MipWidth=Width>>Mip;
            for(int32 SY=0;SY<Component->NumSubsections;++SY) for(int32 SX=0;SX<Component->NumSubsections;++SX)
            for(int32 Y=0;Y<Vertices;++Y) for(int32 X=0;X<Vertices;++X)
            {
                const float U=float(X)*Quads/(Vertices-1),V=float(Y)*Quads/(Vertices-1);const int32 X0=FMath::FloorToInt(U),Y0=FMath::FloorToInt(V);
                const float FX=U-X0,FY=V-Y0;const int32 BX=OffsetX+SX*(Quads+1),BY=OffsetY+SY*(Quads+1);
                const FColor C[]={(*Mips)[0][BX+X0+(BY+Y0)*Width],(*Mips)[0][BX+FMath::Min(X0+1,Quads)+(BY+Y0)*Width],(*Mips)[0][BX+X0+(BY+FMath::Min(Y0+1,Quads))*Width],(*Mips)[0][BX+FMath::Min(X0+1,Quads)+(BY+FMath::Min(Y0+1,Quads))*Width]};
                const auto Interpolate=[FX,FY](float A,float B,float C,float D) { return FMath::RoundToInt(FMath::Lerp(FMath::Lerp(A,B,FX),FMath::Lerp(C,D,FX),FY)); };
                const int32 H=Interpolate((C[0].R<<8)|C[0].G,(C[1].R<<8)|C[1].G,(C[2].R<<8)|C[2].G,(C[3].R<<8)|C[3].G);
                FColor& Target=(*Mips)[Mip][(OffsetX>>Mip)+SX*Vertices+X+((OffsetY>>Mip)+SY*Vertices+Y)*MipWidth];
                Target.R=H>>8;Target.G=H&255;Target.B=Interpolate(C[0].B,C[1].B,C[2].B,C[3].B);Target.A=Interpolate(C[0].A,C[1].A,C[2].A,C[3].A);
            }
        }
    }
    for(auto& Entry:TextureMips)
    {
        UTexture2D* Texture=Entry.Key;TArray<FColor*>& Mips=Entry.Value;
        checkf(BaseCRCs[Texture]==FCrc::MemCrc32(Mips[0],Texture->Source.GetSizeX()*Texture->Source.GetSizeY()*sizeof(FColor)),TEXT("Render-mip repair must preserve full-resolution terrain"));
        for(int32 Mip=GeometryMipCounts[Texture];Mip<Mips.Num();++Mip)
        {
            const int32 Width=FMath::Max(1,Texture->Source.GetSizeX()>>Mip),Height=FMath::Max(1,Texture->Source.GetSizeY()>>Mip),PrevWidth=Texture->Source.GetSizeX()>>(Mip-1);
            for(int32 Y=0;Y<Height;++Y) for(int32 X=0;X<Width;++X)
            {
                FColor& Target=Mips[Mip][X+Y*Width];const FColor* Previous=Mips[Mip-1];
                for(int32 Channel=0;Channel<4;++Channel)
                {
                    const auto Byte=[Previous,Channel](int32 Index) { return reinterpret_cast<const uint8*>(Previous+Index)[Channel]; };
                    reinterpret_cast<uint8*>(&Target)[Channel]=(int32(Byte(2*X+2*Y*PrevWidth))+Byte(2*X+1+2*Y*PrevWidth)+Byte(2*X+(2*Y+1)*PrevWidth)+Byte(2*X+1+(2*Y+1)*PrevWidth))>>2;
                }
            }
        }
        for(int32 Mip=0;Mip<Mips.Num();++Mip) { Texture->Source.UnlockMip(Mip); }
        Texture->Source.ForceGenerateGuid();Texture->PostEditChange();Texture->MarkPackageDirty();
    }
    for(ULandscapeComponent* Component:Landscape->LandscapeComponents)
    { Component->Modify();Component->UpdateCachedBounds();Component->UpdateBounds();Component->MarkRenderStateDirty();Component->MarkPackageDirty(); }
    Landscape->Tags.AddUnique(TEXT("SV_RENDER_MIPS_V1"));Landscape->MarkPackageDirty();
    UE_LOG(LogTemp,Display,TEXT("SV_RENDER_MIPS_REBUILT textures=%d components=%d base_mip_crc_unchanged=1"),TextureMips.Num(),Landscape->LandscapeComponents.Num());
    return TextureMips.Num();
}
#endif

UStaticMesh* USilentValleyEditorLibrary::CreateDistantTerrain(const FString& AssetPath)
{
#if WITH_EDITOR
    UWorld* World=GEditor?GEditor->GetEditorWorldContext().World():nullptr;
    if(!World || !World->GetOutermost()->GetName().Contains(TEXT("SilentValley")) || !AssetPath.StartsWith(TEXT("/Game/MASK/Environment/SilentValley/Terrain/")) || FindObject<UObject>(nullptr,*(AssetPath+TEXT(".")+FPackageName::GetLongPackageAssetName(AssetPath)))) { return nullptr; }
    ALandscape* Land=nullptr;for(TActorIterator<ALandscape> It(World);It;++It) { if(It->ActorHasTag(TEXT("SV_RENDER_MIPS_V1"))) { Land=*It;break; } }
    if(!Land || !Land->GetActorLocation().Equals(FVector(-201600,-201600,0),.1) || !Land->GetActorScale3D().Equals(FVector(200,200,400),.01)) { return nullptr; }
    constexpr int32 Side=2017,PerSide=2016,Count=PerSide*4;
    TArray<uint16> Heights;Heights.SetNumUninitialized(Side*Side);
    { FLandscapeEditDataInterface Edit(Land->GetLandscapeInfo());Edit.GetHeightDataFast(0,0,Side-1,Side-1,Heights.GetData(),0); }
    FFileHelper::SaveArrayToFile(TArrayView<const uint8>(reinterpret_cast<const uint8*>(Heights.GetData()),Heights.Num()*sizeof(uint16)),*(FPaths::ProjectSavedDir()/TEXT("SilentValley/environment-v1/source-heightfield.r16")));
    UE_LOG(LogTemp,Display,TEXT("SV_VISTA_SOURCE nanite=%d side=%d"),Land->IsNaniteEnabled(),Side);
    const auto Sample=[&Heights](FVector2D P)
    {
        const float X=FMath::Clamp(float((P.X+201600)/200),0.f,2016.f),Y=FMath::Clamp(float((P.Y+201600)/200),0.f,2016.f);
        const int32 X0=FMath::FloorToInt(X),Y0=FMath::FloorToInt(Y),X1=FMath::Min(X0+1,2016),Y1=FMath::Min(Y0+1,2016);
        return (FMath::Lerp(FMath::Lerp(float(Heights[X0+Y0*Side]),float(Heights[X1+Y0*Side]),X-X0),FMath::Lerp(float(Heights[X0+Y1*Side]),float(Heights[X1+Y1*Side]),X-X0),Y-Y0)-32768)*400/128;
    };
    const auto Height=[&Sample](FVector2D P)
    {
        const double Extent=FMath::Max(FMath::Abs(P.X),FMath::Abs(P.Y));
        if(Extent<=201600) { return Sample(P)-5.f; }
        const float Edge=Sample(P*(201600/Extent));
        const auto Peak=[P](double X,double Y,double R,float H) { return H*FMath::Exp(-FVector2D(P.X-X,P.Y-Y).SizeSquared()/(R*R)); };
        float Far=9000+15000*(.5f+.5f*FMath::PerlinNoise2D(P/110000))+6000*FMath::PerlinNoise2D(P/34000);
        Far+=Peak(-400000,-220000,160000,42000)+Peak(390000,120000,150000,51000)+Peak(-100000,440000,170000,46000)+Peak(150000,-430000,160000,39000);
        return FMath::Lerp(Edge-5.f,Far,FMath::SmoothStep(0.f,110000.f,float(Extent-201600)));
    };
    const float Extents[]={200600,201600,220000,260000,320000,420000,560000,760000,800000};
    FMeshDescription Desc;FStaticMeshAttributes Attr(Desc);Attr.Register();Attr.GetVertexInstanceUVs().SetNumChannels(1);
    const auto Group=Desc.CreatePolygonGroup();Attr.GetPolygonGroupMaterialSlotNames()[Group]=TEXT("DistantTerrain");
    TArray<FVertexID> Vertices;TArray<FVector3f> Normals;
    for(float E:Extents) for(int32 I=0;I<Count;++I)
    {
        const double T=double(I%PerSide)/PerSide;FVector2D P;
        switch(I/PerSide) { case 0:P=FVector2D(-E,-E+2*E*T);break;case 1:P=FVector2D(-E+2*E*T,E);break;case 2:P=FVector2D(E,E-2*E*T);break;default:P=FVector2D(E-2*E*T,-E); }
        const FVertexID V=Desc.CreateVertex();Vertices.Add(V);Attr.GetVertexPositions()[V]=FVector3f(P.X,P.Y,Height(P));
        Normals.Add(FVector3f(-(Height(P+FVector2D(200,0))-Height(P-FVector2D(200,0)))/400,-(Height(P+FVector2D(0,200))-Height(P-FVector2D(0,200)))/400,1).GetSafeNormal());
    }
    const auto Triangle=[&](int32 A,int32 B,int32 C)
    {
        TArray<FVertexInstanceID> Corners;
        for(int32 Index:{A,B,C})
        {
            const auto V=Desc.CreateVertexInstance(Vertices[Index]);const FVector3f N=Normals[Index],P=Attr.GetVertexPositions()[Vertices[Index]];
            Attr.GetVertexInstanceNormals()[V]=N;Attr.GetVertexInstanceTangents()[V]=(FVector3f(1,0,0)-N*N.X).GetSafeNormal();Attr.GetVertexInstanceBinormalSigns()[V]=1;
            Attr.GetVertexInstanceUVs().Set(V,0,FVector2f(P.X/100,P.Y/100));Corners.Add(V);
        }
        Desc.CreatePolygon(Group,Corners);
    };
    for(int32 Ring=0;Ring<UE_ARRAY_COUNT(Extents)-1;++Ring) for(int32 I=0;I<Count;++I)
    // Unreal front faces use clockwise winding when viewed from above.
    { const int32 Next=(I+1)%Count,A=Ring*Count+I,B=Ring*Count+Next,C=(Ring+1)*Count+Next,D=(Ring+1)*Count+I;Triangle(A,C,B);Triangle(A,D,C); }
    auto* Package=CreatePackage(*AssetPath);auto* Mesh=NewObject<UStaticMesh>(Package,*FPackageName::GetLongPackageAssetName(AssetPath),RF_Public|RF_Standalone|RF_Transactional);
    Mesh->SetNumSourceModels(1);Mesh->GetSourceModel(0).BuildSettings.bRecomputeNormals=false;Mesh->GetSourceModel(0).BuildSettings.bRecomputeTangents=false;
    Mesh->GetSourceModel(0).BuildSettings.bGenerateLightmapUVs=false;Mesh->GetSourceModel(0).BuildSettings.DistanceFieldResolutionScale=0;
    Mesh->CreateMeshDescription(0,MoveTemp(Desc));Mesh->CommitMeshDescription(0);Mesh->GetStaticMaterials().Add(FStaticMaterial());Mesh->Build(false);Mesh->MarkPackageDirty();FAssetRegistryModule::AssetCreated(Mesh);
    return Mesh;
#else
    return nullptr;
#endif
}

UStaticMesh* USilentValleyEditorLibrary::CreateRoadRibbon(const FString& AssetPath)
{
#if WITH_EDITOR
    if(!AssetPath.StartsWith(TEXT("/Game/MASK/Environment/SilentValley/")) || FindObject<UObject>(nullptr,*(AssetPath+TEXT(".")+FPackageName::GetLongPackageAssetName(AssetPath)))) { return nullptr; }
    auto* Package=CreatePackage(*AssetPath);auto* Mesh=NewObject<UStaticMesh>(Package,*FPackageName::GetLongPackageAssetName(AssetPath),RF_Public|RF_Standalone|RF_Transactional);
    FMeshDescription Description;FStaticMeshAttributes Attributes(Description);Attributes.Register();Attributes.GetVertexInstanceUVs().SetNumChannels(1);
    const auto Group=Description.CreatePolygonGroup();Attributes.GetPolygonGroupMaterialSlotNames()[Group]=TEXT("Road");
    for(int32 I=0;I<16;++I)
    {
        TArray<FVertexInstanceID> Corners;
        for(const FVector3f P:{FVector3f(-50+100.f*I/16,-50,0),FVector3f(-50+100.f*(I+1)/16,-50,0),FVector3f(-50+100.f*(I+1)/16,50,0),FVector3f(-50+100.f*I/16,50,0)})
        {
            const auto Vertex=Description.CreateVertex();Attributes.GetVertexPositions()[Vertex]=P;const auto Instance=Description.CreateVertexInstance(Vertex);
            Attributes.GetVertexInstanceNormals()[Instance]=FVector3f(0,0,1);Attributes.GetVertexInstanceTangents()[Instance]=FVector3f(1,0,0);Attributes.GetVertexInstanceBinormalSigns()[Instance]=1;
            Attributes.GetVertexInstanceUVs().Set(Instance,0,FVector2f((P.X+50)/100,(P.Y+50)/100));Corners.Add(Instance);
        }
        Description.CreatePolygon(Group,Corners);
    }
    Mesh->SetNumSourceModels(1);Mesh->CreateMeshDescription(0,MoveTemp(Description));Mesh->CommitMeshDescription(0);
    Mesh->GetStaticMaterials().Add(FStaticMaterial());Mesh->CreateBodySetup();Mesh->GetBodySetup()->CollisionTraceFlag=CTF_UseComplexAsSimple;Mesh->GetBodySetup()->bDoubleSidedGeometry=true;
    Mesh->Build(false);Mesh->MarkPackageDirty();FAssetRegistryModule::AssetCreated(Mesh);return Mesh;
#else
    return nullptr;
#endif
}

int32 USilentValleyEditorLibrary::RefineNaturalLandscape(ASilentValleyRoad* Road,FVector LakeCenter,FVector2D LakeRadii,float WaterHeight)
{
#if WITH_EDITOR
    if(!Road || !Road->GetWorld() || !Road->GetWorld()->GetOutermost()->GetName().Contains(TEXT("SilentValley")) || LakeRadii.X<1000 || LakeRadii.Y<1000) { return -1; }
    ALandscape* Landscape=nullptr;
    for(TActorIterator<ALandscape> It(Road->GetWorld());It;++It) { if(It->ActorHasTag(TEXT("SV_GENERATED"))) { Landscape=*It;break; } }
    if(!Landscape || !Landscape->GetActorScale3D().Equals(FVector(200,200,400),.01f) || !Landscape->GetActorLocation().Equals(FVector(-201600,-201600,0),.1f)) { return -1; }
    if(Landscape->ActorHasTag(TEXT("SV_NATURAL_TERRAIN_V1")))
    { if(!Landscape->ActorHasTag(TEXT("SV_RENDER_MIPS_V1"))) { RebuildSilentValleyHeightmapMips(Landscape); }return 0; }
    constexpr int32 Side=2017;TArray<uint16> Data;Data.SetNumZeroed(Side*Side);
    { FLandscapeEditDataInterface Edit(Landscape->GetLandscapeInfo());Edit.GetHeightDataFast(0,0,Side-1,Side-1,Data.GetData(),0); }
    TMap<FIntPoint,TArray<FVector>> Buckets;
    for(float D=0;D<Road->RouteLengthCM();D+=400.f)
    { const FVector P=Road->RouteLocation(D);Buckets.FindOrAdd(FIntPoint(FMath::FloorToInt(P.X/10000),FMath::FloorToInt(P.Y/10000))).Add(P); }
    const FVector2D POIs[]={FVector2D(-135000,-110000),FVector2D(-75000,-78000),FVector2D(70000,25000),FVector2D(65000,95000),FVector2D(-55000,125000)};
    int32 Changed=0,Protected=0;
    for(int32 Y=0;Y<Side;++Y) for(int32 X=0;X<Side;++X)
    {
        const float WX=-201600+X*200.f,WY=-201600+Y*200.f;const FVector2D P(WX,WY);
        float Distance=BIG_NUMBER;const FIntPoint Cell(FMath::FloorToInt(WX/10000),FMath::FloorToInt(WY/10000));
        for(int32 CY=-1;CY<=1;++CY) for(int32 CX=-1;CX<=1;++CX)
        { if(const auto* Points=Buckets.Find(Cell+FIntPoint(CX,CY))) { for(const FVector& Q:*Points) { Distance=FMath::Min(Distance,static_cast<float>(FVector2D::Distance(P,FVector2D(Q.X,Q.Y)))); } } }
        // Sampling at 4 m plus this 5 m margin keeps the entire established
        // 80 m road corridor byte-for-byte intact, including collision heights.
        float Weight=FMath::SmoothStep(8500.f,18000.f,Distance);
        for(const FVector2D& POI:POIs) { Weight=FMath::Min(Weight,FMath::SmoothStep(18000.f,24000.f,static_cast<float>(FVector2D::Distance(P,POI)))); }
        if(Weight<=0) { ++Protected;continue; }
        const int32 I=Y*Side+X;const float Old=(static_cast<int32>(Data[I])-32768)*400.f/128.f;
        const float Edge=FMath::Clamp((FMath::Max(FMath::Abs(WX),FMath::Abs(WY))-150000)/50000.f,0.f,1.f);
        float Height=Old-Edge*Edge*34000.f;
        Height+=3500.f*FMath::PerlinNoise2D(P/24000.f)+1200.f*FMath::PerlinNoise2D((P+FVector2D(7412,9183))/6500.f)+280.f*FMath::PerlinNoise2D(P/1700.f);
        // Independent rounded ridges replace the square enclosing wall.
        Height+=Edge*10000.f*(.65f+.35f*FMath::PerlinNoise2D(P/18000.f));
        const float R=FVector2D((WX-LakeCenter.X)/LakeRadii.X,(WY-LakeCenter.Y)/LakeRadii.Y).Size();
        if(R<1.8f)
        {
            const float Bed=WaterHeight-650.f+100.f*R*R;
            const float Rim=FMath::Max(Height,WaterHeight+250.f);
            Height=R<1.3f?FMath::Lerp(Bed,Rim,FMath::SmoothStep(.72f,1.3f,R)):FMath::Lerp(Rim,Height,FMath::SmoothStep(1.3f,1.8f,R));
        }
        const uint16 New=static_cast<uint16>(FMath::Clamp(FMath::RoundToInt(32768+FMath::Lerp(Old,Height,Weight)*128.f/400.f),1,65534));
        if(New!=Data[I]) { Data[I]=New;++Changed; }
    }
    Landscape->Modify();
    { FLandscapeEditDataInterface Edit(Landscape->GetLandscapeInfo());Edit.SetHeightData(0,0,Side-1,Side-1,Data.GetData(),0,true);Edit.Flush(); }
    RebuildSilentValleyHeightmapMips(Landscape);Landscape->RecreateCollisionComponents();
    Landscape->Tags.Add(TEXT("SV_NATURAL_TERRAIN_V1"));Landscape->MarkPackageDirty();
    UE_LOG(LogTemp,Display,TEXT("SV_NATURAL_TERRAIN changed=%d protected=%d lake=%s radii=%s water_z=%.1f"),Changed,Protected,*LakeCenter.ToString(),*LakeRadii.ToString(),WaterHeight);
    return Changed;
#else
    return -1;
#endif
}

AActor* USilentValleyEditorLibrary::PlaceSceneryInstances(const FString& Label,UObject* Mesh,const TArray<FTransform>& Transforms)
{
#if WITH_EDITOR
    UWorld* World=GEditor?GEditor->GetEditorWorldContext().World():nullptr;
    if(!World || !World->GetOutermost()->GetName().Contains(TEXT("SilentValley")) || !Label.StartsWith(TEXT("SV_Natural_")) || !Mesh) { return nullptr; }
    AActor* Actor=nullptr;
    for(TActorIterator<AActor> It(World);It;++It) { if(It->GetActorLabel()==Label) { Actor=*It;break; } }
    if(Actor && !Actor->ActorHasTag(TEXT("SV_ENVIRONMENT_V1"))) { return nullptr; }
    if(!Actor) { Actor=World->SpawnActor<AActor>();Actor->SetActorLabel(Label);Actor->Tags={TEXT("SV_GENERATED"),TEXT("SV_ENVIRONMENT_V1")}; }
    Actor->Modify();
    if(auto* Static=Cast<UStaticMesh>(Mesh))
    {
        auto* Component=Actor->FindComponentByClass<UHierarchicalInstancedStaticMeshComponent>();
        if(!Component) { Component=NewObject<UHierarchicalInstancedStaticMeshComponent>(Actor,TEXT("SceneryInstances"));Actor->SetRootComponent(Component);Actor->AddInstanceComponent(Component);Component->RegisterComponent(); }
        Component->SetStaticMesh(Static);Component->SetCollisionEnabled(ECollisionEnabled::NoCollision);Component->SetCanEverAffectNavigation(false);
        Component->ClearInstances();Component->AddInstances(Transforms,false,true);Component->SetCullDistances(5000,9000);
    }
    else if(auto* Skinned=Cast<USkinnedAsset>(Mesh))
    {
        auto* Component=Actor->FindComponentByClass<UInstancedSkinnedMeshComponent>();
        if(!Component) { Component=NewObject<UInstancedSkinnedMeshComponent>(Actor,TEXT("TreeInstances"));Actor->SetRootComponent(Component);Actor->AddInstanceComponent(Component); }
        Component->SetCollisionEnabled(ECollisionEnabled::NoCollision);Component->SetCanEverAffectNavigation(false);
        UE_LOG(LogTemp,Display,TEXT("SV_SCENERY set_asset %s"),*Label);
        Component->SetSkinnedAssetAndUpdate(Skinned);
        UE_LOG(LogTemp,Display,TEXT("SV_SCENERY register %s"),*Label);
        if(!Component->IsRegistered()) { Component->RegisterComponent(); }
        Component->ClearInstances();TArray<int32> Animations;Animations.Init(0,Transforms.Num());Component->AddInstances(Transforms,Animations,false,true);
        UE_LOG(LogTemp,Display,TEXT("SV_SCENERY placed %s count=%d"),*Label,Transforms.Num());
    }
    else { return nullptr; }
    Actor->MarkPackageDirty();return Actor;
#else
    return nullptr;
#endif
}

AActor* USilentValleyEditorLibrary::CreateBlockoutLandscape(ASilentValleyRoad* Road,UMaterialInterface* Material)
{
#if WITH_EDITOR
    if(!Road || !Material || !Road->GetWorld()->GetOutermost()->GetName().Contains(TEXT("SilentValley"))) { return nullptr; }
    UWorld* World=Road->GetWorld();ALandscape* Existing=nullptr;
    for(TActorIterator<ALandscape> It(World);It;++It) { if(!It->ActorHasTag(TEXT("SV_GENERATED"))) { return nullptr; }Existing=*It;break; }
    constexpr int32 Side=2017;constexpr float Half=201600.f,Spacing=200.f;
    TArray<FVector> Samples;TMap<FIntPoint,TArray<int32>> Buckets;
    for(float D=0;D<Road->RouteLengthCM();D+=500.f)
    {
        const FVector P=Road->RouteLocation(D);const int32 Index=Samples.Add(P);Buckets.FindOrAdd(FIntPoint(FMath::FloorToInt(P.X/10000),FMath::FloorToInt(P.Y/10000))).Add(Index);
    }
    TArray<uint16> Data;Data.SetNumUninitialized(Side*Side);
    for(int32 Y=0;Y<Side;++Y) for(int32 X=0;X<Side;++X)
    {
        const float WX=-Half+X*Spacing,WY=-Half+Y*Spacing;
        const auto Gaussian=[WX,WY](float CX,float CY,float Radius,float Height) { return Height*FMath::Exp(-FVector2D(WX-CX,WY-CY).SizeSquared()/(Radius*Radius)); };
        const float Edge=FMath::Clamp((FMath::Max(FMath::Abs(WX),FMath::Abs(WY))-150000)/50000.f,0.f,1.f);
        float Height=6500+1800*FMath::Sin(WX/65000.f)+1400*FMath::Cos(WY/80000.f)+Edge*Edge*34000;
        Height+=Gaussian(-177000,-100000,33000,25000)+Gaussian(163000,15000,42000,32000)+Gaussian(20000,170000,30000,20000);
        const float BaseDistance=FVector2D(WX+135000,WY+110000).Size();
        if(BaseDistance<14000) { Height=FMath::Lerp(8000.f-2,Height,FMath::SmoothStep(8000.f,14000.f,BaseDistance)); }
        const float QuarryDistance=FVector2D(WX-65000,WY-95000).Size();
        if(QuarryDistance<15000) { Height=FMath::Lerp(10000.f-2,Height,FMath::SmoothStep(7000.f,15000.f,QuarryDistance)); }
        float Nearest=BIG_NUMBER,RoadZ=0;const FIntPoint Cell(FMath::FloorToInt(WX/10000),FMath::FloorToInt(WY/10000));
        for(int32 CY=-1;CY<=1;++CY) for(int32 CX=-1;CX<=1;++CX)
        {
            if(const auto* Indices=Buckets.Find(Cell+FIntPoint(CX,CY))) for(int32 Index:*Indices)
            {
                const FVector A=Samples[Index],B=Samples[FMath::Min(Index+1,Samples.Num()-1)];const FVector2D AB(B.X-A.X,B.Y-A.Y);
                const float Alpha=FMath::Clamp(FVector2D::DotProduct(FVector2D(WX-A.X,WY-A.Y),AB)/FMath::Max(1.f,static_cast<float>(AB.SizeSquared())),0.f,1.f);
                const FVector P=FMath::Lerp(A,B,Alpha);const float Dist=FVector2D(WX-P.X,WY-P.Y).SizeSquared();
                if(Dist<Nearest) { Nearest=Dist;RoadZ=P.Z; }
            }
        }
        const float Distance=FMath::Sqrt(Nearest);
        if(Distance<8000) { Height=FMath::Lerp(RoadZ-45,Height,FMath::SmoothStep(550.f,8000.f,Distance)); }
        Data[Y*Side+X]=static_cast<uint16>(FMath::Clamp(FMath::RoundToInt(32768+Height*128/400),0,65535));
    }
    if(Existing)
    {
        Existing->Modify();
        { FLandscapeEditDataInterface Edit(Existing->GetLandscapeInfo());Edit.SetHeightData(0,0,Side-1,Side-1,Data.GetData(),0,true);Edit.Flush(); }
        Existing->Tags.Remove(TEXT("SV_NATURAL_TERRAIN_V1"));RebuildSilentValleyHeightmapMips(Existing);
        Existing->RecreateCollisionComponents();Existing->MarkPackageDirty();return Existing;
    }
    auto* Landscape=World->SpawnActor<ALandscape>(FVector(-Half,-Half,0),FRotator::ZeroRotator);Landscape->SetActorLabel(TEXT("SV_Landscape_4032m"));
    Landscape->LandscapeMaterial=Material;Landscape->SetActorScale3D(FVector(200,200,400));Landscape->StaticLightingLOD=1;
    TMap<FGuid,TArray<uint16>> Heights;Heights.Add(FGuid(),MoveTemp(Data));TMap<FGuid,TArray<FLandscapeImportLayerInfo>> Layers;Layers.Add(FGuid(),{});
    Landscape->Import(FGuid::NewGuid(),0,0,Side-1,Side-1,2,63,Heights,TEXT(""),Layers,ELandscapeImportAlphamapType::Additive,TArrayView<const FLandscapeLayer>());
    Landscape->RegisterAllComponents();Landscape->MarkPackageDirty();return Landscape;
#else
    return nullptr;
#endif
}
