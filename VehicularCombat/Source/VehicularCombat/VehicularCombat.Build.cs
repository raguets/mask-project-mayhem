// Copyright Epic Games, Inc. All Rights Reserved.

using UnrealBuildTool;

public class VehicularCombat : ModuleRules
{
	public VehicularCombat(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
		
		PublicDependencyModuleNames.AddRange(new string[]
		{
		    "Core",
		    "CoreUObject",
		    "Engine",
		    "InputCore",
			"UMG",
			"AIModule",
			"ChaosVehicles",
			"HeadMountedDisplay",
			"PhysicsCore",
			"NavigationSystem",
			"OnlineSubsystem",
			"OnlineSubsystemSteam",
			"OnlineSubsystemUtils"
		});
		PrivateDependencyModuleNames.Add("OnlineBase");
		PrivateDependencyModuleNames.Add("ChaosVehiclesCore");
		PrivateDependencyModuleNames.Add("AnimGraphRuntime");
		PrivateDependencyModuleNames.Add("SlateCore");
		if(Target.bBuildEditor) { PrivateDependencyModuleNames.AddRange(new string[] { "AssetRegistry", "UnrealEd", "Landscape", "Foliage", "MeshDescription", "StaticMeshDescription" }); }
		if (Target.Configuration != UnrealTargetConfiguration.Shipping)
		{
			PrivateDependencyModuleNames.Add("Json");
			PrivateDependencyModuleNames.Add("Slate");
		}
	}
}
