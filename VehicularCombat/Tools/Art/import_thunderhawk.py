"""UE editor Python: import new M.A.S.K. assets; preserve original car and maps.

Requires the compiled native MASK classes. Run using UnrealEditor-Cmd -run=pythonscript.
"""
import unreal, json, traceback, re
from pathlib import Path

PROJECT=Path(unreal.Paths.project_dir()).resolve()
SOURCE=PROJECT/'SourceArt/MASK/Thunderhawk'
DEST='/Game/MASK/Thunderhawk'
REPORT=PROJECT/'Saved/Art/thunderhawk-import.json'
report={'passed':False,'imported':[]}
assets=unreal.AssetToolsHelpers.get_asset_tools()
lib=unreal.EditorAssetLibrary

def import_fbx(filename,name,skeletal=False,skeleton=None,animate=False):
    task=unreal.AssetImportTask();task.filename=str(SOURCE/filename);task.destination_path=DEST;task.destination_name=name
    task.automated=True;task.replace_existing=True;task.save=True;task.factory=unreal.FbxFactory()
    options=unreal.FbxImportUI();options.automated_import_should_detect_type=False
    options.import_as_skeletal=skeletal;options.import_mesh=True;options.import_animations=animate
    options.import_materials=False;options.import_textures=False;options.create_physics_asset=skeletal and name=='SK_THK_Physics'
    options.mesh_type_to_import=unreal.FBXImportType.FBXIT_SKELETAL_MESH if skeletal else unreal.FBXImportType.FBXIT_STATIC_MESH
    if skeleton:options.skeleton=skeleton
    data=options.skeletal_mesh_import_data if skeletal else options.static_mesh_import_data
    data.import_uniform_scale=1.0
    data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS
    if not skeletal:
        data.combine_meshes=False;data.transform_vertex_to_absolute=True
        data.generate_lightmap_u_vs=True;data.auto_generate_collision=False
    else:
        data.set_editor_property('import_content_type',unreal.FBXImportContentType.FBXICT_ALL)
        data.set_editor_property('use_t0_as_ref_pose',False);data.set_editor_property('update_skeleton_reference_pose',True)
    task.options=options
    assets.import_asset_tasks([task]);report['imported']+=list(task.imported_object_paths)
    return lib.load_asset(DEST+'/'+name) if skeletal else None

def texture(name):
    path=DEST+'/Textures/'+name
    if not lib.does_asset_exist(path):
        task=unreal.AssetImportTask();task.filename=str(SOURCE/(name+'.png'));task.destination_path=DEST+'/Textures'
        task.destination_name=name;task.automated=True;task.save=True
        assets.import_asset_tasks([task])
    return lib.load_asset(path)

def scalar(mat,value):
    node=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant,0,0)
    node.set_editor_property('r',float(value));return node

