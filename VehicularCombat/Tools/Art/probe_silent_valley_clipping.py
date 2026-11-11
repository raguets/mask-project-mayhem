"""Read-only dense road/terrain clearance diagnostic on the saved level."""
import unreal,json,math
from pathlib import Path
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
levels.load_level('/Game/MASK/Maps/SilentValley/L_SilentValley_Blockout')
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
road=next(a for a in actors if isinstance(a,unreal.SilentValleyRoad))
land=next(a for a in actors if isinstance(a,unreal.Landscape))
samples=[];problems=[]
for d in range(10000,int(road.route_length_cm())-1000,1000):
    p=road.route_location(d);angle=math.radians(road.route_rotation(d).yaw)
    for offset in (-400,0,400):
        q=p+unreal.Vector(-math.sin(angle)*offset,math.cos(angle)*offset,0)
        hits=unreal.SystemLibrary.line_trace_multi(world,q+unreal.Vector(0,0,100000),q-unreal.Vector(0,0,100000),unreal.TraceTypeQuery.ECC_VISIBILITY,False,[road],unreal.DrawDebugTrace.NONE,True)
        h=next((h.to_tuple() for h in hits if isinstance(h.to_tuple()[9],unreal.LandscapeProxy)),None)
        if not h:continue
        item={'route_m':d/100,'offset_cm':offset,'clearance_cm':q.z-h[5].z}
        samples.append(item)
        if item['clearance_cm']<15:problems.append(item)
out=Path(unreal.Paths.project_dir())/'Saved/SilentValley/environment-v1/clipping.json'
out.write_text(json.dumps({'samples':len(samples),'minimum_clearance_cm':min(s['clearance_cm'] for s in samples),'under_15cm':problems},indent=2))
