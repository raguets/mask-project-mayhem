"""Read-only saved spline mesh and ray evidence, independent of driving."""
import unreal,json
from pathlib import Path
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/MASK/Maps/SilentValley/L_SilentValley_Blockout')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();road=next(a for a in actors if isinstance(a,unreal.SilentValleyRoad))
report={'segments':[],'rays':[]}
for seg in list(road.get_editor_property('segments'))[:4]:
    report['segments'].append({'mesh':str(seg.get_editor_property('static_mesh')),'material':str(seg.get_material(0)),'visible':seg.is_visible(),'start':str(seg.get_start_position()),'end':str(seg.get_end_position()),'bounds':str(seg.get_local_bounds())})
for distance in (6000.,10000.,50000.,100000.,200000.,400000.):
    p=road.route_location(distance)
    hits=unreal.SystemLibrary.line_trace_multi(world,p+unreal.Vector(0,0,1000),p-unreal.Vector(0,0,1000),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,[],unreal.DrawDebugTrace.NONE,True)
    report['rays'].append({'distance':distance,'point':str(p),'hits':[str(h.to_tuple()) for h in hits]})
Path(unreal.Paths.project_dir(),'Saved/SilentValley/surface-probe.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
