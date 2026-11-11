import bpy,json
from pathlib import Path
data={'frame':bpy.context.scene.frame_current,'file':bpy.data.filepath,'parts':[]}
for name in ['RH_MissileLauncherLift','RH_RearCabinetSlide','RH_RadarRotation']:
 o=bpy.data.objects[name];data['parts'].append({'name':name,'location':list(o.location),'drivers':[{'path':f.data_path,'index':f.array_index,'valid':f.driver.is_valid,'simple':f.driver.is_simple_expression,'expression':f.driver.expression,'variables':[(v.name,v.targets[0].id.name if v.targets[0].id else None,v.targets[0].data_path) for v in f.driver.variables]} for f in o.animation_data.drivers]})
Path('G:/DEV/mask-project-mayhem/docs/qa/rhino_v2_driver_state.json').write_text(json.dumps(data,indent=2));print(json.dumps(data))
