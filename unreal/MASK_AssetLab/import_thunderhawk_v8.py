"""Independent asset/Sequencer spike. No VehicularCombat code or content required."""
import unreal, json, math, traceback
from pathlib import Path
PROJECT=Path(unreal.Paths.project_dir())
ART=PROJECT.parents[1]/'art_source'/'Thunderhawk'
REPORT=PROJECT/'import_v8_result.json'
report={'static_import':'NOT_RUN','sequence_creation':'NOT_RUN','numeric_playback':'NOT_RUN','visual_viewer_review':'NOT_RUN'}
try:
    data=json.loads((ART/'exports'/'THK_V8_assembly.json').read_text(encoding='utf-8'))
    task=unreal.AssetImportTask(); task.filename=str(ART/'exports'/'THK_V8.fbx')
    task.destination_path='/Game/Thunderhawk_V8'; task.automated=True; task.replace_existing=True; task.save=True
    ui=unreal.FbxImportUI(); ui.import_as_skeletal=False; ui.import_animations=False
    ui.static_mesh_import_data.combine_meshes=False
    ui.static_mesh_import_data.transform_vertex_to_absolute=True
    task.options=ui
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    report['static_import']='EXECUTED'; report['imported_asset_paths']=list(task.imported_object_paths)
    unreal.EditorAssetLibrary.make_directory('/Game/Maps')
    levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not levels.new_level('/Game/Maps/THK_V8_AssetTest'): raise RuntimeError('Could not create neutral test level')
    actorsys=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    assets=unreal.AssetToolsHelpers.get_asset_tools()
    seqpath='/Game/Thunderhawk_V8/THK_V8_RoundTrip'
    seq=unreal.EditorAssetLibrary.load_asset(seqpath)
    if not seq: seq=assets.create_asset('THK_V8_RoundTrip','/Game/Thunderhawk_V8',unreal.LevelSequence,unreal.LevelSequenceFactoryNew())
    else:
        for old in seq.get_bindings(): old.remove()
    seq.set_display_rate(unreal.FrameRate(24,1)); seq.set_playback_start(0); seq.set_playback_end(193)
    actor_by_name={}; source_by_name={}; missing=[]; animated=0
    for item in data['objects']:
        name=item['name']; obj=unreal.EditorAssetLibrary.load_asset('/Game/Thunderhawk_V8/'+name)
        if not isinstance(obj,unreal.StaticMesh): missing.append(name); continue
        actor=actorsys.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0))
        actor.set_actor_label(name); actor.static_mesh_component.set_static_mesh(obj)
        actor.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
        actor_by_name[name]=actor; source_by_name[name]=item
        if item['animated']:
            animated+=1; binding=seq.add_possessable(actor)
            section=binding.add_track(unreal.MovieScene3DTransformTrack).add_section(); section.set_range(0,193)
            channels=list(section.get_all_channels())
            if len(channels)<9: raise RuntimeError('Transform channels missing for '+name)
            for sample in item['samples']:
                q=unreal.Quat(*sample['quaternion_xyzw']); rot=q.rotator()
                values=sample['translation']+[rot.roll,rot.pitch,rot.yaw]+sample['scale']
                for channel,value in zip(channels[:9],values):
                    channel.add_key(unreal.FrameNumber(sample['frame']),float(value),interpolation=unreal.MovieSceneKeyInterpolation.LINEAR)
    if missing: raise RuntimeError('Missing meshes: '+str(missing))
    report['mesh_actors']=len(actor_by_name); report['animated_bindings']=animated; report['sequence_creation']='EXECUTED'
    # Neutral viewing stage with built-in engine primitives.
    floor=actorsys.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,-3))
    floor.set_actor_label('AssetLab_Floor')
    floor.static_mesh_component.set_static_mesh(unreal.EditorAssetLibrary.load_asset('/Engine/BasicShapes/Plane'))
    floor.set_actor_scale3d(unreal.Vector(30,30,1))
    light=actorsys.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,500))
    light.set_actor_rotation(unreal.Rotator(-45,-30,0),False)
    actorsys.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,500))
    camera=actorsys.spawn_actor_from_class(unreal.CineCameraActor,unreal.Vector(650,-650,350))
    camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(camera.get_actor_location(),unreal.Vector(0,0,75)),False)
    camera.set_actor_label('AssetLab_Camera')
    unreal.EditorAssetLibrary.save_loaded_asset(seq)
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    player,player_actor=unreal.LevelSequencePlayer.create_level_sequence_player(world,seq,unreal.MovieSceneSequencePlaybackSettings())
    checks=[]
    for frame in (1,65,97,151,193):
        params=unreal.MovieSceneSequencePlaybackParams(time=(frame-1)/24.,position_type=unreal.MovieScenePositionType.TIME,update_method=unreal.UpdatePositionMethod.JUMP)
        player.set_playback_position(params)
        for name in ('THK_Wing_L','THK_Wing_R','THK_RearPanel','THK_RearStabilizer','THK_DoorCannon_L','THK_DoorCannon_R'):
            item=source_by_name[name]; expected=item['samples'][frame-1] if item['animated'] else item['samples'][0]
            transform=actor_by_name[name].get_actor_transform()
            loc=transform.translation; q=transform.rotation; scale=transform.scale3d
            error=math.sqrt(sum((a-b)**2 for a,b in zip((loc.x,loc.y,loc.z),expected['translation'])))
            dot=abs(sum(a*b for a,b in zip((q.x,q.y,q.z,q.w),expected['quaternion_xyzw'])))
            angle=math.degrees(2*math.acos(min(1.,max(-1.,dot))))
            scale_error=max(abs(a-b) for a,b in zip((scale.x,scale.y,scale.z),expected['scale']))
            checks.append({'blender_frame':frame,'object':name,'translation_error_cm':error,'rotation_error_deg':angle,'scale_error':scale_error})
    report['playback_checks']=checks
    report['numeric_playback']='PASS' if all(c['translation_error_cm']<.02 and c['rotation_error_deg']<.05 and c['scale_error']<1e-4 for c in checks) else 'FAIL'
    player.stop(); actorsys.destroy_actor(player_actor)
    for actor in actor_by_name.values(): actor.set_actor_transform(unreal.Transform(),False,True)
    levels.save_current_level()
    report['map']='/Game/Maps/THK_V8_AssetTest'; report['sequence']=seqpath
    report['note']='World-origin baked static meshes + sampled transform tracks; not a production skeletal asset or visual equivalence approval.'
except Exception as exc:
    report['error']=str(exc); report['traceback']=traceback.format_exc(); unreal.log_error(report['traceback'])
finally:
    REPORT.write_text(json.dumps(report,indent=2),encoding='utf-8')
    unreal.log_warning('THK_V8_RESULT '+json.dumps({k:v for k,v in report.items() if k in ['static_import','sequence_creation','numeric_playback','mesh_actors','animated_bindings','error']}))
