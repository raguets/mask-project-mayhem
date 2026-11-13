import bpy,math,json
from pathlib import Path
from mathutils import Vector,Quaternion
from mathutils.bvhtree import BVHTree
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Condor';s=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
R=bpy.data.objects['BradTurner_Rig'];root=bpy.data.objects['Condor_Control'];road=json.loads((A/'brad_riding_pose.json').read_text())
for f in list(R.animation_data.drivers):
 if f.data_path.startswith('pose.bones'):R.driver_remove(f.data_path,f.array_index)
for b in R.pose.bones:b.rotation_quaternion=road[b.name]
s.frame_set(121);bpy.context.view_layer.update()
def orient(bname,start,end):
 b=R.pose.bones[bname];rest=R.data.bones[bname];q=(rest.tail_local-rest.head_local).rotation_difference(Vector(end)-Vector(start));mat=(q.to_matrix()@rest.matrix_local.to_3x3()).to_4x4();mat.translation=start;b.matrix=mat;bpy.context.view_layer.update()
def limb(up,low,target,bend):
 a=R.pose.bones[up].head.copy();axis=Vector(target)-a;d=axis.length;axis.normalize();l1=R.data.bones[up].length;l2=R.data.bones[low].length;d=min(d,l1+l2-.001);t=a+axis*d;x=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(max(0,l1*l1-x*x));v=Vector(bend);v=(v-axis*v.dot(axis)).normalized();el=a+axis*x+v*h;orient(up,a,el);orient(low,el,t)
for side,label in [(1,'L'),(-1,'R')]:
 limb('thigh.'+label,'shin.'+label,(.29,side*.30,.55),(1,side*.7,0))
 limb('upper_arm.'+label,'forearm.'+label,(.56,side*.29,1.16),(0,side*.3,-1))
 b=R.pose.bones['foot.'+label];pos=b.head.copy();orient(b.name,pos,pos+Vector((.14,0,-.025)))
flight={b.name:list(b.rotation_quaternion) for b in R.pose.bones}
for b in R.pose.bones:
 q0=Quaternion(road[b.name]);q1=Quaternion(flight[b.name]);q1.make_compatible(q0)
 for i in range(4):drive(b,'rotation_quaternion',i,str((1,0,0,0)[i])+'*(1-p)+p*('+str(q0[i])+'*(1-t)+'+str(q1[i])+'*t)',[('p',R,'driving_pose'),('t',root,'transform')])
# Geometry checks, world-space evaluated surfaces, explicit limited scope.
def geometry(objects):
 dg=bpy.context.evaluated_depsgraph_get();vv=[];ff=[]
 for o in objects:
  if o.type!='MESH':continue
  ev=o.evaluated_get(dg);me=ev.to_mesh();n=len(vv);vv.extend(ev.matrix_world@v.co for v in me.vertices);ff.extend(tuple(n+i for i in f.vertices) for f in me.polygons);ev.to_mesh_clear()
 return vv,ff
blades=[o for o in bpy.data.objects if o.name.startswith('Condor_MainBlade_')]
pilot=[bpy.data.objects['BT_Head_AnatomicalSurface'],bpy.data.objects['BT_ContinuousFlightSuit']]+list(bpy.data.collections['BT_Mask'].all_objects)
body=[o for o in bpy.data.collections['Condor_Vehicle'].all_objects if any(k in o.name for k in ['Fairing','RearCowl','Windshield','Saddle'])]
samples=[]
for frame in range(1,122,6):
 s.frame_set(frame);bpy.context.view_layer.update();v,f=geometry(blades);bv=BVHTree.FromPolygons(v,f);v2,f2=geometry(pilot+body);ob=BVHTree.FromPolygons(v2,f2);samples.append({'frame':frame,'blade_surface_intersections':len(bv.overlap(ob))})
s.frame_set(121);bpy.context.view_layer.update();v,f=geometry(blades);pv,pf=geometry(pilot);clearance=min(p.z for p in v)-max(p.z for p in pv)
# Four states must retain the same body/head datablocks.
identity={o.name:o.data.as_pointer() for o in pilot if o.type=='MESH'};states=[]
for pose in [0.,1.]:
 for mask in [False,True]:
  R['driving_pose']=pose;R['mask_on']=mask;R.update_tag();bpy.context.view_layer.update();states.append({'pose':pose,'mask':mask,'same_meshes':all(bpy.data.objects[n].data.as_pointer()==ptr for n,ptr in identity.items())})
R['driving_pose']=1.;R['mask_on']=True;R.update_tag();s.frame_set(1);bpy.context.view_layer.update()
report={'scope':'21 world-space triangle overlap samples: blades vs pilot head/suit/mask and selected cowl/fairing/glass/saddle. Does not certify all collisions, containment, fingers or deformation. Full-turn rotor clearance uses horizontal plane bound at deployed state.','samples':samples,'full_turn_vertical_pilot_clearance_m':clearance,'four_states':states,'two_persistent_tires':len([o for o in bpy.data.objects if 'PersistentTire' in o.name])==2,'invalid_drivers':[o.name+f.data_path for o in bpy.data.objects if o.animation_data for f in o.animation_data.drivers if not f.driver.is_valid]}
(A/'validation_v3.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Condor_V3_Assembly.blend'),compress=True)
print('VALIDATION',json.dumps(report))
