"""Read-only introspection of the installed PCG Python API before authoring G3."""
import unreal, json
from pathlib import Path

names = ('PCGGraph', 'PCGGraphFactory', 'PCGCreatePointsSettings', 'PCGPoint',
         'PCGStaticMeshSpawnerSettings', 'PCGMeshSelectorWeighted',
         'PCGMeshSelectorWeightedEntry', 'PCGSoftISMComponentDescriptor',
         'PCGVolume', 'PCGComponent')
result = {}
for name in names:
    cls = getattr(unreal, name, None)
    entry = {'available': cls is not None, 'documentation': str(getattr(cls, '__doc__', ''))}
    if cls:
        entry['methods'] = {method: str(getattr(cls, method).__doc__) for method in dir(cls)
                            if any(token in method for token in ('add_node', 'add_edge', 'generate', 'set_graph', 'get_output', 'get_input'))}
    result[name] = entry
Path(unreal.Paths.project_dir(), 'Saved/SilentValley/pcg-python-api.json').write_text(
    json.dumps(result, indent=2), encoding='utf-8')
unreal.log('SV_PCG_API_INSPECTED')
