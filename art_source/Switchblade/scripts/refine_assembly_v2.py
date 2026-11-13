import bpy,math,json
from pathlib import Path
from mathutils import Vector,Quaternion
from mathutils.bvhtree import BVHTree
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Switchblade'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
root=bpy.data.objects['Switchblade_Control'];R=bpy.data.objects['MilesMayhem_Rig'];s=bpy.context.scene
s.frame_set(121);R['driving_pose']=0.;R['in_vehicle']=0.;R['mask_on']=False;R.update_tag();bpy.context.view_layer.update()
# Correct folded-wing profile: root matches body height; tips follow the rising tail.
for side in [-1,1]:
 wing=bpy.data.objects['SB_MainWing_'+str(side)]
 for v in wing.data.vertices:
  p=v.co;t=max(0,min(1,(abs(p.y)-.73)/2.60))
  if p.x<-.80:p.x+=.50*(1-t)+.80*t
  else:p.x+=.80*t
 for o in list(bpy.data.objects):
  if any(k in o.name for k in ['WingOrangeFlash_'+str(side),'WingRedFlash_'+str(side),'WingPanelLine_'+str(side)]):
   if o.type=='MESH':
    for v in o.data.vertices:v.co.x+=.80*max(0,min(1,(abs(v.co.y)-.73)/2.60))
   if o.type=='CURVE':
    for sp in o.data.splines:
     for p in sp.points:p.co.x+=.80*max(0,min(1,(abs(p.co.y)-.73)/2.60))
   if o.type=='MESH':
    n=o.copy();n.data=o.data.copy();n.name=o.name+'_Underside';bpy.data.collections['Switchblade_Vehicle'].objects.link(n)
    for v in n.data.vertices:v.co.z=2*1.45-v.co.z
 # Shortened actual blades clear the raised vertical tail.
 for o in [bpy.data.objects['SB_MainRotorBlade_'+str(side)],bpy.data.objects['SB_BladeTipMark_'+str(side)]]:
  for v in o.data.vertices:
   if v.co.x<-.5:v.co.x=-.5+(v.co.x+.5)*.83
# Remove white flickering panels and regenerate on evaluated cloth at rest.
C=bpy.data.collections['Miles_Character'];CURRENT=C;PARENT=None
NAVY=bpy.data.materials['MM_NavalUniform'];WHITE=bpy.data.materials['MM_Shirt'];BLACK=bpy.data.materials['MM_BootLeather'];GREY=bpy.data.materials['MM_SilverGreyHair']
def bind(o,bone='head',weights=None):
 if weights:
  for i,ww in enumerate(weights):
   for n,w in ww.items():g=o.vertex_groups.get(n) or o.vertex_groups.new(name=n);g.add([i],w,'REPLACE')
 else:o.vertex_groups.new(name=bone).add(list(range(len(o.data.vertices))),1,'REPLACE')
 o.parent=R;m=o.modifiers.new('MilesEditableSkin','ARMATURE');m.object=R;m.use_deform_preserve_volume=True;return o
def vis(o):
 for k in ['hide_render','hide_viewport']:drive(o,k,None,'m',[('m',R,'mask_on')])
suit=bpy.data.objects['MM_ContinuousFlightSuit'];dg=bpy.context.evaluated_depsgraph_get();e=suit.evaluated_get(dg);em=e.to_mesh();cloth=BVHTree.FromPolygons([v.co for v in em.vertices],[tuple(f.vertices) for f in em.polygons]);e.to_mesh_clear()
base=BVHTree.FromPolygons([v.co for v in suit.data.vertices],[tuple(f.vertices) for f in suit.data.polygons])
for name in ['MM_ShirtFront','MM_NarrowTie','MM_JacketLapel_-1','MM_JacketLapel_1']:
 o=bpy.data.objects[name]
 for v in o.data.vertices:
  hit=cloth.ray_cast(Vector((.5,v.co.y,v.co.z)),Vector((-1,0,0)),1.)
  if hit[0]:v.co=hit[0]+hit[1]*.006
 o.data.update()
# Replace angular inherited scalp with close fitted swept-back hair based on this head.
for o in list(C.all_objects):
 if 'SweptBackScalp' in o.name or 'SweptHairStrand' in o.name:bpy.data.objects.remove(o,do_unlink=True)
head=bpy.data.objects['MM_Head_AnatomicalSurface'];head.data.update();vv=[];ff=[];mapping={}
for face in head.data.polygons:
 p=face.center
 if not (p.z>1.748+.015*max(0,p.x/.12) or (p.x<-.025 and p.z>1.68)):continue
 ids=[]
 for k in face.vertices:
  if k not in mapping:
   v=head.data.vertices[k];q=v.co+v.normal*.004;mapping[k]=len(vv);vv.append(tuple(q))
  ids.append(mapping[k])
 ff.append(ids)
o=bind(mesh('MM_GreySweptScalp',vv,ff,GREY,smooth=True));vis(o)
ht=BVHTree.FromPolygons([Vector(v) for v in vv],ff)
for j in range(25):
 y=-.10+.2*j/24;pts=[]
 for x in seq(24,.11,-.11):
  hit=ht.ray_cast(Vector((x,y,2.1)),Vector((0,0,-1)),.5)
  if hit[0]:pts.append(tuple(hit[0]+hit[1]*.0015))
 if len(pts)>5:
  cu=path('MM_GreyHairGroove',pts,.0008,GREY);me=bpy.data.meshes.new_from_object(cu.evaluated_get(dg),depsgraph=dg);o=bpy.data.objects.new(cu.name+'_Mesh',me);C.objects.link(o);bpy.data.objects.remove(cu,do_unlink=True);bind(o);vis(o)
