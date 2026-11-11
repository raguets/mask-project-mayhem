import bpy,json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Rhino';out={}
paths=[A/'Rhino_V1_Vehicle.blend',A/'Rhino_RearVehicle_V1.blend']+[P/'art_source'/folder/name for folder,name in [('Alex_Sector','AlexSector_V1.blend'),('Alex_Sector','AlexSector_Mask_V1.blend'),('Bruce_Sato','BruceSato_V1.blend'),('Bruce_Sato','BruceSato_Mask_V1.blend')]]
try:
 for path in paths:
  bpy.ops.wm.open_mainfile(filepath=str(path));S=bpy.context.scene;entry={'reopened':True,'objects':len(S.objects),'armatures':sum(ob.type=='ARMATURE' for ob in S.objects)}
  if path.name.startswith('Rhino'):
   assert entry['armatures']==0;entry['no_character_dependency']=True;tires=[ob for ob in S.objects if ob.name.endswith('_Tire')];expected=6 if 'RearVehicle' in path.name else 10;assert len(tires)==expected;entry['tires']=len(tires)
   if 'RearVehicle' in path.name:
    assert not bpy.data.objects.get('Rhino_Control');assert not bpy.data.objects.get('RH_Hood');assert not any(ob.animation_data and ob.animation_data.drivers for ob in S.objects);entry['no_main_truck_dependency']=True;entry['driver_bake_verified']=True
   else:
    R=bpy.data.objects['Rhino_Control'];identity={ob.name:ob.data.as_pointer() for ob in tires};states=[]
    for frame in [1,91,151,241]:
     S.frame_set(frame);R.update_tag();bpy.context.view_layer.update();assert identity=={ob.name:ob.data.as_pointer() for ob in tires};states.append({'frame':frame,'pod_location':list(bpy.data.objects['Rhino_RearVehicle_Root'].location),'rear_hatch_angle':bpy.data.objects['RH_RearCockpitHatchPivot'].rotation_euler.y})
    entry['transform_states']=states;assert states[2]['pod_location'][0]<-4.8
  elif '_Mask_' in path.name:
   assert entry['armatures']==0;assert not bpy.data.objects.get('Rhino_Control');assert not any(ob.animation_data and ob.animation_data.drivers for ob in S.objects)
   person=path.name.split('_Mask_')[0];socket=bpy.data.objects[person+'_MaskSocket'];assert len(socket['rest_bind_origin'])==3;entry.update({'no_character_or_vehicle_dependency':True,'socket_origin':list(socket['rest_bind_origin']),'weights_retained':any(ob.type=='MESH' and len(ob.vertex_groups)>1 for ob in S.objects)})
  else:
   assert entry['armatures']==1;assert not bpy.data.objects.get('Rhino_Control');code='AS' if path.name.startswith('Alex') else 'BS';r=bpy.data.objects['AlexSector_Rig' if code=='AS' else 'BruceSato_Rig'];head=bpy.data.objects[code+'_Head_AnatomicalSurface'];identity=head.data.as_pointer();states=[]
   for pose in [0,1]:
    for mask in [False,True]:
     r['driving_pose']=pose;r['mask_on']=mask;r.update_tag();S.frame_set(1+pose);bpy.context.view_layer.update();visible=sum(not ob.hide_render for ob in bpy.data.collections[code+'_Mask'].all_objects);assert (visible>0)==mask;assert head.data.as_pointer()==identity and not head.hide_render;states.append({'pose':pose,'mask':mask,'same_head':True,'visible_mask_parts':visible})
   entry.update({'no_vehicle_dependency':True,'four_states':states})
  bad=[]
  for ob in S.objects:
   if ob.animation_data:
    for f in ob.animation_data.drivers:
     if not f.driver.is_valid:bad.append(ob.name+':'+f.data_path)
  entry['invalid_drivers']=bad;assert not bad,bad;out[path.name]=entry
finally:
 bpy.ops.wm.open_mainfile(filepath=str(A/'Rhino_V1.blend'));(A/'standalone_validation_v1.json').write_text(json.dumps(out,indent=2))
assert len(out)==6;print('RHINO_SIX_COMPONENTS_REOPENED_AND_VERIFIED')
