"""Read-only proof of persisted PCG instances and cosmetic collision policy."""
import unreal, json, math
from pathlib import Path

levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not levels.load_level('/Game/MASK/Maps/SilentValley/L_SilentValley_Blockout'):
    raise RuntimeError('Map reload failed')
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
road = next(a for a in actors if isinstance(a, unreal.SilentValleyRoad))
volume = next(a for a in actors if a.get_actor_label() == 'SV_Pinewood_Rocks_PCG')
components = volume.get_components_by_class(unreal.InstancedStaticMeshComponent)
report = {'passed': False, 'actor_count': len(actors), 'instances': 0, 'components': [],
          'method': 'Reload saved map in an independent editor process; no PCG generate request.'}
for c in components:
    count = c.get_instance_count()
    report['instances'] += count
    report['components'].append({'instances': count, 'mesh': c.get_editor_property('static_mesh').get_path_name(),
                                 'material': c.get_material(0).get_path_name(),
                                 'collision': str(c.get_collision_enabled()),
                                 'editor_only': c.get_editor_property('is_editor_only')})
report['checks'] = {
    'saved_39_instances': report['instances'] == 39,
    'no_decorative_collision': all(c.get_collision_enabled() == unreal.CollisionEnabled.NO_COLLISION for c in components),
    'available_in_game': all(not c.get_editor_property('is_editor_only') for c in components),
    'isolated_instanced_material': all(c.get_material(0).get_path_name().startswith('/Game/MASK/Environment/SilentValley/Materials/MI_SV_BeachRock_Instanced_') for c in components),
    'original_road_length': abs(road.route_length_cm()/100 - 9550.658125) < .1,
    'landscape_material': next(a for a in actors if isinstance(a, unreal.Landscape)).get_editor_property('landscape_material').get_name() == 'M_SV_ValleySurface_v2'
}
report['passed'] = all(report['checks'].values())
Path(unreal.Paths.project_dir(), 'Saved/SilentValley/showcase-01/reload.json').write_text(
    json.dumps(report, indent=2), encoding='utf-8')
if not report['passed']:
    raise RuntimeError('Persisted showcase validation failed: ' + str(report['checks']))
unreal.log('SV_SHOWCASE_RELOAD_VERIFIED')
