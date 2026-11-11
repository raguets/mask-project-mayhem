"""UE full-editor finalization: aligned masks and a playable six-wheel Bruce rear vehicle."""
import unreal,json,traceback,re
from pathlib import Path
PROJECT=Path(unreal.Paths.project_dir()).resolve();SOURCE=PROJECT/'SourceArt/MASK/Rhino';DEST='/Game/MASK/Rhino';DEFAULT_ATLAS='SM_Rhino_Control_BaseColor'
report={'passed':False,'imported':[]};lib=unreal.EditorAssetLibrary;assets=unreal.AssetToolsHelpers.get_asset_tools()
exec((PROJECT/'Tools/Art/unreal_mask_import_helpers.py').read_text(encoding='utf-8-sig'))
try:
    unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
    for name in ('Alex','Bruce'):
        skeleton=lib.load_asset(DEST+'/SK_'+name).get_editor_property('skeleton')
        mask=import_fbx(name+'Mask.fbx','SK_'+name+'Mask',True,skeleton)
        unreal.SkeletalMeshEditorSubsystem.regenerate_lod(mask,3,False,False);lib.save_loaded_asset(mask);lib.save_loaded_asset(skeleton)
    chassis=import_fbx('RhinoRear_Physics.fbx','SK_RH_Rear_Physics',True)
    if not unreal.MaskAssetEditorLibrary.configure_rhino_rear_chassis(chassis):raise RuntimeError('Rear chassis setup failed')
    for item in (chassis,chassis.get_editor_property('skeleton'),chassis.get_editor_property('physics_asset')):lib.save_loaded_asset(item)
    main=lib.load_asset(DEST+'/DA_Rhino');pod=lib.load_asset(DEST+'/DA_RhinoRear');manifest=json.loads((SOURCE/'manifest.json').read_text())
    for prop in ('passenger','passenger_hair','passenger_mask','passenger_pose'):main.set_editor_property(prop,None)
    main.set_editor_property('rear_module_origin',unreal.Vector(-260,0,0));main.set_editor_property('override_center_of_mass',True);main.set_editor_property('center_of_mass',unreal.Vector(0,0,70))
    pod.set_editor_property('chassis',chassis);pod.set_editor_property('vehicle_name','Rhino - module arriere');pod.set_editor_property('driver_name','Bruce Sato');pod.set_editor_property('mask_name','Lifter')
    pod.set_editor_property('supports_flight',False);pod.set_editor_property('mass_kg',1100.);pod.set_editor_property('engine_torque',650.)
    pod.set_editor_property('driver',lib.load_asset(DEST+'/SK_Bruce'));pod.set_editor_property('hair',lib.load_asset(DEST+'/SK_BruceHair'));pod.set_editor_property('mask',lib.load_asset(DEST+'/SK_BruceMask'))
    for pose in ('Driving','Standing'):pod.set_editor_property('driving_pose' if pose=='Driving' else 'standing_pose',lib.load_asset(DEST+'/AN_Bruce_'+pose))
    pod.set_editor_property('driver_location',unreal.Vector(55,0,60));pod.set_editor_property('mounted_driver_location',unreal.Vector(460,-60,137))
    pod.set_editor_property('visual_origin_offset',unreal.Vector(260,0,0));pod.set_editor_property('override_center_of_mass',True);pod.set_editor_property('center_of_mass',unreal.Vector(0,0,50))
    pod.set_editor_property('chase_location',unreal.Vector(0,0,175));pod.set_editor_property('chase_distance',800.);pod.set_editor_property('cockpit_location',unreal.Vector(15,0,180))
    wheels=[]
    for source in manifest['wheels']:
        if not source['pod']:continue
        w=unreal.MaskWheelDefinition();w.set_editor_property('name',source['label']);p=source['position_cm'];w.set_editor_property('center',unreal.Vector(p[0]+260,p[1],p[2]))
        w.set_editor_property('wheel_class',unreal.RhinoPodFrontWheel if 'MiddleInner' in source['prefix'] else unreal.RhinoPodRearWheel);wheels.append(w)
    pod.set_editor_property('wheels',wheels)
    for item in (main,pod):lib.save_loaded_asset(item)
    path=DEST+'/BP_RhinoRear';blueprint=lib.load_asset(path) if lib.does_asset_exist(path) else lib.duplicate_asset('/Game/Blueprints/Pawns/BP_PlayerVehicle',path)
    unreal.BlueprintEditorLibrary.reparent_blueprint(blueprint,unreal.RhinoRearModule);unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
    unreal.get_default_object(blueprint.generated_class()).set_editor_property('definition',pod);unreal.BlueprintEditorLibrary.compile_blueprint(blueprint);lib.save_loaded_asset(blueprint)
    label=lib.load_asset(DEST+'/PAL_Rhino');label.set_editor_property('explicit_assets',[main,pod]);label.set_editor_property('explicit_blueprints',[lib.load_asset(DEST+'/BP_Rhino').generated_class(),blueprint.generated_class()]);lib.save_loaded_asset(label)
    report.update(passed=True,playable_rear=blueprint.get_path_name(),same_bruce_mesh=pod.get_editor_property('driver').get_path_name(),rear_wheels=len(wheels))
except Exception:report['error']=traceback.format_exc();unreal.log_error(report['error'])
finally:
    (PROJECT/'Saved/Art/rhino-finalize.json').write_text(json.dumps(report,indent=2));unreal.log_warning('RHINO_FINALIZE '+json.dumps({k:v for k,v in report.items() if k in ('passed','error')}))
    if unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem):unreal.SystemLibrary.quit_editor()
