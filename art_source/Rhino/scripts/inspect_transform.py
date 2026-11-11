import bpy,json
from pathlib import Path
s=bpy.context.scene;r=bpy.data.objects['Rhino_Control'];out=[]
for frame in [1,91,151,241]:
 s.frame_set(frame);r.update_tag();bpy.context.view_layer.update();entry={'frame':frame,'properties':dict(r.items()),'parts':[]}
 for name in ['Rhino_RearVehicle_Root','RH_RearCockpitHatchPivot','RH_ExhaustCannonPivot_1','RH_BullbarSlide','RH_MissileLauncherLift']:
  ob=bpy.data.objects[name];entry['parts'].append({'name':name,'location':list(ob.location),'rotation':list(ob.rotation_euler),'drivers':[{'expression':f.driver.expression,'valid':f.driver.is_valid,'vars':[(v.name,v.targets[0].id.name,v.targets[0].data_path) for v in f.driver.variables]} for f in ob.animation_data.drivers]})
 out.append(entry)
Path('G:/DEV/mask-project-mayhem/docs/qa/rhino_transform_inspection.json').write_text(json.dumps(out,indent=2));s.frame_set(1);print(json.dumps(out))
