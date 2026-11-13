import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Switchblade';out=A/'renders/independent_final';out.mkdir(exist_ok=True)
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
source=Path(bpy.data.filepath);report=[]
files={item['kind']:Path(item['file']) for item in json.loads((A/'standalone_validation.json').read_text())}
try:
 for name,file,pos,target,lens in [('viper',files['mask'],(1,-1,.55),(.02,0,.02),70),('miles',files['character'],(3,-3,1.9),(0,0,.94),56)]:
  bpy.ops.wm.open_mainfile(filepath=str(file));s=bpy.context.scene;c=s.camera;c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;s.render.resolution_x=1000;s.render.resolution_y=1000;s.cycles.samples=24;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);report.append({'asset':name,'source':str(file),'render':s.render.filepath,'actual_reopened':True})
finally:
 bpy.ops.wm.open_mainfile(filepath=str(source));(out/'manifest.json').write_text(json.dumps(report,indent=2))
print('INDEPENDENT_RENDER_REVIEW_COMPLETE')
