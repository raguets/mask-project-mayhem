"""Independent persisted-level validation; no generation or saving of assets."""
import unreal,json,math
from pathlib import Path
root=Path(unreal.Paths.project_dir());out=root/'Saved/SilentValley/environment-v1'
registry=unreal.AssetRegistryHelpers.get_asset_registry();registry.search_all_assets(True)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not levels.load_level('/Game/MASK/Maps/SilentValley/L_SilentValley_Blockout'):raise RuntimeError('Reload failed')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
def find(label):return next(a for a in actors if a.get_actor_label()==label)
road=next(a for a in actors if isinstance(a,unreal.SilentValleyRoad));terrain=next(a for a in actors if isinstance(a,unreal.Landscape))
water=find('SV_Lake_Surface_v1');cloud=find('SV_VolumetricClouds').get_component_by_class(unreal.VolumetricCloudComponent)
oldpcg=find('SV_Pinewood_Rocks_PCG');plant=json.loads((out/'planting.json').read_text(encoding='utf-8'))
checks={
 'route_length_preserved':abs(road.route_length_cm()/100-9550.658125)<.1,
 'road_material_preserved':road.get_editor_property('road_material').get_name()=='M_SV_RoadMarked_v3',
 'old_pcg_39_preserved':sum(c.get_instance_count() for c in oldpcg.get_components_by_class(unreal.InstancedStaticMeshComponent))==39,
 'terrain_natural_tag':unreal.Name('SV_NATURAL_TERRAIN_V1') in terrain.tags,
 'render_mips_rebuilt':unreal.Name('SV_RENDER_MIPS_V1') in terrain.tags,
 'terrain_material':terrain.get_editor_property('landscape_material').get_name()=='M_SV_NaturalTerrain_v1',
 'single_lake':sum(a.get_actor_label()=='SV_Lake_Surface_v1' for a in actors)==1,
 'water_nonblocking':water.static_mesh_component.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION,
 'water_single_layer': 'WATER' in str(water.static_mesh_component.get_material(0).get_editor_property('shading_model')),
 'cloud_layer':abs(cloud.get_editor_property('layer_bottom_altitude')-2.2)<.01 and cloud.get_editor_property('material') is not None,
 'five_objectives':sum(isinstance(a,unreal.SilentValleyCheckpoint) for a in actors)==5,
 'planting_report_passed':plant['passed']
}
checks['temporal_antialiasing']=unreal.SystemLibrary.get_console_variable_int_value('r.AntiAliasingMethod')==4
checks['terrain_lod_cap']=terrain.get_editor_property('max_lod_level')==2
exposure=find('SV_EnvironmentExposure_v1').get_editor_property('settings')
checks['physical_luminance_histogram']=exposure.get_editor_property('histogram_log_max')>=16 and exposure.get_editor_property('auto_exposure_max_brightness')>=10000
checks['daylight_intensity']=find('SV_Sun').light_component.get_editor_property('intensity')==75000
checks['water_v2']=water.static_mesh_component.get_material(0).get_name()=='M_SV_LakeWater_v2'
vista=json.loads((out/'vistas.json').read_text(encoding='utf-8'))
checks['vistas_report_passed']=vista['passed']
backdrop=find('SV_Distant_Ridges_v1').static_mesh_component
checks['distant_ridges_nonblocking']=backdrop.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION
checks['distant_ridges_material']=backdrop.get_material(0).get_name()=='M_SV_DistantTerrain_v1' and not backdrop.get_material(0).get_editor_property('two_sided')
checks['distant_ridges_mesh']=backdrop.static_mesh.get_name()=='SM_SV_DistantTerrain_v2'
groups=[]
for expected in plant['groups']+vista['groups']:
    actor=find(expected['actor']);cls=unreal.InstancedSkinnedMeshComponent if expected['skinned'] else unreal.HierarchicalInstancedStaticMeshComponent
    component=actor.get_component_by_class(cls);count=component.get_instance_count()
    checks[expected['actor']+'_count']=count==expected['count']
    checks[expected['actor']+'_nonblocking']=component.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION
    groups.append({'actor':expected['actor'],'count':count,'skinned':expected['skinned']})
checks['514_trees']=sum(g['count'] for g in groups if g['skinned'])==514
def height(x,y):
    hits=unreal.SystemLibrary.line_trace_multi(world,unreal.Vector(x,y,100000),unreal.Vector(x,y,-100000),unreal.TraceTypeQuery.ECC_VISIBILITY,False,[road],unreal.DrawDebugTrace.NONE,True)
    hit=next((h.to_tuple() for h in hits if isinstance(h.to_tuple()[9],unreal.LandscapeProxy)),None)
    if not hit:raise RuntimeError('Missing lake bed/shore landscape')
    return hit[5].z
bed=height(-105000,-55000);checks['actual_basin_under_water']=500<5400-bed<750
shore=[height(-105000+math.cos(i*math.tau/8)*14000*1.3,-55000+math.sin(i*math.tau/8)*9000*1.3) for i in range(8)]
checks['eight_shore_samples_above_water']=all(z>5400 for z in shore)
report={'passed':all(checks.values()),'checks':checks,'groups':groups,'lake_depth_m':(5400-bed)/100,'shore_z_cm':shore,'visual_inspection':'separate rendered gate; this is structural validation only'}
(out/'reload.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
if not report['passed']:raise RuntimeError('Persisted environment check failed: '+str(checks))
