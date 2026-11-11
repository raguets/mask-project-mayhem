import bpy,json,os
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');O=P/'art_source/Thunderhawk/renders/v11';O.mkdir(parents=True,exist_ok=True)
s=bpy.context.scene;r=bpy.data.objects['MattTrakker_Rig'];s.render.engine='CYCLES';s.cycles.samples=20;s.cycles.use_denoising=True
try:
 pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='OPTIX';pref.get_devices()
 for d in pref.devices:d.use=d.type!='CPU'
 s.cycles.device='GPU'
except Exception:pass
s.render.resolution_x=1000;s.render.resolution_y=1100;s.render.resolution_percentage=100
views={
 'standing':((3.5,3.4,1.9),(0,0,.96),False,False,False,1,62),
 'standing_mask':((3.5,3.4,1.9),(0,0,.96),False,True,False,1,62),
 'face':((.79,.52,1.76),(0,0,1.685),False,False,False,1,85),
 'spectrum':((.91,.67,1.77),(0,0,1.69),False,True,False,1,75),
 'cabin':((1.45,1.95,1.45),(-.18,.22,.79),True,False,True,97,52),
 'cabin_mask':((1.45,1.95,1.45),(-.18,.22,.79),True,True,True,97,52),
 'road':((5,5,2.8),(0,0,.7),True,False,True,1,50),
 'rear_flight':((-5,4,2.5),(-.2,0,.7),True,True,True,97,52),
 'dashboard':((-.72,.30,1.13),(.36,.20,.76),True,False,True,97,28),
 'face_front':((.95,0,1.69),(0,0,1.685),False,False,False,1,100),
 'face_profile':((0,1.0,1.71),(0,0,1.685),False,False,False,1,95),
 'interior':((1.15,1.65,1.50),(-.15,0,.73),True,False,True,97,48)}
chosen=os.getenv('THK11_VIEWS',','.join(views)).split(',');reports=[]
for name in chosen:
 loc,target,drive,mask,vehicle,fr,lens=views[name]
 for ob in list(bpy.data.collections['MT11_Character'].objects)+list(bpy.data.collections['Spectrum11_Asset'].objects):
  if ob.animation_data:
   for fc in ob.animation_data.drivers:
    if fc.data_path=='hide_render':fc.mute=name in ['interior','dashboard']
 r['driving_pose']=int(drive);r['mask_on']=mask;r.location=(0,.4 if vehicle else 0,0);r.update_tag();s.frame_set(fr);bpy.context.view_layer.update()
 for co in ['THK9_Exterior','THK11_Interior']:
  for ob in bpy.data.collections[co].objects:ob.hide_render=not vehicle
 for ob in bpy.data.collections['MT11_Character'].objects:
  if name in ['interior','dashboard'] or not ob.name.startswith(('MT_Hair','MT_Sideburn')):ob.hide_render=name in ['interior','dashboard']
 for ob in bpy.data.collections['Spectrum11_Asset'].objects:
  if name in ['interior','dashboard']:ob.hide_render=True
 # The close cabin view suppresses only near door to inspect fit; source remains intact.
 if name in ['cabin','cabin_mask','interior']:
  for ob in bpy.data.collections['THK9_Exterior'].objects:
   if ob.name=='THK_Windshield':ob.hide_render=True
 c=s.camera;c.location=loc;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='PERSP';c.data.lens=lens
 s.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True);print('THK11_RENDERED',name,flush=True)
 reports.append({'view':name,'driving':drive,'mask':mask,'frame':fr})
(O/'render_manifest.json').write_text(json.dumps(reports,indent=2))

