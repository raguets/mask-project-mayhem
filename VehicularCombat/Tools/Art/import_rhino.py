"""UE full editor: import Rhino, Alex/Jackrabbit and Bruce/Lifter into an isolated folder."""
import unreal,json,traceback,re
from pathlib import Path
PROJECT=Path(unreal.Paths.project_dir()).resolve();SOURCE=PROJECT/'SourceArt/MASK/Rhino'
DEST='/Game/MASK/Rhino';DEFAULT_ATLAS='SM_Rhino_Control_BaseColor'
REPORT=PROJECT/'Saved/Art/rhino-import.json';report={'passed':False,'imported':[]}
assets=unreal.AssetToolsHelpers.get_asset_tools();lib=unreal.EditorAssetLibrary
exec((PROJECT/'Tools/Art/unreal_mask_import_helpers.py').read_text(encoding='utf-8-sig'))

def animation(name,pose,skeleton):
    task=unreal.AssetImportTask();task.filename=str(SOURCE/(name+'_'+pose+'.fbx'));task.destination_path=DEST
    task.destination_name='AN_'+name+'_'+pose;task.automated=True;task.replace_existing=True;task.save=True;task.factory=unreal.FbxFactory()
    options=unreal.FbxImportUI();options.automated_import_should_detect_type=False;options.import_as_skeletal=False;options.import_mesh=False;options.import_animations=True
    options.mesh_type_to_import=unreal.FBXImportType.FBXIT_ANIMATION;options.skeleton=skeleton
    options.anim_sequence_import_data.set_editor_property('animation_length',unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME)
    options.anim_sequence_import_data.set_editor_property('remove_redundant_keys',False);task.options=options;assets.import_asset_tasks([task])
    return lib.load_asset(DEST+'/'+task.destination_name)

def definition(name):
    path=DEST+'/DA_'+name
    if lib.does_asset_exist(path):return lib.load_asset(path)
    factory=unreal.DataAssetFactory();factory.set_editor_property('data_asset_class',unreal.MaskVehicleDefinition)
    return assets.create_asset('DA_'+name,DEST,unreal.MaskVehicleDefinition,factory)

