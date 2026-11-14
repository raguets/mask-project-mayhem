import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Manta';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
root=bpy.data.objects['Manta_Control'];R=bpy.data.objects['VanessaWarfield_Rig'];S.frame_set(1);bpy.context.view_layer.update()
D=json.loads((A/'proportions_v13.json').read_text());rear_scale=1.41/(-.80-D['old_rear']);front_scale=1.88/(D['old_front']-.50)
def prior(x):return .75+(x-.75)*1.10 if x>.75 else (-1.05+(x+1.05)*1.08 if x<-1.05 else x)
def X(x):return -.94+(x+.80)*rear_scale if x<-.80 else (.47+(x-.50)*front_scale if x>.50 else -.94+(x+.80)*(1.41/1.30))
def C(x):return X(prior(x))
CURRENT=bpy.data.collections['Manta_Vehicle'];PARENT=root
purple=bpy.data.objects['MA_MainBody'].data.materials[0];black=bpy.data.objects['MA_Underbody'].data.materials[0]
# Restore unperforated, already curved shoulders; then create the CORRECT thin bore.
with bpy.data.libraries.load(str(A/'Manta_V11_Assembly.blend'),link=False) as (src,dst):dst.objects=['MA_FixedHoodShoulder_L','MA_FixedHoodShoulder_R']
for old,l in zip(dst.objects,['L','R']):
 ob=bpy.data.objects['MA_FixedHoodShoulder_'+l];ob.data=old.data.copy();bpy.data.objects.remove(old,do_unlink=True)
 # Move the inner seam to 1.5 mm instead of a conspicuous 12 mm gap.
 rows={}
 for v in ob.data.vertices:rows.setdefault(round(v.co.x,5),[]).append(v)
 for row in rows.values():
  inner=min(abs(v.co.y) for v in row)
  for v in row:
   if abs(abs(v.co.y)-inner)<.0001:v.co.y-=math.copysign(.0105,v.co.y)
 for v in ob.data.vertices:v.co.x=C(v.co.x)
 for mod in ob.modifiers:
  if mod.type=='BEVEL':mod.width=.006;mod.segments=5
fixed=bpy.data.objects['MA_FixedHoodRearQuarter']
for v in fixed.data.vertices:
 if v.co.x>C(1.073)-.001:v.co.x=C(1.085)-.0015
# Remove old inner walls/frames left by earlier definitions of the headlights.
for ob in list(bpy.data.objects):
 if ob.name.startswith(('MA_HeadlightPortInnerWall','MA_HeadlightPortRim')):bpy.data.objects.remove(ob,do_unlink=True)
