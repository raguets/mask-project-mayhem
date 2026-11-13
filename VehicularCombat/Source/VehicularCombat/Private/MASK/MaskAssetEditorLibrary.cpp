#include "MASK/MaskAssetEditorLibrary.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/SkeletalMeshSocket.h"
#include "PhysicsEngine/PhysicsAsset.h"
#include "PhysicsEngine/SkeletalBodySetup.h"
#include "Animation/BlendSpace.h"
#include "Animation/AnimSequence.h"
#include "UObject/Package.h"
#include "UObject/UnrealType.h"
#include "Misc/PackageName.h"
#if WITH_EDITOR
#include "AssetRegistry/AssetRegistryModule.h"
#endif

UBlendSpace* UMaskAssetEditorLibrary::CreateDriverLocomotion(const FString& AssetPath,USkeleton* Skeleton,const TArray<UAnimSequence*>& Animations,const TArray<FVector>& Positions)
{
#if WITH_EDITOR
	if(!AssetPath.StartsWith(TEXT("/Game/MASK/OnFoot/")) || !Skeleton || Animations.Num()!=Positions.Num() || Animations.Num()<3) { return nullptr; }
	for(auto* Animation:Animations) { if(!Animation || Animation->GetSkeleton()!=Skeleton) { return nullptr; } }
	auto* Package=CreatePackage(*AssetPath);const FString Name=FPackageName::GetLongPackageAssetName(AssetPath);
	auto* Space=FindObject<UBlendSpace>(Package,*Name);
	if(!Space) { Space=NewObject<UBlendSpace>(Package,*Name,RF_Public|RF_Standalone|RF_Transactional);FAssetRegistryModule::AssetCreated(Space); }
	Space->Modify();Space->SetSkeleton(Skeleton);
	const auto* Parameters=FindFProperty<FStructProperty>(UBlendSpace::StaticClass(),TEXT("BlendParameters"));if(!Parameters || Parameters->ArrayDim<2) { return nullptr; }
	for(int32 Axis=0;Axis<2;++Axis)
	{
		auto* Parameter=Parameters->ContainerPtrToValuePtr<FBlendParameter>(Space,Axis);
		Parameter->DisplayName=Axis==0?TEXT("Forward cm/s"):TEXT("Right cm/s");Parameter->Min=-400;Parameter->Max=400;Parameter->GridNum=8;Parameter->bSnapToGrid=false;
	}
	for(int32 I=Space->GetNumberOfBlendSamples()-1;I>=0;--I) { Space->DeleteSample(I); }
	for(int32 I=0;I<Animations.Num();++I) { if(Space->AddSample(Animations[I],Positions[I])==INDEX_NONE) { return nullptr; } }
	Space->ValidateSampleData();Space->ResampleData();Space->PostEditChange();Space->MarkPackageDirty();return Space;
#else
	return nullptr;
#endif
}

