"""Reproducible native scenery instances from preserved Quixel imports.
Keeps the existing 39-rock PCG layer. No collision/nav obstruction is added.
"""
import unreal,json,random,math,datetime,shutil,traceback
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());OUT=ROOT/'Saved/SilentValley/environment-v1';OUT.mkdir(parents=True,exist_ok=True)
MAP='/Game/MASK/Maps/SilentValley/L_SilentValley_Blockout';FOLDER='/Game/MASK/Environment/SilentValley/Materials'
editor=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
lib=unreal.EditorAssetLibrary;edit=unreal.MaterialEditingLibrary
report={'passed':False,'stage':'start','seed':1110,'collision':'Scenery instances have no collision/nav effect. Full-route/POI exclusions are precomputed; rerun after route edits.'}
def record(stage):
    report['stage']=stage;(OUT/'planting.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
try:
    backup=ROOT/'Saved/SilentValley/backups';backup.mkdir(exist_ok=True)
    shutil.copy2(ROOT/'Content/MASK/Maps/SilentValley/L_SilentValley_Blockout.umap',backup/('BeforePlanting-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.umap'))
    registry=unreal.AssetRegistryHelpers.get_asset_registry();registry.search_all_assets(True)
    registry.scan_paths_synchronous(['/Game/Megaplant_Library','/Game/Fab','/Game/MASK'],True,True)
    if not levels.load_level(MAP):raise RuntimeError('Map load failed')
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    road=next(a for a in editor.get_all_level_actors() if isinstance(a,unreal.SilentValleyRoad))
    exclusions=[a.get_actor_location() for a in editor.get_all_level_actors() if isinstance(a,(unreal.PlayerStart,unreal.SilentValleyCheckpoint))]
    buckets={}
    for d in range(0,int(road.route_length_cm()),400):
        q=road.route_location(d);buckets.setdefault((math.floor(q.x/10000),math.floor(q.y/10000)),[]).append(q)
    def distance(p):
        cx=math.floor(p.x/10000);cy=math.floor(p.y/10000)
        return min((math.hypot(p.x-q.x,p.y-q.y) for x in range(cx-1,cx+2) for y in range(cy-1,cy+2) for q in buckets.get((x,y),[])),default=1e9)
    def ground(p):
        hits=unreal.SystemLibrary.line_trace_multi(world,unreal.Vector(p.x,p.y,100000),unreal.Vector(p.x,p.y,-100000),unreal.TraceTypeQuery.ECC_VISIBILITY,False,[road],unreal.DrawDebugTrace.NONE,True)
        return next((h.to_tuple() for h in hits if isinstance(h.to_tuple()[9],unreal.LandscapeProxy)),None)
    def excluded(p,r):return any(math.hypot(p.x-q.x,p.y-q.y)<r for q in exclusions)
    rng=random.Random(1110);tree_points=[[] for _ in range(4)];grass_points=[[] for _ in range(8)];rock_points=[]
    def transform(p,scale,yaw,pitch=0,roll=0):
        t=unreal.Transform();t.translation=p;t.scale3d=unreal.Vector(scale,scale,scale);t.rotation=unreal.Rotator(pitch=pitch,yaw=yaw,roll=roll).quaternion();return t
    minimum_tree_clearance=1e9
    def tree(p):
        global minimum_tree_clearance
        dist=distance(p)
        if dist<2400 or excluded(p,6500):return
        h=ground(p)
        if not h or h[7].z<.72 or h[5].z<5520:return
        minimum_tree_clearance=min(minimum_tree_clearance,dist)
        tree_points[rng.randrange(4)].append(transform(h[5]-unreal.Vector(0,0,12),rng.uniform(.52,.9),rng.uniform(-180,180),rng.uniform(-1,1),rng.uniform(-1,1)))
    def grass(p):
        if distance(p)<760 or excluded(p,4000):return
        h=ground(p)
        if not h or h[7].z<.7:return
        if math.hypot((p.x+105000)/14000,(p.y+55000)/9000)<1.6 and h[5].z<5430:return
        grass_points[rng.randrange(8)].append(transform(h[5]-unreal.Vector(0,0,2),rng.uniform(.75,1.45),rng.uniform(-180,180)))
    record('projection')
    # Open groves along the approach, with varied depth rather than tree rows.
    for d in range(42000,165001,1000):
        p=road.route_location(d);yaw=math.radians(road.route_rotation(d).yaw);right=unreal.Vector(-math.sin(yaw),math.cos(yaw),0)
        for side in (-1,1):
            for _ in range(2):
                if rng.random()<.52:
                    tree(p+right*(side*rng.uniform(2800,15000))+unreal.Vector(rng.uniform(-1600,1600),rng.uniform(-1600,1600),0))
    # Sparse crowns around the lake leave clear vistas over the water.
    for _ in range(140):
        a=rng.uniform(0,math.tau);r=rng.uniform(1.5,2.8)
        tree(unreal.Vector(-105000+math.cos(a)*14000*r,-55000+math.sin(a)*9000*r,0))
    for d in range(50000,110001,150):
        p=road.route_location(d);yaw=math.radians(road.route_rotation(d).yaw);right=unreal.Vector(-math.sin(yaw),math.cos(yaw),0)
        for side in (-1,1):
            for _ in range(14):
                if rng.random()<.82:
                    grass(p+right*(side*rng.uniform(800,3500))+unreal.Vector(rng.uniform(-180,180),rng.uniform(-180,180),0))
    for _ in range(2800):
        a=rng.uniform(0,math.tau);r=rng.uniform(1.1,1.9)
        grass(unreal.Vector(-105000+math.cos(a)*14000*r,-55000+math.sin(a)*9000*r,0))
    rock=lib.load_asset('/Game/Fab/Megascans/3D/Small_Beach_Rock_wd4kfdx/Medium/wd4kfdx_tier_2/StaticMeshes/wd4kfdx_tier_2')
    box=rock.get_bounding_box();width=max(box.max.x-box.min.x,box.max.y-box.min.y,1)
    for _ in range(150):
        a=rng.uniform(0,math.tau);r=rng.uniform(.98,1.5);p=unreal.Vector(-105000+math.cos(a)*14000*r,-55000+math.sin(a)*9000*r,0)
        h=ground(p)
        if not h or h[7].z<.65 or not 5200<h[5].z<6100 or distance(p)<2000:continue
        radius=rng.uniform(60,280);s=2*radius/width
        rock_points.append(transform(h[5]-unreal.Vector(0,0,box.min.z*s+radius*.15),s,rng.uniform(-180,180),rng.uniform(-10,10),rng.uniform(-10,10)))
    # Copy material chains for their new instance usage; preserve Fab originals.
    material_cache={}
    def instanced_material(source,skinned=False):
        key=(source.get_path_name(),skinned)
        if key in material_cache:return material_cache[key]
        chain=[];master=source
        while isinstance(master,unreal.MaterialInstanceConstant):chain.append(master);master=master.get_editor_property('parent')
        suffix='_SK' if skinned else '_ISM';name='M_SV_Env_'+master.get_name()+suffix+'_v1'
        copied=lib.load_asset(FOLDER+'/'+name) if lib.does_asset_exist(FOLDER+'/'+name) else lib.duplicate_asset(master.get_path_name(),FOLDER+'/'+name)
        copied.set_editor_property('used_with_instanced_static_meshes',True)
        if skinned:copied.set_editor_property('used_with_instanced_skinned_mesh',True)
        edit.recompile_material(copied);lib.save_loaded_asset(copied,False)
        for item in reversed(chain):
            name='MI_SV_Env_'+item.get_name()+suffix+'_v1';target=FOLDER+'/'+name
            child=lib.load_asset(target) if lib.does_asset_exist(target) else lib.duplicate_asset(item.get_path_name(),target)
            edit.set_material_instance_parent(child,copied);edit.update_material_instance(child);lib.save_loaded_asset(child,False);copied=child
        material_cache[key]=copied;return copied
    groups=[]
    def place(label,mesh,transforms,skinned=False):
        if not transforms:return
        actor=unreal.SilentValleyEditorLibrary.place_scenery_instances(label,mesh,transforms)
        record('created_'+label)
        if not actor:raise RuntimeError('Instance actor rejected '+label)
        cls=unreal.InstancedSkinnedMeshComponent if skinned else unreal.HierarchicalInstancedStaticMeshComponent
        component=actor.get_component_by_class(cls)
        for i in range(component.get_num_materials()):
            record('material_'+label+'_'+str(i))
            original=component.get_material(i)
            if original:component.set_material(i,instanced_material(original,skinned))
        if component.get_instance_count()!=len(transforms):raise RuntimeError('Instance count mismatch '+label)
        if 'Rock' in label:component.set_cull_distances(25000,45000)
        groups.append({'actor':label,'mesh':mesh.get_path_name(),'count':len(transforms),'skinned':skinned})
    report.update(expected_trees=sum(map(len,tree_points)),expected_grass=sum(map(len,grass_points)),expected_shore_rocks=len(rock_points),nanite_features={n:unreal.SystemLibrary.get_console_variable_int_value(n) for n in ['r.Nanite.Foliage','r.Nanite.AllowAssemblies','r.Nanite.AllowVoxels']})
    record('trees')
    for index,variant in enumerate('ABCD'):
        record('loading_tree_'+variant)
        mesh=lib.load_asset('/Game/Megaplant_Library/Tree_Baltic_Pine/Tree_Baltic_Pine_01/Tree_Baltic_Pine_01_'+variant)
        if not mesh:raise RuntimeError('Tree source missing')
        record('placing_tree_'+variant)
        place('SV_Natural_Trees_'+variant,mesh,tree_points[index],True)
    record('grass')
    base='/Game/Fab/Megascans/Plants/Wild_Grass_vczndjqja/Medium/vczndjqja_tier_2/StaticMeshes/SM_vczndjqja_Var'
    for index,variant in enumerate('ABCDEFGH'):place('SV_Natural_Grass_'+variant,lib.load_asset(base+variant),grass_points[index])
    place('SV_Natural_Shore_Rocks',rock,rock_points)
    report.update(groups=groups,trees=sum(map(len,tree_points)),grass=sum(map(len,grass_points)),shore_rocks=len(rock_points),min_tree_center_road_distance_m=minimum_tree_clearance/100)
    if not levels.save_current_level():raise RuntimeError('Planting save failed')
    report['passed']=True;record('saved_visual_inspection_pending')
except Exception:
    report['error']=traceback.format_exc();record('error');raise
