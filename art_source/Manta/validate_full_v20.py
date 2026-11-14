import bpy,json,math,time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
A=Path('G:/DEV/mask-project-mayhem/art_source/Manta');S=bpy.context.scene;root=bpy.data.objects['Manta_Control'];R=bpy.data.objects['VanessaWarfield_Rig']
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
def surface(o):
 dg=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(dg);me=ev.to_mesh();v=[ev.matrix_world@p.co for p in me.vertices];f=[list(p.vertices) for p in me.polygons];ev.to_mesh_clear();return BVHTree.FromPolygons(v,f),v
parts=lambda prefixes:[o.name for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(prefixes)]
missiles=parts(('MA_PersistentMissile','MA_MissileRedTip','MA_MissileGuide','MA_TripleLauncherCassette'))
guns=parts(('MA_RedHeadlightCannon','MA_CannonDarkBore','MA_CannonRib'))
jets=parts(('MA_Reactor','MA_Nozzle'))
rear_glass=parts(('MA_RearHatchGlass','MA_QuarterGlass','MA_FlatHatch','MA_FlatQuarter'))
supports=parts(('MA_RearBoardRigidLeg',))
wheels=['MA_FrontWheel_'+str(sign)+'_Tire' for sign in [-1,1]]+['MA_RearWheel_'+str(sign)+'_Tire' for sign in [-1,1]]
hood=['MA_SlidingHoodSkin','MA_FixedHoodRearQuarter','MA_FixedHoodShoulder_L','MA_FixedHoodShoulder_R']
pairs=[('MA_MainBody',n) for n in wheels+['MA_MainWing_1','MA_MainWing_-1','MA_RearLightPanel']+guns+supports]
pairs += [(h,n) for h in hood for n in missiles+guns]
pairs += [('MA_SlidingHoodSkin',n) for n in parts(('MA_HeadlightPortRim','MA_FixedFrontCheek'))+['MA_FixedHoodShoulder_L','MA_FixedHoodShoulder_R','MA_IntegratedRoundedNose']]
pairs += [('MA_RearLightPanel',n) for n in jets+rear_glass]
names=sorted(set(n for pair in pairs for n in pair));hits={a+' / '+b:[] for a,b in pairs};states=[];started=time.time()
for i in range(241):
 f=1+i/2;S.frame_set(int(f),subframe=f%1);bpy.context.view_layer.update();ss={n:surface(bpy.data.objects[n]) for n in names}
 for a,b in pairs:
  overlap=ss[a][0].overlap(ss[b][0])
  if overlap:hits[a+' / '+b].append({'frame':f,'t':float(root['transform']),'triangle_pairs':len(overlap)})
 if i in [0,240]:
  bd={n:{'min':[min(p[k] for p in ss[n][1]) for k in range(3)],'max':[max(p[k] for p in ss[n][1]) for k in range(3)],'centre':list(sum(ss[n][1],Vector())/len(ss[n][1]))} for n in wheels+['MA_RearLightPanel','MA_SlidingHoodSkin']}
  states.append({'frame':f,'bounds':bd})
# Missile containment samples complement triangle intersection checks.
direction=Vector((1,.371,.163)).normalized()
def inside(tree,p):
 p=p.copy();count=0
 for j in range(24):
  hit=tree.ray_cast(p,direction,20)
  if hit[0] is None:return bool(count%2)
  count+=1;p=hit[0]+direction*.00001
 return False
contain=[]
for f in range(1,122):
 S.frame_set(f);bpy.context.view_layer.update();panels={h:surface(bpy.data.objects[h])[0] for h in hood}
 for n in missiles:
  tr,v=surface(bpy.data.objects[n]);sample=[sum(v,Vector())/len(v)]+v[::max(1,len(v)//12)]
  for h,tr in panels.items():
   count=sum(inside(tr,p) for p in sample)
   if count:contain.append({'frame':f,'part':n,'hood':h,'samples_inside':count})
S.frame_set(121);bpy.context.view_layer.update();tilt=next(o for o in bpy.data.objects['MA_TripleLauncherLift'].children if o.type=='EMPTY');axis=(tilt.matrix_world.to_3x3()@Vector((1,0,0))).normalized();angle=math.degrees(math.asin(axis.z))
gun_axes=[]
for sign in [-1,1]:
 o=bpy.data.objects['MA_MainWingForwardCannon_'+str(sign)];axisw=(o.matrix_world.to_3x3()@Vector((0,-sign,0))).normalized();gun_axes.append(list(axisw))
invalid=[]
for o in bpy.data.objects:
 if o.animation_data:
  invalid.extend([(o.name,f.data_path,f.array_index) for f in o.animation_data.drivers if not f.driver.is_valid])
pilot=[]
for mask in [False,True]:
 R['driving_pose']=1.;R['in_vehicle']=1.;R['mask_on']=mask;R.update_tag();S.frame_set(1);bpy.context.view_layer.update()
 check=['VW_ContinuousBodyAndFace']+([o.name for o in bpy.data.collections['Whip_Mask'].all_objects if o.type=='MESH'] if mask else [])
 cs={n:surface(bpy.data.objects[n])[0] for n in check};ov={}
 for n in ['MA_Windshield','MA_TbarRoof','MA_CabinFloor']:
  tr=surface(bpy.data.objects[n])[0];ov[n]=sum(len(tr.overlap(t)) for t in cs.values())
 pilot.append({'mask_on':mask,'surface_overlaps':ov,'driver_world_y':R.matrix_world.translation.y})
R['mask_on']=False;R.update_tag();S.frame_set(1);bpy.context.view_layer.update()
r={'source':bpy.data.filepath,'version':20,'phases':241,'elapsed_seconds':time.time()-started,'invalid_drivers':invalid,'selected_surface_overlaps':hits,'missile_containment_samples':contain,'missile_elevation_degrees':angle,'wing_cannon_forward_axes':gun_axes,'end_states':states,'pilot':pilot,'limits':'Selected evaluated triangle surfaces and finite missile containment samples. Does not prove all-part clearance/containment, padded contacts, suspension motion or flight physics.'}
(A/'validation_full_v20.json').write_text(json.dumps(r,indent=2));print(json.dumps({'nonzero_phase_counts':{k:len(v) for k,v in hits.items() if v},'containment_records':len(contain),'missile_angle':angle,'invalid_drivers':invalid,'pilot':pilot,'elapsed':r['elapsed_seconds']}))
