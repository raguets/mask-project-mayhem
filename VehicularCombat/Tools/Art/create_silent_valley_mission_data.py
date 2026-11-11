"""Create the editable mission tuning asset without touching the level or textures."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir());out=root/'Saved/SilentValley/mission-data';out.mkdir(parents=True,exist_ok=True)
path='/Game/MASK/Missions/SilentValley/DA_SilentValley_01'
asset=unreal.load_asset(path)
if not asset:
    factory=unreal.DataAssetFactory();factory.set_editor_property('data_asset_class',unreal.SilentValleyMissionDefinition)
    asset=unreal.AssetToolsHelpers.get_asset_tools().create_asset('DA_SilentValley_01','/Game/MASK/Missions/SilentValley',unreal.SilentValleyMissionDefinition,factory)
if not isinstance(asset,unreal.SilentValleyMissionDefinition) or not unreal.EditorAssetLibrary.save_loaded_asset(asset,False):raise RuntimeError('Mission asset save failed')
(out/'report.json').write_text(json.dumps({'saved':True,'definition':asset.get_path_name()},indent=2),encoding='utf-8')
