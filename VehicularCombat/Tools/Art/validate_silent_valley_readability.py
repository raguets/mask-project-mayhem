"""Independent persisted-level checks. Does not generate PCG or save assets."""
import unreal,json,math
from pathlib import Path
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not levels.load_level('/Game/MASK/Maps/SilentValley/L_SilentValley_Blockout'):raise RuntimeError('Reload failed')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
def find(label):return next(a for a in actors if a.get_actor_label()==label)
road=next(a for a in actors if isinstance(a,unreal.SilentValleyRoad))
landscape=next(a for a in actors if isinstance(a,unreal.Landscape))
pcg=find('SV_Pinewood_Rocks_PCG');instances=sum(c.get_instance_count() for c in pcg.get_components_by_class(unreal.InstancedStaticMeshComponent))
checks={'route_length_preserved':abs(road.route_length_cm()/100-9550.658125)<.1,
        'terrain_material_v4':landscape.get_editor_property('landscape_material').get_name()=='M_SV_ValleySurface_v4',
        'pcg_39_instances_preserved':instances==39,
        'fill_survives_capture_sun_rotation':unreal.Name('SV_AMBIENT_FILL') in find('SV_AmbientFill').tags,
        'fill_no_shadows':not find('SV_AmbientFill').light_component.get_editor_property('cast_shadows'),
        'ten_sign_posts':sum(a.get_actor_label().startswith('SV_SignPost_') for a in actors)==10}
checks['road_material_v3']=road.get_editor_property('road_material').get_name()=='M_SV_RoadMarked_v3'
checks['all_road_segments_material_v3']=all(c.get_material(0).get_name()=='M_SV_RoadMarked_v3' for c in road.get_editor_property('segments'))
checks['sun_priority_distinct']=all(a.light_component.get_editor_property('forward_shading_priority')==(0 if unreal.Name('SV_AMBIENT_FILL') in a.tags else 1) for a in actors if isinstance(a,unreal.DirectionalLight))
signs=[]
for cp in [a for a in actors if isinstance(a,unreal.SilentValleyCheckpoint)]:
    index=cp.get_editor_property('zone_index');name=cp.get_editor_property('zone_name')
    board=find('SV_Sign_'+str(index));front=find('SV_Label_'+name);back=find('SV_Label_Return_'+str(index))
    normal=board.get_actor_forward_vector()
    checks['sign_'+str(index)+'_front_aligned']=normal.dot(front.get_actor_forward_vector())>.999
    checks['sign_'+str(index)+'_back_aligned']=normal.dot(back.get_actor_forward_vector())<-.999
    checks['sign_'+str(index)+'_front_clear_of_board']=(front.get_actor_location()-board.get_actor_location()).dot(normal)>13
    checks['sign_'+str(index)+'_nonblocking']=board.static_mesh_component.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION
    signs.append({'name':name,'front':str(front.get_actor_location()),'back':str(back.get_actor_location())})
report={'passed':all(checks.values()),'checks':checks,'signs':signs,'pcg_instances':instances,'visual_validation':'separate rendered inspection required'}
out=Path(unreal.Paths.project_dir())/'Saved/SilentValley/readability-v1/reload.json'
out.write_text(json.dumps(report,indent=2),encoding='utf-8')
if not report['passed']:raise RuntimeError('Readability persistence validation failed '+str(checks))
