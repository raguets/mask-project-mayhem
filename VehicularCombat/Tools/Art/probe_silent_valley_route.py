"""Read-only transforms from the saved map and the actual spline."""
import unreal,json
from pathlib import Path
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/MASK/Maps/SilentValley/L_SilentValley_Blockout')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();road=next(a for a in actors if isinstance(a,unreal.SilentValleyRoad))
report={'starts':[{'name':a.get_actor_label(),'location':str(a.get_actor_location()),'rotation':str(a.get_actor_rotation())} for a in actors if isinstance(a,unreal.PlayerStart)],'route':[{'distance':d,'location':str(road.route_location(d)),'rotation':str(road.route_rotation(d))} for d in (0.,1.,100.,650.,1300.,2600.)]}
Path(unreal.Paths.project_dir(),'Saved/SilentValley/route-transforms.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
