import bpy,json,math
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Hurricane';H=P/'art_source/Hondo_MacLean'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
files=[('vehicle',A/'Hurricane_V7_Vehicle.blend'),('character',H/'HondoMacLean_V1.blend'),('mask',H/'HondoMask_V1.blend')];reports=[]
try:
 for kind,path in files:
  bpy.ops.wm.open_mainfile(filepath=str(path));S=bpy.context.scene;S.frame_set(1);bpy.context.view_layer.update()
  item={'kind':kind,'file':str(path),'objects':len(S.objects),'armatures':[o.name for o in S.objects if o.type=='ARMATURE'],'invalid_drivers':[],'missing_driver_targets':[]}
  for o in S.objects:
   for owner in [o]+([o.data.shape_keys] if o.type=='MESH' and o.data.shape_keys else []):
    if owner.animation_data:
     for f in owner.animation_data.drivers:
      if not f.driver.is_valid:item['invalid_drivers'].append(owner.name+':'+f.data_path)
      for v in f.driver.variables:
       if v.type=='SINGLE_PROP' and not v.targets[0].id:item['missing_driver_targets'].append(owner.name+':'+f.data_path)
  if kind=='character':
   R=bpy.data.objects['HondoMacLean_Rig'];names=['HondoMacLean_Rig','HMC_Head_AnatomicalSurface','HMC_ContinuousFlightSuit'];ids={n:bpy.data.objects[n].as_pointer() for n in names};item['states']=[]
   assert len(item['armatures'])==1 and 'Hurricane_Control' not in S.objects
   assert R.animation_data and len(R.animation_data.drivers)>100
   assert not any(f.data_path in ['["gunner_pose"]','["vehicle_lift"]'] for f in R.animation_data.drivers)
   mask=[o for o in bpy.data.collections['HMC_Mask'].all_objects if o.type=='MESH']
   for d,g,m in [(0,0,False),(0,0,True),(1,0,False),(1,0,True),(0,1,False),(0,1,True)]:
    R['driving_pose']=d;R['gunner_pose']=g;R['mask_on']=m;R['in_vehicle']=0.;R.update_tag();S.frame_set(2);S.frame_set(1);bpy.context.view_layer.update()
    assert all(bpy.data.objects[n].as_pointer()==p for n,p in ids.items())
    assert all(o.hide_render!=m for o in mask)
    bounds={}
    for name in names[1:]:
     o=bpy.data.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get());me=o.to_mesh();points=[o.matrix_world@v.co for v in me.vertices];assert all(math.isfinite(x) for p in points for x in p);bounds[name]=[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)];o.to_mesh_clear()
    item['states'].append({'driving_pose':d,'gunner_pose':g,'mask_on':m,'same_body_head_rig':True,'mask_visibility_correct':True,'bounds':bounds})
   item['pose_drivers_retained']=len(R.animation_data.drivers)
  elif kind=='vehicle':
   assert not item['armatures'];assert not any(o.name.startswith('HMC_') for o in S.objects)
   ROOT=bpy.data.objects['Hurricane_Control'];S.frame_set(151);bpy.context.view_layer.update();item['lift_m']=bpy.data.objects['HU_UpperChassisLift'].location.z;assert abs(item['lift_m']-.30)<1e-5
   barrel=bpy.data.objects['HU_RightWindshieldBarrel'];e=barrel.evaluated_get(bpy.context.evaluated_depsgraph_get());me=e.to_mesh();item['windshield_barrel_y']=[min((e.matrix_world@v.co).y for v in me.vertices),max((e.matrix_world@v.co).y for v in me.vertices)];e.to_mesh_clear();assert item['windshield_barrel_y'][1]<0
   item['tires']=[o.name for o in S.objects if o.name.endswith('_Tire') and o.name.startswith('HU_')];assert len(item['tires'])==6
  else:
   assert not item['armatures'] and 'HondoMacLean_Rig' not in S.objects and 'Hurricane_Control' not in S.objects
   assert not any(m.type=='ARMATURE' for o in S.objects for m in o.modifiers)
   socket=bpy.data.objects['HondoMask_HeadSocket'];item['rest_bind_origin']=list(socket['rest_bind_origin']);item['mask_meshes']=len([o for o in bpy.data.collections['HMC_Mask'].objects if o.type=='MESH']);assert item['mask_meshes']>10
  assert not item['invalid_drivers'] and not item['missing_driver_targets']
  if kind=='character':
   R['driving_pose']=0.;R['gunner_pose']=0.;R['mask_on']=False;R.update_tag()
  S.frame_set(1);bpy.context.view_layer.update()
  folder=A/'renders/standalone_v7';folder.mkdir(parents=True,exist_ok=True)
  S.render.engine='CYCLES';S.cycles.device='GPU';S.cycles.samples=20;S.cycles.use_denoising=True;S.render.resolution_x=1000;S.render.resolution_y=1000;S.render.resolution_percentage=100;S.render.filepath=str(folder/(kind+'.png'));bpy.ops.render.render(write_still=True);item['reopened_render']=S.render.filepath
  item['status']='passed';reports.append(item)
finally:
 bpy.ops.wm.open_mainfile(filepath=str(A/'Hurricane_V7_Assembly.blend'))
 (A/'standalone_validation_v7.json').write_text(json.dumps({'reopened':reports,'expected':3,'method':'Actual live Blender reopen of each ordinary-saved source; native driver targets, object identities, six character states, wheel count, lift and right-side cannon checked.'},indent=2))
assert len(reports)==3
print('STANDALONE_REOPEN_PASSED',[(x['kind'],x['objects']) for x in reports])
