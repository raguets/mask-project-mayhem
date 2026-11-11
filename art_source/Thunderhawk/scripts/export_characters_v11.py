"""Export clean standalone .blend assets from reviewed V11, in a separate process."""
import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Matt_Trakker';A.mkdir(parents=True,exist_ok=True)
s=bpy.context.scene;r=bpy.data.objects['MattTrakker_Rig'];char=bpy.data.collections['MT11_Character'];mask=bpy.data.collections['Spectrum11_Asset']
keep=set(char.all_objects)|set(mask.all_objects)
keep|={o for o in s.objects if o.type in ['CAMERA','LIGHT'] or o.name=='Review_Floor' or o.name.startswith('REF_MT_')}
for o in list(bpy.data.objects):
 if o not in keep:bpy.data.objects.remove(o,do_unlink=True)
for co in list(bpy.data.collections):
 if len(co.all_objects)==0:bpy.data.collections.remove(co)
for ac in list(bpy.data.actions):
 if ac.name.startswith('MT_Pose_'):bpy.data.actions.remove(ac)
s.name='MattTrakker_V2_Independent';s.frame_set(1);r.location=(0,0,0);r['driving_pose']=0;r['mask_on']=False;r.update_tag();bpy.context.view_layer.update()
s['usage']='Select MattTrakker_Rig. Object Properties > Custom Properties: driving_pose=0 standing or 1 driving; mask_on=False or True. One body and one face only.'
s['reference_limit']='Portrait is an illustration; supplied photographic references are replicas and toys. Realistic anatomical interpretation, not certified ultra-faithful photoreal likeness.'
s.camera.location=(3.5,3.4,1.9);s.camera.rotation_euler=(Vector((0,0,.96))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=62
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   view=area.spaces.active.region_3d;view.view_location=(0,0,.94);view.view_distance=3.2;view.view_rotation=(Vector((3,4,2))-Vector((0,0,.94))).to_track_quat('Z','Y');area.spaces.active.overlay.show_extras=False
bpy.ops.object.select_all(action='DESELECT');r.select_set(True);bpy.context.view_layer.objects.active=r
bpy.ops.wm.save_as_mainfile(filepath=str(A/'MattTrakker_V2.blend'),compress=True)
charcount=len(char.all_objects)
# Spectrum file: socket-local geometry, no dependency on Matt or vehicle.
head_origin=Vector((-.008,0,1.55));socket=bpy.data.objects.new('Spectrum_HeadSocket',None);mask.objects.link(socket);socket.empty_display_size=.05;socket['attach_to']='MattTrakker_Rig/head';socket['rest_head_origin_m']=list(head_origin)
for ob in list(mask.objects):
 if ob==socket:continue
 ob.animation_data_clear()
 for mod in list(ob.modifiers):
  if mod.type=='ARMATURE':ob.modifiers.remove(mod)
 ob.parent=None;ob.matrix_world.identity()
 if ob.type=='MESH':
  for v in ob.data.vertices:v.co-=head_origin
 ob.parent=socket;ob.hide_render=False;ob.hide_viewport=False
for ob in list(char.all_objects):bpy.data.objects.remove(ob,do_unlink=True)
for co in list(bpy.data.collections):
 if co.name.startswith(('MT11','MT_Editable')):bpy.data.collections.remove(co)
for ob in list(s.objects):
 if ob.name.startswith('REF_MT_'):bpy.data.objects.remove(ob,do_unlink=True)
s.name='Spectrum_V2_Independent';s['usage']='Standalone removable Spectrum. Spectrum_HeadSocket is local origin matching the head-bone origin in Matt asset. Append this collection and bone-parent socket to head.'
s.camera.location=(.85,.67,.4);s.camera.rotation_euler=(Vector((.02,0,.14))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=70
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_location=(0,0,.14);area.spaces.active.region_3d.view_distance=.8
bpy.ops.object.select_all(action='DESELECT');socket.select_set(True);bpy.context.view_layer.objects.active=socket
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Spectrum_V2.blend'),compress=True)
print('INDEPENDENT_ASSETS_SAVED '+json.dumps({'character_objects':charcount,'spectrum_objects':len(mask.objects),'files':['MattTrakker_V2.blend','Spectrum_V2.blend']}),flush=True)