def subtract(target,cut,name):
 m=target.modifiers.new(name,'BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cut;bpy.context.view_layer.objects.active=target;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cut,do_unlink=True)
ports=[]
for sign,l in [(1,'L'),(-1,'R')]:
 gun=bpy.data.objects['MA_HeadlightCannonTravel_'+str(sign)]
 # Thin barrels fit inside thin rectangular ports, without cutting the bonnet skin.
 for ob in gun.children:
  if ob.type=='MESH':
   for v in ob.data.vertices:v.co.y=sign*.53+(v.co.y-sign*.53)*.58;v.co.z=.58+(v.co.z-.58)*.58
 bpy.context.view_layer.update()
 points=[ob.matrix_world@v.co for ob in gun.children if ob.type=='MESH' for v in ob.data.vertices]
 portx=max(p.x for p in points)+.02;minx=min(p.x for p in points)-.02;ports.append({'side':sign,'x':portx,'y':sign*.53,'z':.58,'width':.22,'height':.070,'visible_extension':.18})
 drive(gun,'location',0,'.20*t',[('t',root,'transform')])
 cut=box('TempThinHeadlightBore',((minx+portx+.25)/2,sign*.53,.58),(portx+.25-minx,.220,.070),None,0)
 subtract(bpy.data.objects['MA_FixedHoodShoulder_'+l],cut,'ThinRectangularCannonBore')
 # Thin body-coloured edge, never white surfaces. The hole remains open in road mode.
 for zz in [.542,.618]:box('MA_HeadlightPortRim',(portx,sign*.53,zz),(.010,.232,.006),purple,.002,root)
 for yy in [-.113,.113]:box('MA_HeadlightPortRim',(portx,sign*.53+yy,.58),(.010,.006,.070),purple,.002,root)
 gun['independence_note']='Parent Manta_Control, never MA_SlidingHood. 20cm travel, 18cm visible beyond fixed thin headlight port.'
# An interpreted fixed underlap closes seams optically without welding moving parts.
def oldwidth(x):
 k=[(.74,.33),(1.87,.305),(1.98,.325),(2.045,.54),(2.12,.54)]
 for (a,v),(b,w) in zip(k,k[1:]):
  if x<=b:return v+(w-v)*(x-a)/(b-a)
 return .54
def top(x,y):
 k=[(.74,.835),(1.17,.79),(1.75,.70),(2.12,.63)];z=k[-1][1]
 for (a,v),(b,w) in zip(k,k[1:]):
  if x<=b:z=v+(w-v)*(x-a)/(b-a);break
 t=max(0,min(1,(x-1.45)/.67));return z+.048*(1-(y/.70)**2)+.015*sin(pi*(x-.74)/1.38)-.135*t*t*(3-2*t)
for sign in [-1,1]:
 xs=seq(48,1.085,2.12);vv=[]
 for x in xs:
  w=oldwidth(x)
  for yy in [w-.018,w+.018]:vv.append((C(x),sign*yy,top(x,sign*yy)-.080))
 mesh('MA_HoodHiddenJointUnderlap',vv,[(i*2,i*2+1,i*2+3,i*2+2) for i in range(len(xs)-1)],purple,root,bevel=.002)
# Missiles and cassette rotate together to 30 degrees only after the bay clears.
launcher=bpy.data.objects['MA_TripleLauncherLift'];children=list(launcher.children)
tilt=empty('MA_TripleMissileElevation',(C(1.26),0,.645),launcher)
for ob in children:
 wm=ob.matrix_world.copy();ob.parent=tilt;ob.matrix_parent_inverse=tilt.matrix_world.inverted();ob.matrix_world=wm
q='min(1,max(0,(t-.86)/.14))'
drive(tilt,'rotation_euler',1,str(-pi/6)+'*'+q,[('t',root,'transform')]);tilt['deployed_elevation_degrees']=30.
# Soften manufactured edges without subdividing wheel openings into lumpy ovals.
for ob in bpy.data.collections['Manta_Vehicle'].objects:
 if ob.type!='MESH':continue
 for mod in ob.modifiers:
  if mod.type=='BEVEL':
   mod.segments=max(5,mod.segments)
   if ob.name.startswith(('MA_DoorBody','MA_Rocker','MA_RearLightPanel')):mod.width=min(.025,max(.018,mod.width))
   elif ob.name.startswith('MA_MainWing_'):mod.width=.016
# Re-solve the SAME articulated character for the recalibrated left-hand cockpit.
R['driving_pose']=0.;R['in_vehicle']=0.;R.update_tag();bpy.context.view_layer.update()
for b in R.pose.bones:
 for i in range(4):
  try:R.driver_remove('pose.bones["'+b.name+'"].rotation_quaternion',i)
  except:pass
 b.rotation_quaternion=(1,0,0,0)
bpy.context.view_layer.update()
def orient(name,start,end):
 b=R.pose.bones[name];rest=R.data.bones[name];q=(rest.tail_local-rest.head_local).rotation_difference(Vector(end)-Vector(start));m=(q.to_matrix()@rest.matrix_local.to_3x3()).to_4x4();m.translation=start;b.matrix=m;bpy.context.view_layer.update()
def limb(upper,lower,target,bend):
 a=R.pose.bones[upper].head.copy();axis=(Vector(target)-a).normalized();d=min((Vector(target)-a).length,R.data.bones[upper].length+R.data.bones[lower].length-.001);target=a+axis*d;l1=R.data.bones[upper].length;l2=R.data.bones[lower].length;x=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(max(0,l1*l1-x*x));v=Vector(bend);v=(v-axis*v.dot(axis)).normalized();el=a+axis*x+v*h;orient(upper,a,el);orient(lower,el,target)
for sign,l in [(1,'L'),(-1,'R')]:
 limb('thigh.'+l,'shin.'+l,(.73,sign*.105,.85),(0,0,1))
 limb('upper_arm.'+l,'forearm.'+l,(.48,sign*.13,1.34),(0,sign*.2,-1))
 b=R.pose.bones['foot.'+l];p=b.head.copy();orient(b.name,p,p+Vector((.15,0,-.02)))
 b=R.pose.bones['hand.'+l];p=b.head.copy();orient(b.name,p,p+Vector((.035,-sign*.045,.015)))
pose={b.name:list(b.rotation_quaternion) for b in R.pose.bones}
for b in R.pose.bones:
 val=pose[b.name];b.rotation_quaternion=(1,0,0,0)
 for i,v in enumerate(val):drive(b,'rotation_quaternion',i,str((1,0,0,0)[i])+'*(1-p)+'+str(v)+'*p',[('p',R,'driving_pose')])
root['hood_note']='Closed tight seams 1.5mm with fixed underlap, fixed rear quarter and side shoulders. Thin rectangular open headlight bores, short independent cannons. 30-degree missile cassette after geometric clearance.'
root['tail_support_note']='Two supports broad fore/aft (14/12/10cm nested sections), thin left/right (2.5/2.1/1.7cm); taller rear lamp faces. Board covers full nozzle envelope.'
(A/'headlight_ports_v14.json').write_text(json.dumps(ports,indent=2));(A/'vanessa_driving_pose_v14.json').write_text(json.dumps(pose,indent=2))
R['driving_pose']=1.;R['in_vehicle']=1.;R['mask_on']=False;R.update_tag();S.frame_set(121);S.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Manta_V14_Assembly.blend'),compress=True)
print('V14_CONSOLIDATED_SAVED')
