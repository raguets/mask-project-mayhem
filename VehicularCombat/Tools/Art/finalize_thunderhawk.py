"""Small repeatable editor/commandlet finalization; no mesh reimport or asset deletion."""
import unreal,json,traceback
from pathlib import Path
PROJECT=Path(unreal.Paths.project_dir());DEST='/Game/MASK/Thunderhawk'
report={'passed':False};lib=unreal.EditorAssetLibrary
try:
    mesh=lib.load_asset(DEST+'/SK_THK_Physics')
    if not unreal.MaskAssetEditorLibrary.configure_thunderhawk_chassis(mesh):raise RuntimeError('Physics root configuration failed')
    lib.save_loaded_asset(mesh);lib.save_loaded_asset(mesh.get_editor_property('physics_asset'))
    definition=lib.load_asset(DEST+'/DA_Thunderhawk');blueprint=lib.load_asset(DEST+'/BP_Thunderhawk')
    if not definition or not blueprint:raise RuntimeError('Missing completed import')
    label_path=DEST+'/PAL_Thunderhawk'
    label=lib.load_asset(label_path) if lib.does_asset_exist(label_path) else None
    if not label:
        factory=unreal.DataAssetFactory();factory.set_editor_property('data_asset_class',unreal.PrimaryAssetLabel)
        label=unreal.AssetToolsHelpers.get_asset_tools().create_asset('PAL_Thunderhawk',DEST,unreal.PrimaryAssetLabel,factory)
    label.set_editor_property('is_runtime_label',True);label.set_editor_property('label_assets_in_my_directory',False)
    label.set_editor_property('explicit_assets',[definition]);label.set_editor_property('explicit_blueprints',[blueprint.generated_class()])
    rules=unreal.PrimaryAssetRules();rules.set_editor_property('cook_rule',unreal.PrimaryAssetCookRule.ALWAYS_COOK)
    rules.set_editor_property('apply_recursively',True);label.set_editor_property('rules',rules);lib.save_loaded_asset(label)
    report.update(passed=True,chassis=mesh.get_path_name(),label=label.get_path_name())
except Exception:report['error']=traceback.format_exc();unreal.log_error(report['error'])
finally:
    (PROJECT/'Saved/Art/thunderhawk-finalize.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    unreal.log_warning('MASK_FINALIZE '+json.dumps(report))
