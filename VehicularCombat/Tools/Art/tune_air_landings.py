"""User-requested faster direct return, with bounded-force flare retained."""
import unreal,json
from pathlib import Path
P=Path(unreal.Paths.project_dir()).resolve();out=[]
for name,speed in [('Thunderhawk',8.),('Raven',8.),('Condor',6.)]:
    definition=unreal.EditorAssetLibrary.load_asset('/Game/MASK/'+name+'/DA_'+name)
    if not definition:raise RuntimeError('Missing '+name)
    dynamics=definition.get_editor_property('dynamics');dynamics.set_editor_property('landing_descent_mps',speed)
    if name=='Condor':
        dynamics.set_editor_property('speed_command_rate_mps2',10.)
        dynamics.set_editor_property('maximum_pitch_degrees',22.)
        definition.set_editor_property('clearance_center',unreal.Vector(-30,0,150))
        definition.set_editor_property('clearance_extent',unreal.Vector(200,155,100))
    definition.set_editor_property('dynamics',dynamics);unreal.EditorAssetLibrary.save_loaded_asset(definition)
    out.append({'vehicle':name,'maximum_descent_mps':speed,'flight_model':str(dynamics.get_editor_property('flight_model'))})
(P/'Saved/Art/air-landing-tuning.json').write_text(json.dumps(out,indent=2))
definition=unreal.EditorAssetLibrary.load_asset('/Game/MASK/Condor/DA_Condor')
bounds=[]
for part in definition.get_editor_property('parts'):
    mesh=part.get_editor_property('mesh')
    box=mesh.get_bounding_box()
    bounds.append({'part':str(part.get_editor_property('name')),'min':str(box.min),'max':str(box.max)})
(P/'Saved/Art/condor-road-mesh-bounds.json').write_text(json.dumps(bounds,indent=2))