try:
    unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
    manifest=json.loads((SOURCE/'manifest.json').read_text(encoding='utf-8'));lib.make_directory(DEST)
    for image in SOURCE.glob('*_BaseColor.png'):
        task=unreal.AssetImportTask();task.filename=str(image);task.destination_path=DEST+'/Textures';task.destination_name=image.stem;task.automated=True;task.replace_existing=True;task.save=True;assets.import_asset_tasks([task])
    import_fbx('Rhino_Visual.fbx','Rhino_Visual')
    chassis=import_fbx('Rhino_Physics.fbx','SK_RH_Physics',True)
    if not unreal.MaskAssetEditorLibrary.configure_rhino_chassis(chassis):raise RuntimeError('Rhino physics configuration failed')
    lib.save_loaded_asset(chassis);lib.save_loaded_asset(chassis.get_editor_property('skeleton'));lib.save_loaded_asset(chassis.get_editor_property('physics_asset'))
    crew={};report['lods']={}
    for actor in manifest['crew']:
        name=actor['name'];body=import_fbx(name+'Body.fbx','SK_'+name,True);skeleton=body.get_editor_property('skeleton');lib.save_loaded_asset(skeleton)
        item={'Body':body,'Hair':None,'Mask':None,'location':actor['location_cm']}
        for kind in actor['meshes']:
            mesh=body if kind=='Body' else import_fbx(name+kind+'.fbx','SK_'+name+kind,True,skeleton)
            assign_materials(mesh,name+kind,manifest['materials'],True);item[kind]=mesh
            report['lods'][name+kind]=unreal.SkeletalMeshEditorSubsystem.regenerate_lod(mesh,3,False,False);lib.save_loaded_asset(mesh)
        for pose in ('Driving','Standing'):item[pose]=animation(name,pose,skeleton)
        crew[name]=item
    main=definition('Rhino');pod=definition('RhinoRear');main_parts=[];pod_parts=[]
    editor=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    for item in manifest['parts']:
        mesh=lib.load_asset(DEST+'/'+item['name']) if lib.does_asset_exist(DEST+'/'+item['name']) else next((lib.load_asset(p) for p in report['imported'] if p.split('.')[-1].endswith(item['name'])),None)
        if not mesh:raise RuntimeError('Missing Rhino part '+item['name'])
        assign_materials(mesh,item['name'],manifest['materials']);options=unreal.StaticMeshReductionOptions();options.set_editor_property('auto_compute_lod_screen_size',True);lods=[]
        for fraction,screen in [(1.,1.),(.5,.45),(.2,.16)]:
            lod=unreal.StaticMeshReductionSettings();lod.set_editor_property('percent_triangles',fraction);lod.set_editor_property('screen_size',screen);lods.append(lod)
        options.set_editor_property('reduction_settings',lods);editor.set_lods(mesh,options);lib.save_loaded_asset(mesh)
        part=unreal.MaskVehiclePart();part.set_editor_property('name',item['name']);part.set_editor_property('mesh',mesh);part.set_editor_property('wheel',item['wheel']);samples=[]
        for i,s in enumerate(item['samples']):
            t=unreal.Transform();t.translation=unreal.Vector(*s['t']);t.rotation=unreal.Quat(*s['q']);t.scale3d=unreal.Vector(*s['s'])
            if item['pod']:
                # Rear root has translation only in this source. Remove it from
                # local part tracks: the persistent module actor supplies that motion.
                offset=manifest['pod_track'][i]['t'];t.translation=unreal.Vector(s['t'][0]-offset[0],s['t'][1]-offset[1],s['t'][2]-offset[2])
            samples.append(t)
        part.set_editor_property('samples',samples);(pod_parts if item['pod'] else main_parts).append(part)
    main.set_editor_property('parts',main_parts);pod.set_editor_property('parts',pod_parts)
    wheel_sets={False:[],True:[]}
    for wheel in manifest['wheels']:
        w=unreal.MaskWheelDefinition();w.set_editor_property('name',wheel['label']);w.set_editor_property('center',unreal.Vector(*wheel['position_cm']))
        w.set_editor_property('wheel_class',unreal.RhinoFrontWheel if 'Front' in wheel['prefix'] else unreal.RhinoRearWheel);wheel_sets[wheel['pod']].append(w)
    main.set_editor_property('wheels',wheel_sets[False]);pod.set_editor_property('wheels',wheel_sets[True])
    main.set_editor_property('chassis',chassis);main.set_editor_property('vehicle_name','Rhino');main.set_editor_property('driver_name','Alex Sector');main.set_editor_property('mask_name','Jackrabbit')
    main.set_editor_property('supports_flight',False);main.set_editor_property('mass_kg',6000.);main.set_editor_property('engine_torque',2200.);main.set_editor_property('transform_seconds',manifest['duration'])
    for key,kind in [('driver','Body'),('hair','Hair'),('mask','Mask'),('driving_pose','Driving'),('standing_pose','Standing')]:main.set_editor_property(key,crew['Alex'][kind])
    main.set_editor_property('driver_location',unreal.Vector(*crew['Alex']['location']))
    for key,kind in [('passenger','Body'),('passenger_hair','Hair'),('passenger_mask','Mask'),('passenger_pose','Driving')]:main.set_editor_property(key,crew['Bruce'][kind])
    main.set_editor_property('passenger_location',unreal.Vector(*crew['Bruce']['location']))
    main.set_editor_property('chase_location',unreal.Vector(100,0,280));main.set_editor_property('chase_distance',1250.);main.set_editor_property('cockpit_location',unreal.Vector(155,60,255))
    main.set_editor_property('clearance_center',unreal.Vector(-200,100,240));main.set_editor_property('clearance_extent',unreal.Vector(700,450,170));main.set_editor_property('rear_module',pod)
    track=[]
    for s in manifest['pod_track']:
        t=unreal.Transform();t.translation=unreal.Vector(*s['t']);t.rotation=unreal.Quat(*s['q']);t.scale3d=unreal.Vector(*s['s']);track.append(t)
    main.set_editor_property('rear_module_track',track);lib.save_loaded_asset(main);lib.save_loaded_asset(pod)
    blueprint=lib.load_asset(DEST+'/BP_Rhino') if lib.does_asset_exist(DEST+'/BP_Rhino') else lib.duplicate_asset('/Game/Blueprints/Pawns/BP_PlayerVehicle',DEST+'/BP_Rhino')
    unreal.BlueprintEditorLibrary.reparent_blueprint(blueprint,unreal.RhinoPawn);unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
    unreal.get_default_object(blueprint.generated_class()).set_editor_property('definition',main);unreal.BlueprintEditorLibrary.compile_blueprint(blueprint);lib.save_loaded_asset(blueprint)
    path=DEST+'/PAL_Rhino';label=lib.load_asset(path) if lib.does_asset_exist(path) else None
    if not label:
        factory=unreal.DataAssetFactory();factory.set_editor_property('data_asset_class',unreal.PrimaryAssetLabel);label=assets.create_asset('PAL_Rhino',DEST,unreal.PrimaryAssetLabel,factory)
    label.set_editor_property('is_runtime_label',True);label.set_editor_property('label_assets_in_my_directory',False);label.set_editor_property('explicit_assets',[main,pod]);label.set_editor_property('explicit_blueprints',[blueprint.generated_class()])
    rules=unreal.PrimaryAssetRules();rules.set_editor_property('cook_rule',unreal.PrimaryAssetCookRule.ALWAYS_COOK);rules.set_editor_property('apply_recursively',True);label.set_editor_property('rules',rules);lib.save_loaded_asset(label)
    import runpy
    runpy.run_path(str(PROJECT/'Tools/Art/finalize_rhino.py'))
    if not json.loads((PROJECT/'Saved/Art/rhino-finalize.json').read_text())['passed']:raise RuntimeError('Playable rear finalization failed')
    report.update(passed=True,parts=len(main_parts)+len(pod_parts),truck_tires=len(wheel_sets[False]),pod_tires=len(wheel_sets[True]),crew=['Alex Sector','Bruce Sato'])
except Exception:report['error']=traceback.format_exc();unreal.log_error(report['error'])
finally:
    REPORT.write_text(json.dumps(report,indent=2),encoding='utf-8');unreal.log_warning('RHINO_IMPORT '+json.dumps({k:v for k,v in report.items() if k in ('passed','error','parts')}))
    if unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem):unreal.SystemLibrary.quit_editor()
