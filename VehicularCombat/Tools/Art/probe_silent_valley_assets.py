"""Read-only resolution probe; file presence and registry presence are distinct."""
import unreal,json
from pathlib import Path
registry=unreal.AssetRegistryHelpers.get_asset_registry();registry.search_all_assets(True);registry.scan_paths_synchronous(['/Game/Core','/Game/Fab'],True,True)
paths=['/Game/Core/BP_CustomGameMode','/Game/Core/BP_CustomPlayerController','/Game/Fab/Megascans/3D/Small_Beach_Rock_wd4kfdx/Medium/wd4kfdx_tier_2/StaticMeshes/wd4kfdx_tier_2']
report=[]
for path in paths:
    direct=unreal.load_asset(path);registered=unreal.EditorAssetLibrary.does_asset_exist(path)
    report.append({'path':path,'direct':direct.get_path_name() if direct else None,'class':direct.get_class().get_name() if direct else None,'registry':registered})
Path(unreal.Paths.project_dir(),'Saved/SilentValley/asset-resolution.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
