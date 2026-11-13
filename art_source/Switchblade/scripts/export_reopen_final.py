import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Switchblade';B=P/'art_source/Miles_Mayhem';B.mkdir(exist_ok=True)
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
source=Path(bpy.data.filepath);version=source.stem.split('_')[1];report=[]
character_version='V3' if int(version[1:])>=16 else ('V2' if version=='V15' else 'V1')
def prune(keep):
 for o in list(bpy.data.objects):
  if o not in keep:bpy.data.objects.remove(o,do_unlink=True)
 for c in list(bpy.data.collections):
  if not c.all_objects:bpy.data.collections.remove(c)
def studio():return set(bpy.data.collections['Switchblade_Studio'].all_objects)
def cam(pos,target,lens):
 o=bpy.context.scene.camera;o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens
def select(o):
 bpy.ops.object.select_all(action='DESELECT');o.hide_set(False);o.select_set(True);bpy.context.view_layer.objects.active=o
try:
 bpy.ops.wm.open_mainfile(filepath=str(source));prune(set(bpy.data.collections['Switchblade_Vehicle'].all_objects)|set(bpy.data.collections['Switchblade_Interior'].all_objects)|studio());select(bpy.data.objects['Switchblade_Control']);out=A/('Switchblade_'+version+'_Vehicle.blend');bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);report.append({'kind':'vehicle','file':str(out)})
 bpy.ops.wm.open_mainfile(filepath=str(source));r=bpy.data.objects['MilesMayhem_Rig'];r.parent=None
 for i in [0,2]:r.driver_remove('location',i)
 r.location=(0,0,0);r['in_vehicle']=0.;r['driving_pose']=0.;r['mask_on']=False;r.update_tag();bpy.context.view_layer.update()
 prune(set(bpy.data.collections['Miles_Character'].all_objects)|set(bpy.data.collections['Miles_ViperMask'].all_objects)|studio());cam((3,-3,1.9),(0,0,.94),56);select(r);out=B/('MilesMayhem_'+character_version+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);report.append({'kind':'character','file':str(out)})
 r['mask_on']=True;r.update_tag();bpy.context.view_layer.update();origin=r.data.bones['head'].head_local.copy();mask=bpy.data.collections['Miles_ViperMask'];socket=bpy.data.objects.new('Viper_HeadSocket',None);mask.objects.link(socket);socket['rest_bind_origin']=list(origin);socket['attachment_note']='Restore bind origin and armature weights when assembling; shoulder gorget follows spine, helmet follows head.'
 for o in list(mask.all_objects):
  if o==socket:continue
  matrix=o.matrix_world.copy();o.animation_data_clear()
  for m in list(o.modifiers):
   if m.type=='ARMATURE':o.modifiers.remove(m)
  if o.type=='MESH':o.data.transform(Matrix.Translation(-origin)@matrix)
  elif o.type=='CURVE':
   for sp in o.data.splines:
    for p in sp.points:p.co=(*(Matrix.Translation(-origin)@matrix@Vector(p.co[:3])),1)
  o.parent=socket;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=Matrix.Identity(4);o.hide_render=False;o.hide_viewport=False
 prune(set(mask.all_objects)|studio());cam((1,-1,.55),(.02,0,.02),70)
 minz=min((o.matrix_world@v.co).z for o in mask.all_objects if o.type=='MESH' for v in o.data.vertices)
 bpy.data.objects['Review_Floor'].location.z=minz+.01;select(socket);out=B/('Viper_'+character_version+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);report.append({'kind':'mask','file':str(out)})
 for item in report:
  bpy.ops.wm.open_mainfile(filepath=item['file']);objects=set(bpy.data.objects);bad=[]
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
   r=bpy.data.objects['MilesMayhem_Rig'];h=bpy.data.objects['MM_Head_AnatomicalSurface'];body=bpy.data.objects['MM_ContinuousFlightSuit'];ids=(h.data.as_pointer(),body.data.as_pointer());item['four_states']=[]
   for pose in [0.,1.]:
    for m in [False,True]:r['driving_pose']=pose;r['mask_on']=m;r.update_tag();bpy.context.view_layer.update();item['four_states'].append({'pose':pose,'mask_on':m,'same_head_body':ids==(h.data.as_pointer(),body.data.as_pointer())})
  item['passed']=not bad and item['armatures']==(1 if item['kind']=='character' else 0)
finally:
 bpy.ops.wm.open_mainfile(filepath=str(source));(A/'standalone_validation.json').write_text(json.dumps(report,indent=2));(A/('standalone_validation_'+version.lower()+'.json')).write_text(json.dumps(report,indent=2))
print('INDEPENDENT_SOURCES_REOPENED',json.dumps(report))
