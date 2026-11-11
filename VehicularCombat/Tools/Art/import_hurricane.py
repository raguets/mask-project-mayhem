"""Full UE editor import: Hurricane V7, one Hondo and separately visible Blaster."""
import unreal,json,traceback,re
from pathlib import Path
PROJECT=Path(unreal.Paths.project_dir()).resolve();SOURCE=PROJECT/'SourceArt/MASK/Hurricane'
DEST='/Game/MASK/Hurricane';DEFAULT_ATLAS='SM_Hurricane_Control_BaseColor'
REPORT=PROJECT/'Saved/Art/hurricane-import.json';report={'passed':False,'imported':[]}
assets=unreal.AssetToolsHelpers.get_asset_tools();lib=unreal.EditorAssetLibrary
exec((PROJECT/'Tools/Art/unreal_mask_import_helpers.py').read_text(encoding='utf-8-sig'))

def transforms(samples):
    result=[]
    for s in samples:
        t=unreal.Transform();t.translation=unreal.Vector(*s['t']);t.rotation=unreal.Quat(*s['q']);t.scale3d=unreal.Vector(*s['s']);result.append(t)
    return result

def animation(pose,skeleton):
    task=unreal.AssetImportTask();task.filename=str(SOURCE/('Hondo_'+pose+'.fbx'));task.destination_path=DEST
    task.destination_name='AN_Hondo_'+pose;task.automated=True;task.replace_existing=True;task.save=True;task.factory=unreal.FbxFactory()
    options=unreal.FbxImportUI();options.automated_import_should_detect_type=False;options.import_as_skeletal=False;options.import_mesh=False;options.import_animations=True
    options.mesh_type_to_import=unreal.FBXImportType.FBXIT_ANIMATION;options.skeleton=skeleton
    options.anim_sequence_import_data.set_editor_property('animation_length',unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME)
    options.anim_sequence_import_data.set_editor_property('remove_redundant_keys',False);task.options=options;assets.import_asset_tasks([task])
    return lib.load_asset(DEST+'/'+task.destination_name)