# Replace long shell with a compact helmet and separate open-neck shoulder gorget.
M=bpy.data.collections['Miles_ViperMask'];CURRENT=M
bpy.data.objects.remove(bpy.data.objects['MM_Viper_ContinuousShell'],do_unlink=True)
SHELL=bpy.data.materials['MM_ViperNavyShell'];EDGE=bpy.data.materials['SB_EdgeBlue']
def rings(name,rows,bone,front_dip=0):
 vv=[];ff=[];N=64
 for j,(z,rx,ry) in enumerate(rows):
  for i in range(N):
   a=2*pi*i/N;x=-.012+rx*math.copysign(abs(cos(a))**.65,cos(a));y=ry*math.copysign(abs(sin(a))**.75,sin(a));zz=z-front_dip*max(0,cos(a)) if j==len(rows)-1 else z;vv.append((x,y,zz))
 for j in range(len(rows)-1):
  for i in range(N):ff.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
 if name.endswith('Helmet'):ff.append(tuple((len(rows)-1)*N+i for i in range(N)))
 o=bind(mesh(name,vv,ff,SHELL,smooth=True),bone);o.modifiers.new('ManufacturedShellWall','SOLIDIFY').thickness=.005
 return o
helmet=rings('MM_Viper_CompactHelmet',[(1.585,.11,.108),(1.62,.143,.139),(1.72,.153,.150),(1.80,.143,.146),(1.86,.095,.11),(1.886,.01,.018)],'head')
gorget=rings('MM_Viper_ShoulderGorget',[(1.405,.215,.235),(1.44,.206,.225),(1.52,.14,.163)],'spine',.055)
for o in [helmet,gorget]:
 for k in ['hide_render','hide_viewport']:drive(o,k,None,'1-m',[('m',R,'mask_on')])
# Add visor edge and cheek seams to emphasize faceted front, not a cylindrical sleeve.
for side in [-1,1]:
 pts=[(.141,side*.135,1.75),(.158,side*.123,1.67),(.139,side*.085,1.60)]
 cu=path('MM_Viper_CheekRim',pts,.006,EDGE);me=bpy.data.meshes.new_from_object(cu.evaluated_get(dg),depsgraph=dg);o=bpy.data.objects.new(cu.name+'_Mesh',me);M.objects.link(o);bpy.data.objects.remove(cu,do_unlink=True);bind(o)
 for k in ['hide_render','hide_viewport']:drive(o,k,None,'1-m',[('m',R,'mask_on')])
# Recalculate a genuine bent-knee seated pose, with unchanged skeleton lengths.
for f in list(R.animation_data.drivers):
 if f.data_path.startswith('pose.bones'):R.driver_remove(f.data_path,f.array_index)
for b in R.pose.bones:b.rotation_quaternion=(1,0,0,0)
bpy.context.view_layer.update()
def orient(name,start,end):
 b=R.pose.bones[name];rest=R.data.bones[name];q=(rest.tail_local-rest.head_local).rotation_difference(Vector(end)-Vector(start));mat=(q.to_matrix()@rest.matrix_local.to_3x3()).to_4x4();mat.translation=start;b.matrix=mat;bpy.context.view_layer.update()
def limb(upper,lower,target,bend):
 a=R.pose.bones[upper].head.copy();axis=(Vector(target)-a).normalized();l1=R.data.bones[upper].length;l2=R.data.bones[lower].length;d=min((Vector(target)-a).length,l1+l2-.001);target=a+axis*d;x=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(max(0,l1*l1-x*x));v=Vector(bend);v=(v-axis*v.dot(axis)).normalized();el=a+axis*x+v*h;orient(upper,a,el);orient(lower,el,target)
sp=R.pose.bones['spine'];sp.rotation_quaternion=sp.bone.matrix_local.to_quaternion().inverted()@Quaternion((0,1,0),.12)@sp.bone.matrix_local.to_quaternion();bpy.context.view_layer.update()
for side,label in [(1,'L'),(-1,'R')]:
 limb('thigh.'+label,'shin.'+label,(.58,side*.18,.70),(1,side*.2,0))
 limb('upper_arm.'+label,'forearm.'+label,(.47,side*.24,1.20),(0,side*.3,-1))
 for name,vec in [('foot.'+label,(.14,0,-.015)),('hand.'+label,(.075,0,.01))]:
  b=R.pose.bones[name];pos=b.head.copy();orient(name,pos,pos+Vector(vec))
pose={b.name:list(b.rotation_quaternion) for b in R.pose.bones}
for b in R.pose.bones:
 for i,val in enumerate(pose[b.name]):drive(b,'rotation_quaternion',i,str((1,0,0,0)[i])+'*(1-p)+'+str(val)+'*p',[('p',R,'driving_pose')])
for name in ['SB_SeatBase']:bpy.data.objects[name].location.z-=.08
for o in bpy.data.collections['Switchblade_Interior'].all_objects:
 if o.name.startswith('SB_RudderPedal'):o.location.x-=.38
 if o.name in ['SB_FlightYoke','SB_ControlColumn']:o.location.x-=.20
root.update_tag();R['in_vehicle']=1.;R['driving_pose']=1.;R['mask_on']=True;R.update_tag();s.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Switchblade_V2_Assembly.blend'),compress=True)
(A/'miles_seated_pose_v2.json').write_text(json.dumps(pose,indent=2))
print('REFINED_V2_SAVED')
