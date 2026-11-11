"""Isolated blockout limits. No changes to vehicle movement or original maps.
Invisible static barriers at the Landscape perimeter and 2 km ceiling; these
are prototype world limits, not finished scenery or a tested flight encounter.
"""
import unreal, json, shutil, datetime
from pathlib import Path

root = Path(unreal.Paths.project_dir())
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
editor = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
backup = root / 'Saved/SilentValley/backups'
backup.mkdir(parents=True, exist_ok=True)
shutil.copy2(root / 'Content/MASK/Maps/SilentValley/L_SilentValley_Blockout.umap',
             backup / ('BeforeLimits-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '.umap'))
if not levels.load_level('/Game/MASK/Maps/SilentValley/L_SilentValley_Blockout'):
    raise RuntimeError('Cannot load isolated map')
cube = unreal.load_asset('/Engine/BasicShapes/Cube')
specs = {
    'SV_Limit_West': ((-201600, 0, 50000), (1000, 404200, 300000)),
    'SV_Limit_East': ((201600, 0, 50000), (1000, 404200, 300000)),
    'SV_Limit_South': ((0, -201600, 50000), (404200, 1000, 300000)),
    'SV_Limit_North': ((0, 201600, 50000), (404200, 1000, 300000)),
    'SV_Limit_Ceiling': ((0, 0, 200000), (404200, 404200, 1000)),
}
boundaries = {}
for name, (position, size) in specs.items():
    actor = next((a for a in editor.get_all_level_actors() if a.get_actor_label() == name), None)
    if actor and unreal.Name('SV_G2_LIMIT') not in actor.tags:
        raise RuntimeError('Refusing untagged actor: ' + name)
    if not actor:
        actor = editor.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*position))
    actor.set_actor_label(name)
    actor.tags = [unreal.Name('SV_GENERATED'), unreal.Name('SV_G2_LIMIT')]
    actor.set_actor_location(unreal.Vector(*position), False, True)
    actor.set_actor_scale3d(unreal.Vector(*(v / 100 for v in size)))
    actor.static_mesh_component.set_static_mesh(cube)
    actor.static_mesh_component.set_collision_profile_name('BlockAll')
    actor.set_actor_hidden_in_game(True)
    boundaries[name] = actor
if not levels.save_current_level():
    raise RuntimeError('Cannot save map limits')
# Newly spawned editor bodies may still have deferred physics registration.
# Reload the saved map before testing the collision that a game will load.
if not levels.load_level('/Game/MASK/Maps/SilentValley/L_SilentValley_Blockout'):
    raise RuntimeError('Cannot reload saved map limits')
boundaries = {a.get_actor_label(): a for a in editor.get_all_level_actors() if a.get_actor_label() in specs}
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
report = {'passed': False, 'checks': [], 'method': 'Editor collision rays against each isolated barrier; not manual flight/driving validation.',
          'inner_boundary_m': 2011, 'ceiling_m': 1995, 'placeholder': True}
all_actors = list(editor.get_all_level_actors())
for name, actor in boundaries.items():
    ignore = [a for a in all_actors if a != actor]
    direction = {'West': (-1, 0), 'East': (1, 0), 'South': (0, -1), 'North': (0, 1)}
    rays = [(unreal.Vector(0, 0, 190000), unreal.Vector(0, 0, 205000))] if name.endswith('Ceiling') else [
        (unreal.Vector(x * 190000, y * 190000, z), unreal.Vector(x * 205000, y * 205000, z))
        for z in (10000, 100000, 180000) for x, y in [direction[name.split('_')[-1]]]]
    for start, end in rays:
        hits = unreal.SystemLibrary.line_trace_multi(world, start, end, unreal.TraceTypeQuery.ECC_VISIBILITY,
                                                     False, ignore, unreal.DrawDebugTrace.NONE, True)
        hit = next((h.to_tuple() for h in (hits or []) if h.to_tuple()[9] == actor), None)
        report['checks'].append({'actor': name, 'start_z_cm': start.z, 'blocked': hit is not None})
report['passed'] = all(c['blocked'] for c in report['checks'])
(root / 'Saved/SilentValley/boundary-probes.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
if not report['passed']:
    raise RuntimeError('Boundary collision ray failed')
unreal.log('SV_BOUNDARY_RAYS_VERIFIED')
