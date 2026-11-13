import bpy,math,json
from pathlib import Path
from mathutils import Vector,Quaternion
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Condor'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
CURRENT=bpy.data.collections['Condor_Vehicle'];root=bpy.data.objects['Condor_Control'];PARENT=root;R=bpy.data.objects['BradTurner_Rig'];s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
def taper(x):return .85-.15*max(0,min(1,(-.40-x)/1.17))
for o in CURRENT.all_objects:
 if o.type=='MESH' and o.name.startswith(('Condor_RearMonobloc','Condor_RearBlockVent')):
  for v in o.data.vertices:v.co.y*=taper(v.co.x)
front_names=('Condor_AngularFrontCowl','Condor_AngularBlackInset','Condor_LowerFairing','Condor_MirrorPod','Condor_FacetedWindshield','Condor_WindshieldPerimeter','Condor_InstrumentPanel','Condor_Display','Condor_Handlebar','Condor_Grip','Condor_SquareWeaponSocket')
for o in CURRENT.all_objects:
 if o.name.startswith(front_names):
  if o.type=='MESH':
   for v in o.data.vertices:v.co.y*=.82
  elif o.type=='CURVE':
   for sp in o.data.splines:
    for p in sp.points:p.co.y*=.82
  if o.name.startswith('Condor_SquareWeaponSocket'):
   for v in o.data.vertices:v.co.z=.78+(v.co.z-.78)*.82
  if o.name=='Condor_AngularFrontCowl':
   for v in o.data.vertices:
    if v.index>=32:v.co.z=.78+(v.co.z-.78)*.82
# Converging mast arms, fixed crossmember and a rotating hub holding BOTH blades.
mast=bpy.data.objects['Condor_RotorSupport'];hub=bpy.data.objects['Condor_MainRotorHub'];black=bpy.data.materials['Condor_Charcoal'];chrome=bpy.data.materials['Condor_WheelAlloy']
for o in list(CURRENT.all_objects):
 if o.name.startswith(('Condor_MastArm','Condor_MastCrossBridge','Condor_MainRotorSpindle')):bpy.data.objects.remove(o,do_unlink=True)
for side in [-1,1]:
 tube('Condor_ConvergingMast_'+str(side),(-.46,side*.30,.43),(-1.718,side*.075,.45),.039,black,N=4,root=mast)
 h=bpy.data.objects['Condor_BladeHinge_'+str(side)];h.location.y=side*.075;h.animation_data.drivers[0].driver.expression=str(-side)+'*1.394*(1-max(0,(t-0.72)/0.28))'
tube('Condor_FixedMastAxle',(-.46,-.34,.43),(-.46,.34,.43),.041,black)
tube('Condor_MastTopBridge',(-1.718,-.095,.45),(-1.718,.095,.45),.038,black,root=mast)
tube('Condor_RotorBearing',(-1.757,0,.45),(-1.679,0,.45),.088,chrome,root=hub)
tube('Condor_RotatingBladeGrips',(-1.718,-.11,.45),(-1.718,.11,.45),.030,black,root=hub)
# Refit hand targets to narrower handlebars, preserving weighted character and legs.
def orient(name,a,b):
 pb=R.pose.bones[name];rest=R.data.bones[name];q=(rest.tail_local-rest.head_local).rotation_difference(Vector(b)-Vector(a));m=(q.to_matrix()@rest.matrix_local.to_3x3()).to_4x4();m.translation=a;pb.matrix=m;bpy.context.view_layer.update()
def arms(side,label,t):
 up='upper_arm.'+label;low='forearm.'+label;a=R.pose.bones[up].head.copy();target=Vector((.56,side*.29*.82,1.06+.12*t));axis=target-a;d=axis.length;axis.normalize();l1=R.data.bones[up].length;l2=R.data.bones[low].length;d=min(d,l1+l2-.001);target=a+axis*d;x=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(max(0,l1*l1-x*x));v=Vector((0,side*.3,-1));v=(v-axis*v.dot(axis)).normalized();el=a+axis*x+v*h;orient(up,a,el);orient(low,el,target)
poses=[]
for frame,t in [(1,0),(121,1)]:
 s.frame_set(frame);R['driving_pose']=1.;R.update_tag();bpy.context.view_layer.update();pose={b.name:list(b.rotation_quaternion) for b in R.pose.bones}
 for f in list(R.animation_data.drivers):
  if f.data_path.startswith('pose.bones'):R.driver_remove(f.data_path,f.array_index)
 for b in R.pose.bones:b.rotation_quaternion=pose[b.name]
 for side,label in [(1,'L'),(-1,'R')]:arms(side,label,t)
 poses.append({b.name:list(b.rotation_quaternion) for b in R.pose.bones})
 # Restore initial drivers before evaluating the other endpoint.
 for b in R.pose.bones:
  for i,v in enumerate(pose[b.name]):drive(b,'rotation_quaternion',i,str((1,0,0,0)[i])+'*(1-p)+'+str(v)+'*p',[('p',R,'driving_pose')])
for b in R.pose.bones:
 q0=Quaternion(poses[0][b.name]);q1=Quaternion(poses[1][b.name]);q1.make_compatible(q0)
 for i in range(4):drive(b,'rotation_quaternion',i,str((1,0,0,0)[i])+'*(1-p)+p*('+str(q0[i])+'*(1-t)+'+str(q1[i])+'*t)',[('p',R,'driving_pose'),('t',root,'transform')])
# No waist at the helmet neck: widen shell lower rings, then blend into shoulders.
mask=bpy.data.objects['BT_HocusPocus_OnePiece'];N=128
for v in mask.data.vertices:
 if v.index<8*N and v.co.z<1.657:
  j=v.index//N;a=2*pi*(v.index%N)/N;ry=max(.139,[.100,.107,.112,.116,.120,.124,.127,.133][j]);rx=max(.143,[.108,.125,.136,.140,.149,.162,.166,.160][j]);v.co.y=ry*sin(a);v.co.x=-.010+rx*cos(a)
# Mid collar ring bridges widened lower shell to the projected shoulder contact ring.
base=14*N
for i in range(N):mask.data.vertices[base+i].co=mask.data.vertices[i].co.lerp(mask.data.vertices[base+N+i].co,.5)
voice=material('BT_VocalGrille',(.006,.008,.010),.25,.42);mask.data.materials.append(voice);voiceidx=len(mask.data.materials)-1
for v in mask.data.vertices:
 if 1.582<=v.co.z<=1.640 and v.co.x>0:
  a=math.atan2(v.co.y,max(.001,v.co.x+.01));width=.34-.17*(v.co.z-1.582)/.058
  if abs(a)<width:v.co.x+=.010+.002*sin(a*100)**2
mask.data.update()
for f in mask.data.polygons:
 p=f.center
 if 1.582<p.z<1.640 and p.x>.10:
  a=math.atan2(p.y,p.x+.01);width=.34-.17*(p.z-1.582)/.058
  if abs(a)<width:f.material_index=voiceidx if int((a+.4)*55)%4!=0 else 0
mask['vocal_system']='Integrated triangular relief grille with ribs before mouth, user Darth Vader-like reference. No separate mask object.'
s.frame_set(1);R['mask_on']=True;R.update_tag();bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Condor_V12_Assembly.blend'),compress=True)
print('V12_TAPER_CONVERGING_MAST_NARROW_FRONT_VOCAL_MASK_SAVED')
