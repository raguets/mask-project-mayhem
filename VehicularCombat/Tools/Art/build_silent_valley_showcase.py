"""G3 first 500 m rock layer, using the owner's existing Fab import.

Run with UnrealEditor -ExecCmds="py <absolute script path>": PCG needs editor
ticks after the script returns. -ExecutePythonScript exits too soon. The graph
remains editable; points are rebuilt from the road by
this script after route changes. No vegetation asset or licence is acquired.
"""
import unreal, json, random, math, shutil, datetime, time, traceback
from pathlib import Path

ROOT = Path(unreal.Paths.project_dir()).resolve()
OUT = ROOT / 'Saved/SilentValley/showcase-01'
OUT.mkdir(parents=True, exist_ok=True)
MAP = '/Game/MASK/Maps/SilentValley/L_SilentValley_Blockout'
FOLDER = '/Game/MASK/Environment/SilentValley/PCG'
GRAPH = FOLDER + '/PCG_SV_PinewoodRocks_v1'
ROCK = '/Game/Fab/Megascans/3D/Small_Beach_Rock_wd4kfdx/Medium/wd4kfdx_tier_2/StaticMeshes/wd4kfdx_tier_2'
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assets = unreal.AssetToolsHelpers.get_asset_tools()
lib = unreal.EditorAssetLibrary
report = {'passed': False, 'stage': 'start', 'asset': ROCK,
          'scope': '500 m, rocks only; trees/grass/photorealistic pass incomplete',
          'route_interval_m': [500, 1000], 'seed': 1108}

