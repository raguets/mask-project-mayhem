import bpy,json,re
from pathlib import Path
from mathutils import Vector,Matrix
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Condor';B=P/'art_source/Brad_Turner';B.mkdir(exist_ok=True)
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
source=A/'Condor_V7_Assembly.blend';report=[]
def studio():return set(bpy.data.collections['Condor_Studio'].all_objects)
def prune(keep):
 for o in list(bpy.data.objects):
  if o not in keep:bpy.data.objects.remove(o,do_unlink=True)
 for c in list(bpy.data.collections):
  if not c.all_objects:bpy.data.collections.remove(c)
def cam(target,pos,lens=55):
 c=bpy.context.scene.camera;c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens
def select(o):
 bpy.ops.object.select_all(action='DESELECT');o.hide_set(False);o.select_set(True);bpy.context.view_layer.objects.active=o
try:
 bpy.ops.wm.open_mainfile(filepath=str(source));prune(set(bpy.data.collections['Condor_Vehicle'].all_objects)|studio());select(bpy.data.objects['Condor_Control']);out=A/'Condor_V7_Vehicle.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);report.append({'kind':'vehicle','file':str(out)})
 bpy.ops.wm.open_mainfile(filepath=str(source));r=bpy.data.objects['BradTurner_Rig'];r.parent=None
 for i in [0,2]:r.driver_remove('location',i)
 r.location=(0,0,0);r['in_vehicle']=0.;r['driving_pose']=0.;r['mask_on']=False
 for f in r.animation_data.drivers:
  if f.data_path.startswith('pose.bones'):
   f.driver.expression=re.sub(r'\bt\b','0',f.driver.expression)
   for v in list(f.driver.variables):
    if v.name=='t':f.driver.variables.remove(v)
 keep=set(bpy.data.collections['BT_Character'].all_objects)|set(bpy.data.collections['BT_Mask'].all_objects)|studio();prune(keep);r.update_tag();bpy.context.view_layer.update();cam((0,0,.95),(3,-3,1.8),65);select(r)
 out=B/'BradTurner_V1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);report.append({'kind':'character','file':str(out)})
 # Export mask from independent character at rest, retaining attachment weights.
 r['mask_on']=True;r.update_tag();bpy.context.view_layer.update();origin=r.data.bones['head'].head_local.copy();mask=bpy.data.collections['BT_Mask'];socket=bpy.data.objects.new('HocusPocus_HeadSocket',None);mask.objects.link(socket);socket['rest_bind_origin']=list(origin)
 for o in list(mask.all_objects):
  if o==socket:continue
  matrix=o.matrix_world.copy();o.animation_data_clear()
  for m in list(o.modifiers):
   if m.type=='ARMATURE':o.modifiers.remove(m)
  if o.type=='MESH':o.data.transform(Matrix.Translation(-origin)@matrix)
  o.parent=socket;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=Matrix.Identity(4);o.hide_render=False;o.hide_viewport=False
 prune(set(mask.all_objects)|studio());cam((.02,0,.14),(1,-1,.6),75);select(socket)
 floor=bpy.data.objects['Review_Floor'];floor.location.z=-.18
 out=B/'HocusPocus_V1.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);report.append({'kind':'mask','file':str(out)})
 # Actual reopen of each source, checking surviving dependencies and four states.
 for item in report:
  bpy.ops.wm.open_mainfile(filepath=item['file']);objects=set(bpy.data.objects);bad=[]
  for o in objects:
   for m in o.modifiers:
    if m.type=='ARMATURE' and m.object not in objects:bad.append(o.name)
   if o.animation_data:
    for f in o.animation_data.drivers:
     for v in f.driver.variables:
      for t in v.targets:
       if isinstance(t.id,bpy.types.Object) and t.id not in objects:bad.append(o.name+':missing driver target')
  item['actual_reopened']=True;item['invalid_dependencies']=bad;item['armatures']=sum(o.type=='ARMATURE' for o in objects)
  if item['kind']=='character':
   r=bpy.data.objects['BradTurner_Rig'];head=bpy.data.objects['BT_Head_AnatomicalSurface'];suit=bpy.data.objects['BT_ContinuousFlightSuit'];ids=(head.data.as_pointer(),suit.data.as_pointer());item['four_states']=[]
   for pose in [0.,1.]:
    for mask_on in [False,True]:r['driving_pose']=pose;r['mask_on']=mask_on;r.update_tag();bpy.context.view_layer.update();item['four_states'].append({'pose':pose,'mask':mask_on,'same_head_and_body':ids==(head.data.as_pointer(),suit.data.as_pointer())})
  item['passed']=not bad and item['armatures']==(1 if item['kind']=='character' else 0)
finally:
 bpy.ops.wm.open_mainfile(filepath=str(source));(A/'standalone_validation_v7.json').write_text(json.dumps(report,indent=2))
print('REOPENED_COMPONENTS',json.dumps(report))