static bool ConfigureMaskChassis(USkeletalMesh* Mesh,const TCHAR* Prefix,FVector Center,FVector Size,FVector WeaponLocation)
{
#if WITH_EDITOR
	if (!Mesh || !Mesh->GetPathName().StartsWith(Prefix) || !Mesh->GetPhysicsAsset()) { return false; }
	auto* Physics=Mesh->GetPhysicsAsset();
	Physics->Modify();Mesh->Modify();
	// Only this newly imported physics proxy is edited. No original vehicle asset is touched.
	Physics->SkeletalBodySetups.Reset();Physics->ConstraintSetup.Reset();
	auto* Body=NewObject<USkeletalBodySetup>(Physics,NAME_None,RF_Transactional);
	// FBX retains the armature node above the Blender bone named "root".
	// The simulated body must drive reference bone 0, or the component stays
	// fixed while only a child body moves inside it.
	Body->BoneName=Mesh->GetRefSkeleton().GetBoneName(0);Body->PhysicsType=EPhysicsType::PhysType_Simulated;
	Body->CollisionTraceFlag=CTF_UseSimpleAsComplex;
	const FTransform RootPose=Mesh->GetRefSkeleton().GetRefBonePose()[0];
	const FVector BoneScale=RootPose.GetScale3D().GetAbs();
	FKBoxElem Box;Box.Center=RootPose.InverseTransformPosition(Center);
	Box.Rotation=RootPose.GetRotation().Inverse().Rotator();
	Box.X=Size.X/FMath::Max(BoneScale.X,UE_SMALL_NUMBER);Box.Y=Size.Y/FMath::Max(BoneScale.Y,UE_SMALL_NUMBER);Box.Z=Size.Z/FMath::Max(BoneScale.Z,UE_SMALL_NUMBER);
	UE_LOG(LogTemp,Display,TEXT("MASK_PHYS_ASSET root=%s reference_scale=%s box=%.3f,%.3f,%.3f"),*Body->BoneName.ToString(),*BoneScale.ToString(),Box.X,Box.Y,Box.Z);
	Body->AggGeom.BoxElems.Add(Box);Body->InvalidatePhysicsData();Body->CreatePhysicsMeshes();
	Physics->SkeletalBodySetups.Add(Body);Physics->UpdateBodySetupIndexMap();Physics->UpdateBoundsBodiesArray();
	for (const FName Name : {FName(TEXT("PrimaryWeaponSocket")),FName(TEXT("SecondaryWeaponSocket"))})
	{
		auto* Socket=const_cast<USkeletalMeshSocket*>(Mesh->FindSocket(Name));
		if (!Socket) { Socket=NewObject<USkeletalMeshSocket>(Mesh);Mesh->GetMeshOnlySocketList().Add(Socket); }
		Socket->SocketName=Name;Socket->BoneName=Body->BoneName;
		Socket->RelativeLocation=RootPose.InverseTransformPosition(WeaponLocation);
		Socket->RelativeRotation=RootPose.GetRotation().Inverse().Rotator();
	}
	Physics->MarkPackageDirty();Mesh->MarkPackageDirty();return true;
#else
	return false;
#endif
}

bool UMaskAssetEditorLibrary::ConfigureThunderhawkChassis(USkeletalMesh* Mesh)
{
	return ConfigureMaskChassis(Mesh,TEXT("/Game/MASK/Thunderhawk/"),FVector(0,0,61),FVector(435,172,58),FVector(-20,0,135));
}
bool UMaskAssetEditorLibrary::ConfigureRhinoChassis(USkeletalMesh* Mesh)
{
	return ConfigureMaskChassis(Mesh,TEXT("/Game/MASK/Rhino/"),FVector(130,0,155),FVector(640,235,205),FVector(150,0,340));
}
bool UMaskAssetEditorLibrary::ConfigureRhinoRearChassis(USkeletalMesh* Mesh)
{
	return ConfigureMaskChassis(Mesh,TEXT("/Game/MASK/Rhino/"),FVector(0,0,75),FVector(290,270,100),FVector(15,0,225));
}
bool UMaskAssetEditorLibrary::ConfigureHurricaneChassis(USkeletalMesh* Mesh)
{
	return ConfigureMaskChassis(Mesh,TEXT("/Game/MASK/Hurricane/"),FVector(0,0,72),FVector(510,180,72),FVector(40,0,225));
}

bool UMaskAssetEditorLibrary::ConfigureRavenChassis(USkeletalMesh* Mesh)
{
	return ConfigureMaskChassis(Mesh,TEXT("/Game/MASK/Raven/"),FVector(0,0,52),FVector(435,170,52),FVector(215,0,55));
}

bool UMaskAssetEditorLibrary::ConfigureCondorChassis(USkeletalMesh* Mesh)
{
	return ConfigureMaskChassis(Mesh,TEXT("/Game/MASK/Condor/"),FVector(-5,0,65),FVector(230,38,50),FVector(137,0,78));
}