def record():
    (OUT / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')

def fail():
    report['error'] = traceback.format_exc()
    record()
    unreal.log_error(report['error'])
    unreal.SystemLibrary.quit_editor()

try:
    backup = ROOT / 'Saved/SilentValley/backups'
    backup.mkdir(exist_ok=True)
    shutil.copy2(ROOT / 'Content/MASK/Maps/SilentValley/L_SilentValley_Blockout.umap',
                 backup / ('BeforeShowcase-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '.umap'))
    if not levels.load_level(MAP):
        raise RuntimeError('Cannot load isolated Silent Valley map')
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    registry.scan_paths_synchronous(['/Game/Fab', '/Game/MASK'], True, True)
    rock = unreal.load_asset(ROCK)
    if not rock:
        raise RuntimeError('Existing owner-imported rock unavailable; no replacement download')
    # PCG uses ISM components. The imported Fab master lacks that usage flag.
    # Copy its complete parent chain into our namespace instead of changing
    # the owner's imported master (which may be shared by other assets).
    original_material = rock.get_editor_property('static_materials')[0].material_interface
    chain, parent = [], original_material
    while isinstance(parent, unreal.MaterialInstanceConstant):
        chain.append(parent)
        parent = parent.get_editor_property('parent')
    if not isinstance(parent, unreal.Material):
        raise RuntimeError('Unsupported rock material hierarchy')
    material_folder = '/Game/MASK/Environment/SilentValley/Materials'
    master_name = 'M_SV_BeachRock_Instanced_v1'
    master = unreal.load_asset(material_folder + '/' + master_name)
    if not master:
        master = assets.duplicate_asset(master_name, material_folder, parent)
    master.set_editor_property('used_with_instanced_static_meshes', True)
    unreal.MaterialEditingLibrary.recompile_material(master)
    lib.save_loaded_asset(master, False)
    rock_material = master
    for index, source_material in enumerate(reversed(chain)):
        name = 'MI_SV_BeachRock_Instanced_' + str(index) + '_v1'
        instance = unreal.load_asset(material_folder + '/' + name)
        if not instance:
            instance = assets.duplicate_asset(name, material_folder, source_material)
        unreal.MaterialEditingLibrary.set_material_instance_parent(instance, rock_material)
        unreal.MaterialEditingLibrary.update_material_instance(instance)
        lib.save_loaded_asset(instance, False)
        rock_material = instance
    report['instanced_material'] = rock_material.get_path_name()
    road = next(a for a in actors.get_all_level_actors() if isinstance(a, unreal.SilentValleyRoad))
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    rng = random.Random(1108)
    bounds = rock.get_bounding_box()
    width = max(bounds.max.x - bounds.min.x, bounds.max.y - bounds.min.y, 1)
    all_route = [road.route_location(d) for d in range(0, int(road.route_length_cm()), 500)]
    exclusions = [a.get_actor_location() for a in actors.get_all_level_actors()
                  if isinstance(a, (unreal.PlayerStart, unreal.SilentValleyCheckpoint))]
    points, locations = [], []
    min_clearance = float('inf')
    # Sparse, reproducible candidates on both verges. Check distance to the
    # WHOLE road (including return legs), not just the sampled local tangent.
    for distance in range(50000, 100001, 1250):
        center = road.route_location(distance)
        yaw = math.radians(road.route_rotation(distance).yaw)
        right = unreal.Vector(-math.sin(yaw), math.cos(yaw), 0)
        for side in (-1, 1):
            if rng.random() < .38:
                continue
            lateral = side * rng.uniform(1400, 4200)
            p = center + right * lateral
            radius = rng.uniform(45, 145)
            clearance = min(math.hypot(p.x-q.x, p.y-q.y) for q in all_route) - radius
            if clearance < 1000 or any(math.hypot(p.x-q.x, p.y-q.y) < 4500 + radius for q in exclusions):
                continue
            hits = unreal.SystemLibrary.line_trace_multi(
                world, p + unreal.Vector(0, 0, 50000), p - unreal.Vector(0, 0, 50000),
                unreal.TraceTypeQuery.ECC_VISIBILITY, False, [], unreal.DrawDebugTrace.NONE, True)
            hit = next((h.to_tuple() for h in hits if isinstance(h.to_tuple()[9], unreal.LandscapeProxy)), None)
            if not hit or hit[7].z < .8:
                continue
            scale = radius * 2 / width
            location = hit[5] - unreal.Vector(0, 0, bounds.min.z * scale + radius * .12)
            transform = unreal.Transform()
            transform.translation = location
            transform.rotation = unreal.Rotator(pitch=rng.uniform(-8, 8), yaw=rng.uniform(-180, 180), roll=rng.uniform(-8, 8)).quaternion()
            transform.scale3d = unreal.Vector(scale, scale, scale)
            point = unreal.PCGPoint()
            point.transform = transform
            point.density = 1
            point.seed = rng.randrange(1, 1000000)
            points.append(point)
            locations.append([location.x, location.y, location.z])
            min_clearance = min(min_clearance, clearance)
    if not points:
        raise RuntimeError('No landscape-projected candidates survived exclusions')
    graph = unreal.load_asset(GRAPH)
    new_graph = graph is None
    if new_graph:
        graph = assets.create_asset('PCG_SV_PinewoodRocks_v1', FOLDER, unreal.PCGGraph, unreal.PCGGraphFactory())
        graph.set_editor_property('description', '500 m sparse rocks. Re-run source script after route edits. Road + spawn + checkpoint exclusions are precomputed, not a live spline filter.')
        source, settings = graph.add_node_of_type(unreal.PCGCreatePointsSettings)
        sink, spawner = graph.add_node_of_type(unreal.PCGStaticMeshSpawnerSettings)
    else:
        if not str(graph.get_editor_property('description')).startswith('500 m sparse rocks.'):
            raise RuntimeError('Preserving graph with unrecognized ownership description')
        nodes = list(graph.get_editor_property('nodes'))
        source = next(n for n in nodes if isinstance(n.get_settings(), unreal.PCGCreatePointsSettings))
        sink = next(n for n in nodes if isinstance(n.get_settings(), unreal.PCGStaticMeshSpawnerSettings))
        settings, spawner = source.get_settings(), sink.get_settings()
    settings.set_editor_property('points_to_create', points)
    settings.set_editor_property('coordinate_space', unreal.PCGCoordinateSpace.WORLD)
    spawner.set_editor_property('synchronous_load', True)
    selector = spawner.get_editor_property('mesh_selector_parameters')
    descriptor = unreal.PCGSoftISMComponentDescriptor()
    descriptor.set_editor_property('static_mesh', rock)
    descriptor.set_editor_property('override_materials', [rock_material])
    descriptor.set_editor_property('instance_start_cull_distance', 20000)
    descriptor.set_editor_property('instance_end_cull_distance', 35000)
    descriptor.set_editor_property('component_tags', [unreal.Name('SV_SHOWCASE_ROCK')])
    descriptor.set_editor_property('use_default_collision', False)
    body = descriptor.get_editor_property('body_instance')
    body.set_editor_property('collision_enabled', unreal.CollisionEnabled.NO_COLLISION)
    descriptor.set_editor_property('body_instance', body)
    entry = unreal.PCGMeshSelectorWeightedEntry()
    entry.set_editor_property('descriptor', descriptor)
    entry.set_editor_property('weight', 1)
    selector.set_editor_property('mesh_entries', [entry])
    if new_graph:
        if not graph.add_edge(source, 'Out', sink, 'In'):
            raise RuntimeError('PCG point-to-spawner edge failed')
        graph.add_edge(sink, 'Out', graph.get_output_node(), 'Out')
    if not lib.save_loaded_asset(graph, False):
        raise RuntimeError('PCG graph save failed')
    actor = next((a for a in actors.get_all_level_actors() if a.get_actor_label() == 'SV_Pinewood_Rocks_PCG'), None)
    if actor and unreal.Name('SV_SHOWCASE') not in actor.tags:
        raise RuntimeError('Refusing to edit untagged existing PCG actor')
    if not actor:
        actor = actors.spawn_actor_from_class(unreal.PCGVolume, unreal.Vector(0, 0, 0))
        actor.set_actor_label('SV_Pinewood_Rocks_PCG')
        actor.tags = [unreal.Name('SV_GENERATED'), unreal.Name('SV_SHOWCASE')]
    component = actor.get_editor_property('pcg_component')
    component.set_editor_property('generation_trigger', unreal.PCGComponentGenerationTrigger.GENERATE_ON_DEMAND)
    component.set_graph(graph)
    # A previous generation may still contain exactly 39 instances. Clear it
    # first, otherwise a count-only poll can save before the new graph runs.
    component.cleanup_local(True)
    phase = 'cleaning'
    started = time.monotonic()
    report.update(stage='cleaning', expected_instances=len(points), min_road_edge_clearance_m=(min_clearance-500)/100,
                  point_locations_cm=locations, graph=GRAPH)
    record()

    def tick(_delta):
        global handle, phase
        try:
            instances = list(actor.get_components_by_class(unreal.InstancedStaticMeshComponent))
            count = sum(c.get_instance_count() for c in instances)
            if phase == 'cleaning' and count == 0:
                phase = 'generating'
                component.generate(True)
                report['stage'] = phase
                record()
                return
            correct_material = all(c.get_material(0) == rock_material for c in instances if c.get_instance_count())
            if phase == 'generating' and count == len(points) and correct_material and not component.get_editor_property('generation_in_progress'):
                # Saving pumps Slate events. Unregister before saving to prevent
                # recursive calls trying to save a package already being saved.
                unreal.unregister_slate_post_tick_callback(handle)
                if not levels.save_current_level():
                    raise RuntimeError('Cannot save generated level')
                report.update(passed=True, stage='saved', generated_instances=count,
                              elapsed_seconds=time.monotonic()-started)
                record()
                unreal.SystemLibrary.quit_editor()
            elif time.monotonic()-started > 120:
                raise RuntimeError('PCG generation timeout, actual instances=' + str(count))
        except Exception:
            unreal.unregister_slate_post_tick_callback(handle)
            fail()
    handle = unreal.register_slate_post_tick_callback(tick)
except Exception:
    fail()
