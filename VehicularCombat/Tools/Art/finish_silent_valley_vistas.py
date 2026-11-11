"""Interpreted Colorado backdrop and denser open Pinewood groves.
Preserve the original 298 trees, playable heightfield, roads and POIs.
"""
import unreal,json,random,math,datetime,shutil
from pathlib import Path
root=Path(unreal.Paths.project_dir());out=root/'Saved/SilentValley/environment-v1'
shutil.copy2(root/'Content/MASK/Maps/SilentValley/L_SilentValley_Blockout.umap',root/'Saved/SilentValley/backups'/('BeforeVistas-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.umap'))
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
registry=unreal.AssetRegistryHelpers.get_asset_registry();registry.search_all_assets(True)
if not levels.load_level('/Game/MASK/Maps/SilentValley/L_SilentValley_Blockout'):raise RuntimeError('Load failed')
editor=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors=editor.get_all_level_actors()
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
road=next(a for a in actors if isinstance(a,unreal.SilentValleyRoad))
land=next(a for a in actors if isinstance(a,unreal.Landscape))
if unreal.Name('SV_RENDER_MIPS_V1') not in land.tags:raise RuntimeError('Repair render mips first')
lib=unreal.EditorAssetLibrary
folder='/Game/MASK/Environment/SilentValley/Terrain';lib.make_directory(folder)
path=folder+'/SM_SV_DistantTerrain_v2'
mesh=lib.load_asset(path) if lib.does_asset_exist(path) else unreal.SilentValleyEditorLibrary.create_distant_terrain(path)
if not mesh or not lib.save_loaded_asset(mesh,False):raise RuntimeError('Backdrop creation/save failed')
label='SV_Distant_Ridges_v1';backdrop=next((a for a in actors if a.get_actor_label()==label),None)
if not backdrop:
    backdrop=editor.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,0))
    backdrop.set_actor_label(label);backdrop.tags=[unreal.Name('SV_GENERATED'),unreal.Name('SV_ENVIRONMENT_V1')]
backdrop.static_mesh_component.set_static_mesh(mesh)
material_path='/Game/MASK/Environment/SilentValley/Materials/M_SV_DistantTerrain_v1'
material=lib.load_asset(material_path) if lib.does_asset_exist(material_path) else lib.duplicate_asset('/Game/MASK/Environment/SilentValley/Materials/M_SV_NaturalTerrain_v1',material_path)
material.set_editor_property('two_sided',False)
unreal.MaterialEditingLibrary.recompile_material(material)
if not lib.save_loaded_asset(material,False):raise RuntimeError('Backdrop material save failed')
backdrop.set_actor_location(unreal.Vector(),False,True)
backdrop.set_actor_rotation(unreal.Rotator(),False)
backdrop.set_actor_scale3d(unreal.Vector(1,1,1))
backdrop.static_mesh_component.set_material(0,material)
backdrop.static_mesh_component.set_collision_profile_name('NoCollision')
backdrop.static_mesh_component.set_cast_shadow(False)
backdrop.static_mesh_component.set_editor_property('can_ever_affect_navigation',False)

route=[road.route_location(d) for d in range(0,int(road.route_length_cm()),400)]
pois=[a.get_actor_location() for a in actors if isinstance(a,(unreal.PlayerStart,unreal.SilentValleyCheckpoint))]
rng=random.Random(11112026);points=[[] for _ in range(4)];minimum=1e9;centers=[]
for d in range(50000,140001,500):
    p=road.route_location(d);angle=math.radians(road.route_rotation(d).yaw)
    for side in (-1,1):
        if rng.random()>.72:continue
        offset=side*rng.uniform(3000,8500)
        q=p+unreal.Vector(-math.sin(angle)*offset+rng.uniform(-1600,1600),math.cos(angle)*offset+rng.uniform(-1600,1600),0)
        clearance=min(math.hypot(q.x-r.x,q.y-r.y) for r in route)
        if clearance<2600 or any(math.hypot(q.x-r.x,q.y-r.y)<6500 for r in pois):continue
        if any(math.hypot(q.x-r.x,q.y-r.y)<500 for r in centers):continue
        hits=unreal.SystemLibrary.line_trace_multi(world,q+unreal.Vector(0,0,100000),q-unreal.Vector(0,0,100000),unreal.TraceTypeQuery.ECC_VISIBILITY,False,[road],unreal.DrawDebugTrace.NONE,True)
        hit=next((h.to_tuple() for h in hits if isinstance(h.to_tuple()[9],unreal.LandscapeProxy)),None)
        if not hit or hit[7].z<.74:continue
        transform=unreal.Transform();transform.translation=hit[5]-unreal.Vector(0,0,12)
        scale=rng.uniform(.65,1.05);transform.scale3d=unreal.Vector(scale,scale,scale)
        transform.rotation=unreal.Rotator(yaw=rng.uniform(-180,180)).quaternion()
        points[rng.randrange(4)].append(transform);minimum=min(minimum,clearance);centers.append(q)
groups=[]
for i,variant in enumerate('ABCD'):
    if not points[i]:raise RuntimeError('Empty grove group')
    tree=lib.load_asset('/Game/Megaplant_Library/Tree_Baltic_Pine/Tree_Baltic_Pine_01/Tree_Baltic_Pine_01_'+variant)
    actor=unreal.SilentValleyEditorLibrary.place_scenery_instances('SV_Natural_Grove_'+variant,tree,points[i])
    if not actor:raise RuntimeError('Grove placement failed')
    component=actor.get_component_by_class(unreal.InstancedSkinnedMeshComponent)
    original=next(a for a in actors if a.get_actor_label()=='SV_Natural_Trees_'+variant).get_component_by_class(unreal.InstancedSkinnedMeshComponent)
    for slot in range(original.get_num_materials()):component.set_material(slot,original.get_material(slot))
    if component.get_instance_count()!=len(points[i]):raise RuntimeError('Grove count mismatch')
    groups.append({'actor':actor.get_actor_label(),'count':len(points[i]),'skinned':True})
if not levels.save_current_level():raise RuntimeError('Map save failed')
(out/'vistas.json').write_text(json.dumps({'passed':True,'interpretation':'Colorado reference interpreted as a non-playable distant terrain ring, estimated extents2–8km; preserved original source heightfield','backdrop_mesh':mesh.get_path_name(),'backdrop_collision':str(backdrop.static_mesh_component.get_collision_enabled()),'original_trees_preserved':298,'additional_trees':sum(map(len,points)),'min_new_tree_road_sample_distance_m':minimum/100,'groups':groups,'visual_validation':'pending rendered inspection'},indent=2),encoding='utf-8')
