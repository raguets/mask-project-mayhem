import bpy,json
from pathlib import Path
from mathutils import Vector
s=bpy.context.scene;p=Path('G:/DEV/mask-project-mayhem/art_source/Thunderhawk/renders/v10');p.mkdir(parents=True,exist_ok=True)
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True
try:
 pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='OPTIX';pref.get_devices()
 for d in pref.devices:d.use=d.type!='CPU'
 s.cycles.device='GPU'
except Exception:pass
s.render.resolution_x=1100;s.render.resolution_y=900;s.render.resolution_percentage=100
views=[('driver',(.9,1.75,1.4),(-.15,.4,.84),97,True),('mask',(.6,1.0,1.25),(-.34,.4,1.10),97,True),('flight',(5,5,3),(0,0,.75),97,False),('reactors',(-4,2,1.3),(-2.1,0,.48),97,False)]
for name,loc,target,fr,isolate in views:
 s.frame_set(fr)
 for ob in bpy.data.collections['THK9_Exterior'].objects:ob.hide_render=isolate
 if isolate:bpy.data.objects['Review_Floor'].hide_render=True
 else:bpy.data.objects['Review_Floor'].hide_render=False
 c=s.camera;c.location=loc;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='PERSP';c.data.lens=55 if name!='mask' else 70
 s.render.filepath=str(p/(name+'.png'));bpy.ops.render.render(write_still=True)
 print('V10_RENDER',name,flush=True)
# Sample transforms, assert cover remains clear throughout reactor movement.
report=[]
for fr in [1,45,85,91,97,121,127,133,150,173,193]:
 s.frame_set(fr);a=bpy.data.objects['THK_Reactor_Deploy_L'].location.x;z=bpy.data.objects['THK_RearPanel_Lift'].location.z
 assert a>=-.085001 and a<=.000001
 if a<-.00001:assert abs(z-.215)<.00001,(fr,a,z)
 report.append({'frame':fr,'reactor_x':a,'panel_z':z})
(p/'sequence_check.json').write_text(json.dumps(report,indent=2))
