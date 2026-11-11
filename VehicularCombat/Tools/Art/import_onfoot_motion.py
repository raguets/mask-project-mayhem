"""UE Python commandlet: import animation-only FBX onto the existing four skeletons."""
import unreal,json,traceback
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir()).resolve();SOURCE=ROOT/'SourceArt/MASK/OnFoot';DEST='/Game/MASK/OnFoot'
REPORT=ROOT/'Saved/Art/onfoot/import.json';report={'passed':False,'actors':[]}
tools=unreal.AssetToolsHelpers.get_asset_tools();lib=unreal.EditorAssetLibrary
profiles=[('Matt','Thunderhawk/SK_Matt','Thunderhawk/DA_Thunderhawk'),('Alex','Rhino/SK_Alex','Rhino/DA_Rhino'),('Bruce','Rhino/SK_Bruce','Rhino/DA_RhinoRear'),('Hondo','Hurricane/SK_Hondo','Hurricane/DA_Hurricane')]
try:
    unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
    for actor,mesh_path,definition_path in profiles:
        mesh=lib.load_asset('/Game/MASK/'+mesh_path);skeleton=mesh.get_editor_property('skeleton');definition=lib.load_asset('/Game/MASK/'+definition_path)
        manifest=json.loads((SOURCE/actor/'manifest.json').read_text(encoding='utf-8'));folder=DEST+'/'+actor;lib.make_directory(folder)
        animations=[];positions=[];jump=None;imported=[]
        for clip in manifest['clips']:
            name='AN_'+clip['name'];path=folder+'/'+name
            task=unreal.AssetImportTask();task.filename=str(SOURCE/actor/(clip['name']+'.fbx'));task.destination_path=folder;task.destination_name=name
            task.automated=True;task.replace_existing=True;task.save=True;task.factory=unreal.FbxFactory()
            options=unreal.FbxImportUI();options.automated_import_should_detect_type=False;options.import_as_skeletal=False;options.import_mesh=False;options.import_animations=True
            options.mesh_type_to_import=unreal.FBXImportType.FBXIT_ANIMATION;options.skeleton=skeleton;options.import_materials=False;options.import_textures=False
            options.anim_sequence_import_data.set_editor_property('animation_length',unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME)
            options.anim_sequence_import_data.set_editor_property('remove_redundant_keys',False)
            options.anim_sequence_import_data.set_editor_property('import_uniform_scale',1.)
            options.anim_sequence_import_data.set_editor_property('use_default_sample_rate',True);task.options=options
            tools.import_asset_tasks([task]);animation=lib.load_asset(path)
            if not isinstance(animation,unreal.AnimSequence):raise RuntimeError('Animation import missing: '+path+' / '+str(task.imported_object_paths))
            if animation.get_editor_property('skeleton')!=skeleton:raise RuntimeError('Wrong skeleton '+path)
            if not lib.save_loaded_asset(animation,False):raise RuntimeError('Animation save failed '+path)
            imported.append(path)
            if clip['name']=='Jump':jump=animation
            else:animations.append(animation);positions.append(unreal.Vector(clip['x'],clip['y'],0))
        blend=unreal.MaskAssetEditorLibrary.create_driver_locomotion(folder+'/BS_Locomotion',skeleton,animations,positions)
        if not blend or not lib.save_loaded_asset(blend,False):raise RuntimeError('Blend space build/save failed '+actor)
        definition.set_editor_property('driver_locomotion',blend);definition.set_editor_property('driver_jump',jump)
        if not lib.save_loaded_asset(definition,False):raise RuntimeError('Definition save failed '+actor)
        report['actors'].append({'actor':actor,'mesh':mesh.get_path_name(),'skeleton':skeleton.get_path_name(),'blend_space':blend.get_path_name(),'jump':jump.get_path_name(),'animations':imported})
    # Record the existing rifle contract without changing its geometry or materials.
    cls=unreal.load_class(None,'/Game/Blueprints/Pickups/Weapons/BP_Weapon_AssaultRifle.BP_Weapon_AssaultRifle_C')
    cdo=unreal.get_default_object(cls);components=cdo.get_components_by_class(unreal.SkeletalMeshComponent)
    report['weapon']=[{'component':c.get_name(),'mesh':c.get_skeletal_mesh_asset().get_path_name() if c.get_skeletal_mesh_asset() else None,'bounds_methods':[n for n in dir(c.get_skeletal_mesh_asset()) if 'bounds' in n.lower()]} for c in components]
    report['passed']=True
except Exception:
    report['error']=traceback.format_exc();unreal.log_error(report['error']);raise
finally:
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text(json.dumps(report,indent=2),encoding='utf-8')
