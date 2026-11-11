"""Read-only import/API audit before the environment pass."""
import unreal,json
from pathlib import Path
registry=unreal.AssetRegistryHelpers.get_asset_registry();registry.search_all_assets(True)
report={'resources':[],'api':{}}
for folder in ['/Game/Megaplant_Library','/Game/Fab/Megascans/Plants','/Game/Fab/Megascans/Surfaces']:
    registry.scan_paths_synchronous([folder],True)
    for a in registry.get_assets_by_path(folder,True):
        cls=str(a.asset_class_path.asset_name)
        if cls in ['StaticMesh','SkeletalMesh','MaterialInstanceConstant','Texture2D']:
            report['resources'].append({'path':str(a.package_name),'class':cls})
for name in ['MaterialShadingModel','MaterialExpressionSingleLayerWaterMaterialOutput','VolumetricCloudComponent','HierarchicalInstancedStaticMeshComponent']:
    cls=getattr(unreal,name,None);report['api'][name]=str(cls.__doc__) if cls else 'Unavailable'
out=Path(unreal.Paths.project_dir())/'Saved/SilentValley/environment-v1';out.mkdir(parents=True,exist_ok=True)
(out/'resources.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