try:
    unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
    manifest=json.loads((SOURCE/'manifest.json').read_text());lib.make_directory(DEST)
    for image in SOURCE.glob('*_BaseColor.png'):
        task=unreal.AssetImportTask();task.filename=str(image);task.destination_path=DEST+'/Textures';task.destination_name=image.stem
        task.automated=True;task.replace_existing=True;task.save=True;assets.import_asset_tasks([task])
    import_fbx('Hurricane_Visual.fbx','Hurricane_Visual')
    chassis=import_fbx('Hurricane_Physics.fbx','SK_HU_Physics',True)
    if not unreal.MaskAssetEditorLibrary.configure_hurricane_chassis(chassis):raise RuntimeError('Hurricane physics configuration failed')
    for item in (chassis,chassis.get_editor_property('skeleton'),chassis.get_editor_property('physics_asset')):lib.save_loaded_asset(item)
    body=import_fbx('HondoBody.fbx','SK_Hondo',True);skeleton=body.get_editor_property('skeleton');lib.save_loaded_asset(skeleton);crew={'Hair':None};report['lods']={}
    # V7's short hair is part of the body mesh; do not invent a second head/hair.
    for kind in ('Body','Mask'):
        mesh=body if kind=='Body' else import_fbx('Hondo'+kind+'.fbx','SK_Hondo'+kind,True,skeleton)
        if not mesh:raise RuntimeError('Missing Hondo '+kind)
        assign_materials(mesh,'Hondo'+kind,manifest['materials'],True);crew[kind]=mesh
        report['lods'][kind]=unreal.SkeletalMeshEditorSubsystem.regenerate_lod(mesh,3,False,False);lib.save_loaded_asset(mesh)
    for pose in ('Driving','Standing','Transform'):
        crew[pose]=animation(pose,skeleton)
        if not crew[pose]:raise RuntimeError('Missing Hondo '+pose+' animation')
    path=DEST+'/DA_Hurricane'
    if lib.does_asset_exist(path):definition=lib.load_asset(path)
    else:
        factory=unreal.DataAssetFactory();factory.set_editor_property('data_asset_class',unreal.MaskVehicleDefinition)
        definition=assets.create_asset('DA_Hurricane',DEST,unreal.MaskVehicleDefinition,factory)
    editor=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem);parts=[];mapping={}
    imported=[lib.load_asset(p) for p in report['imported']]
    for item in manifest['parts']:
        name=item['name'];mesh=lib.load_asset(DEST+'/'+name) if lib.does_asset_exist(DEST+'/'+name) else None
        if not mesh:
            # FBX sanitizes punctuation in controller names. Retain minus signs
            # when matching so the four shock/upright quadrants stay distinct.
            canonical=lambda s:re.sub(r'[^A-Za-z0-9_-]','_',s)
            mesh=next((m for m in imported if isinstance(m,unreal.StaticMesh) and (m.get_name().endswith(canonical(name)) or m.get_name().endswith(name))),None)
        if not mesh:raise RuntimeError('Missing part '+name+'; available='+str([m.get_name() for m in imported if m]))
        mapping[name]=mesh.get_path_name();assign_materials(mesh,name,manifest['materials'])
        options=unreal.StaticMeshReductionOptions();options.set_editor_property('auto_compute_lod_screen_size',True);lods=[]
        for fraction,screen in [(1.,1.),(.5,.45),(.2,.16)]:
            lod=unreal.StaticMeshReductionSettings();lod.set_editor_property('percent_triangles',fraction);lod.set_editor_property('screen_size',screen);lods.append(lod)
        options.set_editor_property('reduction_settings',lods);editor.set_lods(mesh,options)
        if item['control']==manifest['spare_control']:
            editor.add_simple_collisions(mesh,unreal.ScriptingCollisionShapeType.BOX)
            definition.set_editor_property('spare_mesh',mesh);definition.set_editor_property('spare_mount_samples',transforms(item['samples']))
        else:
            p=unreal.MaskVehiclePart();p.set_editor_property('name',name);p.set_editor_property('mesh',mesh);p.set_editor_property('wheel',item['wheel']);p.set_editor_property('samples',transforms(item['samples']));parts.append(p)
        lib.save_loaded_asset(mesh)
    wheels=[]
    for source in manifest['wheels']:
        w=unreal.MaskWheelDefinition();w.set_editor_property('name',source['label']);w.set_editor_property('center',unreal.Vector(*source['position_cm']))
        w.set_editor_property('wheel_class',unreal.HurricaneFrontWheel if 'Front' in source['prefix'] else unreal.HurricaneRearWheel);wheels.append(w)
    for prop,value in dict(parts=parts,wheels=wheels,chassis=chassis,vehicle_name='Hurricane',driver_name='Hondo MacLean',mask_name='Blaster',supports_flight=False,
        mass_kg=1800.,engine_torque=550.,transform_seconds=manifest['duration'],driver=crew['Body'],hair=crew['Hair'],mask=crew['Mask'],
        driving_pose=crew['Driving'],standing_pose=crew['Standing'],driver_transformation_pose=crew['Transform'],driver_transform_samples=transforms(manifest['driver_tracks']),
        driver_location=unreal.Vector(*manifest['driver_location_cm']),override_center_of_mass=True,center_of_mass=unreal.Vector(0,0,45),
        chase_location=unreal.Vector(0,0,155),chase_distance=800.,cockpit_location=unreal.Vector(-15,-37,148),
        clearance_center=unreal.Vector(0,0,200),clearance_extent=unreal.Vector(300,135,130)).items():definition.set_editor_property(prop,value)
    lib.save_loaded_asset(definition)
    path=DEST+'/BP_Hurricane';blueprint=lib.load_asset(path) if lib.does_asset_exist(path) else lib.duplicate_asset('/Game/Blueprints/Pawns/BP_PlayerVehicle',path)
    unreal.BlueprintEditorLibrary.reparent_blueprint(blueprint,unreal.HurricanePawn);unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
    unreal.get_default_object(blueprint.generated_class()).set_editor_property('definition',definition);unreal.BlueprintEditorLibrary.compile_blueprint(blueprint);lib.save_loaded_asset(blueprint)
    path=DEST+'/PAL_Hurricane';label=lib.load_asset(path) if lib.does_asset_exist(path) else None
    if not label:
        factory=unreal.DataAssetFactory();factory.set_editor_property('data_asset_class',unreal.PrimaryAssetLabel);label=assets.create_asset('PAL_Hurricane',DEST,unreal.PrimaryAssetLabel,factory)
    label.set_editor_property('is_runtime_label',True);label.set_editor_property('label_assets_in_my_directory',False)
    label.set_editor_property('explicit_assets',[definition]);label.set_editor_property('explicit_blueprints',[blueprint.generated_class()])
    rules=unreal.PrimaryAssetRules();rules.set_editor_property('cook_rule',unreal.PrimaryAssetCookRule.ALWAYS_COOK);rules.set_editor_property('apply_recursively',True);label.set_editor_property('rules',rules);lib.save_loaded_asset(label)
    report.update(passed=True,parts=len(parts),tires=len(wheels),crew='One Hondo rig/body/head with detachable Blaster',mapping=mapping)
except Exception:report['error']=traceback.format_exc();unreal.log_error(report['error'])
finally:
    REPORT.write_text(json.dumps(report,indent=2));unreal.log_warning('HURRICANE_IMPORT '+json.dumps({k:v for k,v in report.items() if k in ('passed','error','parts')}));unreal.SystemLibrary.quit_editor()
