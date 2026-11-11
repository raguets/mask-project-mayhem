import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Hurricane'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
out=[]
for name in ['Hurricane_V7_Vehicle.blend','Hurricane_V7_Assembly.blend']:
 bpy.ops.wm.open_mainfile(filepath=str(A/name));S=bpy.context.scene;root=bpy.data.objects['Hurricane_Control'];R=bpy.data.objects.get('HondoMacLean_Rig')
 if R:R['mask_on']=True;R['in_vehicle']=1.;R['driving_pose']=1.;R.update_tag()
 S.frame_set(151);bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT');root.hide_set(False);root.select_set(True);bpy.context.view_layer.objects.active=root
 cam=S.camera;cam.location=(8,-8,5.1);cam.rotation_euler=(Vector((0,0,1.45))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=49;S.render.resolution_x=1280;S.render.resolution_y=960;S.render.resolution_percentage=100
 for screen in bpy.data.screens:
  for ar in screen.areas:
   if ar.type=='VIEW_3D':
    sp=ar.spaces.active;sp.overlay.show_extras=False;sp.region_3d.view_location=(0,0,1.4);sp.region_3d.view_distance=9.;sp.region_3d.view_rotation=(cam.location-Vector((0,0,1.4))).to_track_quat('Z','Y')
   elif ar.type=='PROPERTIES':ar.spaces.active.context='OBJECT';ar.spaces.active.pin_id=root
 bpy.ops.wm.save_as_mainfile(filepath=str(A/name),compress=True);out.append({'file':name,'frame':S.frame_current,'selected':root.name})
(A/'final_presentation_v7.json').write_text(json.dumps(out,indent=2));print('FINAL_PRESENTATION_SAVED',out)