def material(part,slot,contract):
    key=re.sub(r'[^A-Za-z0-9_]','_',part+'_'+slot)
    path=DEST+'/Materials/MI2_'+key
    old=lib.load_asset(path) if lib.does_asset_exist(path) else None
    if old:return old
    edit=unreal.MaterialEditingLibrary
    glass='Glass' in part or contract.get('glass')
    master_name='M_MASK_Glass' if glass else 'M_MASK_PBR'
    master_path=DEST+'/Materials/'+master_name
    mat=lib.load_asset(master_path) if lib.does_asset_exist(master_path) else None
    if mat:
        pass
    elif glass:
        mat=assets.create_asset(master_name,DEST+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
        mat.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT)
        mat.set_editor_property('two_sided',True)
        mat.set_editor_property('translucency_lighting_mode',unreal.TranslucencyLightingMode.TLM_SURFACE_PER_PIXEL_LIGHTING)
        mat.set_editor_property('refraction_method',unreal.RefractionMode.RM_PIXEL_NORMAL_OFFSET)
        color=edit.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,0,0)
        color.set_editor_property('constant',unreal.LinearColor(.11,.18,.20,1))
        edit.connect_material_property(color,'',unreal.MaterialProperty.MP_BASE_COLOR)
        edit.connect_material_property(scalar(mat,.22),'',unreal.MaterialProperty.MP_OPACITY)
        edit.connect_material_property(scalar(mat,.08),'',unreal.MaterialProperty.MP_ROUGHNESS)
        edit.connect_material_property(scalar(mat,.5),'',unreal.MaterialProperty.MP_SPECULAR)
        edit.connect_material_property(scalar(mat,1.45),'',unreal.MaterialProperty.MP_REFRACTION)
    else:
        mat=assets.create_asset(master_name,DEST+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
        node=edit.create_material_expression(mat,unreal.MaterialExpressionTextureSampleParameter2D,0,0)
        node.set_editor_property('parameter_name','Atlas')
        node.set_editor_property('texture',texture('SM_THK_Root_BaseColor'))
        edit.connect_material_property(node,'RGB',unreal.MaterialProperty.MP_BASE_COLOR)
        for parameter,value,prop in [('Metallic',0,unreal.MaterialProperty.MP_METALLIC),('Roughness',.5,unreal.MaterialProperty.MP_ROUGHNESS)]:
            scalar_node=edit.create_material_expression(mat,unreal.MaterialExpressionScalarParameter,0,0)
            scalar_node.set_editor_property('parameter_name',parameter);scalar_node.set_editor_property('default_value',value)
            edit.connect_material_property(scalar_node,'',prop)
    edit.set_material_usage(mat,unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH)
    edit.recompile_material(mat);lib.save_loaded_asset(mat)
    instance=assets.create_asset('MI2_'+key,DEST+'/Materials',unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
    edit.set_material_instance_parent(instance,mat)
    if not glass:
        edit.set_material_instance_texture_parameter_value(instance,'Atlas',texture(part+'_BaseColor'))
        edit.set_material_instance_scalar_parameter_value(instance,'Metallic',contract.get('metallic',0))
        edit.set_material_instance_scalar_parameter_value(instance,'Roughness',contract.get('roughness',.5))
    lib.save_loaded_asset(instance);return instance

def assign_materials(mesh,part,contracts,skeletal=False):
    slots=mesh.get_editor_property('materials') if skeletal else mesh.get_editor_property('static_materials')
    for index,slot in enumerate(slots):
        name=str(slot.get_editor_property('material_slot_name'))
        canonical=name.removeprefix('M_Game_')
        contract=next((m for m in contracts if m['name'].split('.')[0]==canonical),{})
        mat=material(part,name,contract)
        if skeletal:
            slot.set_editor_property('material_interface',mat)
            slots[index]=slot
        else:mesh.set_material(index,mat)
    if skeletal:mesh.set_editor_property('materials',slots)
    lib.save_loaded_asset(mesh,False)

try:
    unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
    manifest=json.loads((SOURCE/'manifest.json').read_text(encoding='utf-8'))
    lib.make_directory(DEST)
    for image in SOURCE.glob('*_BaseColor.png'):
        task=unreal.AssetImportTask();task.filename=str(image);task.destination_path=DEST+'/Textures'
        task.destination_name=image.stem;task.automated=True;task.replace_existing=True;task.save=True
        assets.import_asset_tasks([task])
    import_fbx('Thunderhawk_Visual.fbx','Thunderhawk_Visual')
    chassis=import_fbx('Thunderhawk_Physics.fbx','SK_THK_Physics',True)
    lib.save_loaded_asset(chassis.get_editor_property('skeleton'))
    body=import_fbx('MattBody.fbx','SK_Matt',True,animate=True)
    skeleton=body.get_editor_property('skeleton')
    lib.save_loaded_asset(skeleton)
    for pose in ('Standing','Driving'):
        task=unreal.AssetImportTask();task.filename=str(SOURCE/('Matt_'+pose+'.fbx'));task.destination_path=DEST
        task.destination_name='AN_Matt_'+pose;task.automated=True;task.replace_existing=True;task.save=True;task.factory=unreal.FbxFactory()
        options=unreal.FbxImportUI();options.automated_import_should_detect_type=False
        options.import_as_skeletal=False;options.import_mesh=False;options.import_animations=True
        options.mesh_type_to_import=unreal.FBXImportType.FBXIT_ANIMATION;options.skeleton=skeleton
        options.anim_sequence_import_data.set_editor_property('animation_length',unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME)
        options.anim_sequence_import_data.set_editor_property('remove_redundant_keys',False)
        task.options=options;assets.import_asset_tasks([task]);report['imported']+=list(task.imported_object_paths)
        for path in task.imported_object_paths:lib.save_loaded_asset(lib.load_asset(path))
    hair=import_fbx('MattHair.fbx','SK_MattHair',True,skeleton)
    mask=import_fbx('Spectrum.fbx','SK_Spectrum',True,skeleton)
    if not unreal.MaskAssetEditorLibrary.configure_thunderhawk_chassis(chassis):raise RuntimeError('Physics chassis configuration failed')
    lib.save_loaded_asset(chassis);lib.save_loaded_asset(chassis.get_editor_property('physics_asset'))
    report['skeletal_lods']={}
    for mesh,name in [(body,'MattBody'),(hair,'MattHair'),(mask,'Spectrum')]:
        assign_materials(mesh,name,manifest['materials'],True)
        report['skeletal_lods'][name]=unreal.SkeletalMeshEditorSubsystem.regenerate_lod(mesh,3,False,False)
        lib.save_loaded_asset(mesh)
    definition=lib.load_asset(DEST+'/DA_Thunderhawk') if lib.does_asset_exist(DEST+'/DA_Thunderhawk') else None
    if not definition:
        factory=unreal.DataAssetFactory();factory.set_editor_property('data_asset_class',unreal.MaskVehicleDefinition)
        definition=assets.create_asset('DA_Thunderhawk',DEST,unreal.MaskVehicleDefinition,factory)
    parts=[];static_editor=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    for item in manifest['parts']:
        direct_path=DEST+'/'+item['name']
        mesh=lib.load_asset(direct_path) if lib.does_asset_exist(direct_path) else None
        if not mesh:
            # Legacy FBX may prefix the import destination name for a multi-mesh file.
            mesh=next((lib.load_asset(p) for p in report['imported'] if p.split('.')[-1].endswith(item['name'])),None)
        if not mesh:raise RuntimeError('Missing rigid part '+item['name'])
        assign_materials(mesh,item['name'],manifest['materials'])
        lods=unreal.StaticMeshReductionOptions()
        lods.set_editor_property('auto_compute_lod_screen_size',True)
        settings=[]
        for percent,screen in [(1.,1.),(.5,.45),(.2,.16)]:
            option=unreal.StaticMeshReductionSettings();option.set_editor_property('percent_triangles',percent);option.set_editor_property('screen_size',screen);settings.append(option)
        lods.set_editor_property('reduction_settings',settings);static_editor.set_lods(mesh,lods)
        static_editor.add_simple_collisions(mesh,unreal.ScriptingCollisionShapeType.BOX)
        part=unreal.MaskVehiclePart();part.set_editor_property('name',item['name']);part.set_editor_property('mesh',mesh)
        part.set_editor_property('wheel',item['wheel'])
        samples=[]
        for sample in item['samples']:
            t=unreal.Transform();t.translation=unreal.Vector(*sample['t']);t.rotation=unreal.Quat(*sample['q']);t.scale3d=unreal.Vector(*sample['s']);samples.append(t)
        part.set_editor_property('samples',samples);parts.append(part);lib.save_loaded_asset(mesh)
    definition.set_editor_property('parts',parts)
    for key,value in [('chassis',chassis),('driver',body),('hair',hair),('mask',mask)]:definition.set_editor_property(key,value)
    lib.save_loaded_asset(skeleton)
    animations=[lib.load_asset(DEST+'/AN_Matt_'+pose) for pose in ('Standing','Driving')]
    animations=[a for a in animations if isinstance(a,unreal.AnimSequence)]
    report['animations']=[a.get_path_name() for a in animations]
    for key,token in [('driving_pose','Driving'),('standing_pose','Standing')]:
        animation=next((a for a in animations if token.lower() in a.get_name().lower()),None)
        if not animation:raise RuntimeError('Missing baked animation '+token)
        definition.set_editor_property(key,animation)
    definition.set_editor_property('driver_location',unreal.Vector(*manifest['driver_location_cm']))
    lib.save_loaded_asset(definition)
    blueprint=lib.load_asset(DEST+'/BP_Thunderhawk') if lib.does_asset_exist(DEST+'/BP_Thunderhawk') else None
    if not blueprint:blueprint=lib.duplicate_asset('/Game/Blueprints/Pawns/BP_PlayerVehicle',DEST+'/BP_Thunderhawk')
    unreal.BlueprintEditorLibrary.reparent_blueprint(blueprint,unreal.ThunderhawkPawn)
    unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
    cdo=unreal.get_default_object(blueprint.generated_class());cdo.set_editor_property('definition',definition)
    # Original weapon, HUD, camera and engine settings are inherited from the copied BP.
    unreal.BlueprintEditorLibrary.compile_blueprint(blueprint);lib.save_loaded_asset(blueprint)
    report.update(passed=True,parts=len(parts),definition=definition.get_path_name(),blueprint=blueprint.get_path_name())
except Exception:
    report['error']=traceback.format_exc();unreal.log_error(report['error'])
finally:
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text(json.dumps(report,indent=2),encoding='utf-8')
    unreal.log_warning('MASK_IMPORT '+json.dumps({k:v for k,v in report.items() if k in ('passed','parts','error')}))
    if unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem):unreal.SystemLibrary.quit_editor()
