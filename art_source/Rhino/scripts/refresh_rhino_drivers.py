import bpy,json,re
from pathlib import Path
s=bpy.context.scene;r=bpy.data.objects['Rhino_Control'];out=[]
for ob in s.objects:
 if ob.animation_data:
  for f in ob.animation_data.drivers:
   if any(t.id==r for v in f.driver.variables for t in v.targets):
    expression=re.sub(r'(?<![0-9A-Za-z_])\.(\d)',r'0.\1',f.driver.expression)
    f.driver.expression=expression+' + 0.0';f.mute=False;ob.update_tag()
for frame in [1,151,241]:
 s.frame_set(frame);r.update_tag();bpy.context.view_layer.update()
 out.append({'frame':frame,'battle':r['battle_mode'],'parts':[{ 'name':ob.name,'location':list(ob.location),'rotation':list(ob.rotation_euler),'drivers':[{'valid':f.driver.is_valid,'simple':f.driver.is_simple_expression,'expression':f.driver.expression} for f in ob.animation_data.drivers]} for ob in s.objects if ob.animation_data and any(t.id==r for f in ob.animation_data.drivers for v in f.driver.variables for t in v.targets)]})
Path('G:/DEV/mask-project-mayhem/docs/qa/rhino_driver_refresh.json').write_text(json.dumps(out,indent=2));s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True);print(json.dumps(out))
