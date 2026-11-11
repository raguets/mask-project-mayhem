"""Commandlet-safe completion and actual saved-asset contract checks for Raven."""
import unreal,json,traceback,re
from pathlib import Path
PROJECT=Path(unreal.Paths.project_dir()).resolve();SOURCE=PROJECT/'SourceArt/MASK/Raven';DEST='/Game/MASK/Raven'
DEFAULT_ATLAS='SM_RV_PresentationOffset_BaseColor';REPORT=PROJECT/'Saved/Art/raven-finalize.json'
report={'passed':False,'imported':[]};assets=unreal.AssetToolsHelpers.get_asset_tools();lib=unreal.EditorAssetLibrary
exec((PROJECT/'Tools/Art/unreal_mask_import_helpers.py').read_text(encoding='utf-8-sig'))
try:
    unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
    definition=lib.load_asset(DEST+'/DA_Raven');body=definition.get_editor_property('driver');skeleton=body.get_editor_property('skeleton')
    hair=import_fbx('CalhounHair.fbx','SK_CalhounHair',True,skeleton)
    manifest=json.loads((SOURCE/'manifest.json').read_text());assign_materials(hair,'CalhounHair',manifest['materials'],True)
    unreal.SkeletalMeshEditorSubsystem.regenerate_lod(hair,3,False,False);lib.save_loaded_asset(hair)
    definition.set_editor_property('hair',hair);lib.save_loaded_asset(definition)
    thunder=lib.load_asset('/Game/MASK/Thunderhawk/DA_Thunderhawk')
    dyn=definition.get_editor_property('dynamics');tdyn=thunder.get_editor_property('dynamics')
    parts=definition.get_editor_property('parts');wheels=definition.get_editor_property('wheels')
    checks={
        'vehicle_and_pilot':definition.get_editor_property('vehicle_name')=='Raven' and definition.get_editor_property('driver_name')=='Calhoun Burns',
        'supports_fixed_wing':definition.get_editor_property('supports_flight') and dyn.get_editor_property('flight_model')==unreal.MaskFlightModel.FIXED_WING,
        'same_minimum_speed_as_thunderhawk':dyn.get_editor_property('minimum_airspeed_mps')==tdyn.get_editor_property('minimum_airspeed_mps') and dyn.get_editor_property('minimum_airspeed_mps')>5,
        'same_maximum_speed_as_thunderhawk':dyn.get_editor_property('maximum_airspeed_mps')==tdyn.get_editor_property('maximum_airspeed_mps'),
        'four_named_wheels':{str(w.get_editor_property('name')) for w in wheels}=={'FL','FR','RL','RR'},
        'twenty_rigid_groups_with_97_samples':len(parts)==20 and all(len(p.get_editor_property('samples'))==97 and p.get_editor_property('mesh') for p in parts),
        'one_skeleton_body_hair_mask':all(definition.get_editor_property(k).get_editor_property('skeleton')==skeleton for k in ['driver','hair','mask']),
        'locomotion_and_jump_assigned':bool(definition.get_editor_property('driver_locomotion') and definition.get_editor_property('driver_jump')),
        'raven_pawn_blueprint':isinstance(unreal.get_default_object(lib.load_blueprint_class(DEST+'/BP_Raven')),unreal.RavenPawn),
        'cook_label_present':lib.does_asset_exist(DEST+'/PAL_Raven'),
        'separate_dark_rear_glass':lib.does_asset_exist(DEST+'/Materials/M_Raven_RearPrivacyGlass') and lib.does_asset_exist(DEST+'/Materials/M_Raven_Glass')
    }
    report.update(checks=checks,passed=all(checks.values()),parts=len(parts),minimum_airspeed_mps=dyn.get_editor_property('minimum_airspeed_mps'),maximum_airspeed_mps=dyn.get_editor_property('maximum_airspeed_mps'))
    if not report['passed']:raise RuntimeError('Raven contract checks failed')
except Exception:
    report['error']=traceback.format_exc();raise
finally:REPORT.write_text(json.dumps(report,indent=2),encoding='utf-8')
