import bpy,json
from pathlib import Path
from mathutils import Vector,Matrix
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Manta';B=P/'art_source/Vanessa_Warfield';B.mkdir(exist_ok=True)
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
source=A/'Manta_V5_Assembly.blend';report=[]
def prune(keep):
 for o in list(bpy.data.objects):
  if o not in keep:bpy.data.objects.remove(o,do_unlink=True)
 for c in list(bpy.data.collections):
  if not c.all_objects:bpy.data.collections.remove(c)
def studio():return set(bpy.data.collections['Manta_Studio'].all_objects)
def present(o,cam,target,lens=58):
 bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT');o.hide_set(False);o.select_set(True);bpy.context.view_layer.objects.active=o
 c=bpy.context.scene.camera;c.location=cam;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens
 for scr in bpy.data.screens:
  for ar in scr.areas:
   if ar.type=='VIEW_3D':ar.spaces.active.shading.type='MATERIAL';ar.spaces.active.region_3d.view_location=target;ar.spaces.active.region_3d.view_distance=3 if o.type=='ARMATURE' else 7
try:
 bpy.ops.wm.save_as_mainfile(filepath=str(A/'Session_before_final_export.blend'),copy=True,compress=True)
 bpy.ops.wm.open_mainfile(filepath=str(source));prune(set(bpy.data.collections['Manta_Vehicle'].all_objects)|set(bpy.data.collections['Manta_Interior'].all_objects)|studio());present(bpy.data.objects['Manta_Control'],(6,-6,3.8),(0,0,.65));out=A/'Manta_V5_Vehicle.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);report.append({'kind':'vehicle','file':str(out)})
 bpy.ops.wm.open_mainfile(filepath=str(source));r=bpy.data.objects['VanessaWarfield_Rig'];r.parent=None
 for i in range(3):r.driver_remove('location',i)
 r.location=(0,0,0);r['in_vehicle']=0.;r['driving_pose']=0.;r['mask_on']=False;r.update_tag();bpy.context.view_layer.update()
 prune(set(bpy.data.collections['Vanessa_Character'].all_objects)|set(bpy.data.collections['Whip_Mask'].all_objects)|studio());present(r,(2.9,-3.4,2),(0,0,.93),65);out=B/'VanessaWarfield_V1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);report.append({'kind':'character','file':str(out)})
 r['mask_on']=True;r.update_tag();bpy.context.view_layer.update();origin=r.data.bones['head'].head_local.copy();mask=bpy.data.collections['Whip_Mask'];socket=bpy.data.objects.new('Whip_HeadSocket',None);mask.objects.link(socket);socket['rest_bind_origin']=list(origin);socket['attachment_note']='Restore rest origin and named head/chest armature weights when assembling. Collar is flexible; rigid shell follows head.'
 for o in list(mask.all_objects):
  if o==socket:continue
  matrix=o.matrix_world.copy();o.animation_data_clear()
  for m in list(o.modifiers):
   if m.type=='ARMATURE':o.modifiers.remove(m)
  if o.type=='MESH':o.data.transform(Matrix.Translation(-origin)@matrix)
  o.parent=socket;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=Matrix.Identity(4);o.hide_render=False;o.hide_viewport=False
 prune(set(mask.all_objects)|studio());present(socket,(1,-1,.6),(.02,0,.01),70)
 z=min((o.matrix_world@v.co).z for o in mask.all_objects if o.type=='MESH' for v in o.data.vertices);bpy.data.objects['MA_StudioFloor'].location.z=z-.065
 out=B/'Whip_V1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);report.append({'kind':'mask','file':str(out)})
 for item in report:
  bpy.ops.wm.open_mainfile(filepath=item['file']);bpy.context.view_layer.update();objects=set(bpy.data.objects);bad=[]
  for o in objects:
   if o.parent and o.parent not in objects:bad.append(o.name+':parent')
   for m in o.modifiers:
    if m.type=='ARMATURE' and m.object not in objects:bad.append(o.name+':armature')
   if o.animation_data:
    for f in o.animation_data.drivers:
     if not f.driver.is_valid:bad.append(o.name+':invalid driver '+f.data_path)
     for v in f.driver.variables:
      for t in v.targets:
       if isinstance(t.id,bpy.types.Object) and t.id not in objects:bad.append(o.name+':driver target')
  item['actual_reopened']=True;item['invalid_dependencies']=bad;item['armatures']=sum(o.type=='ARMATURE' for o in objects)
  if item['kind']=='character':
   r=bpy.data.objects['VanessaWarfield_Rig'];body=bpy.data.objects['VW_ContinuousBodyAndFace'];identity=body.data.as_pointer();item['four_states']=[]
   for pose in [0.,1.]:
    for m in [False,True]:r['driving_pose']=pose;r['mask_on']=m;r.update_tag();bpy.context.view_layer.update();item['four_states'].append({'pose':pose,'mask_on':m,'same_body_face_mesh':identity==body.data.as_pointer()})
  item['passed']=not bad and item['armatures']==(1 if item['kind']=='character' else 0)
finally:
 bpy.ops.wm.open_mainfile(filepath=str(source));(A/'standalone_validation_v5.json').write_text(json.dumps(report,indent=2))
print('INDEPENDENT_SOURCES_REOPENED',json.dumps(report))
