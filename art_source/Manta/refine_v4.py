import bpy,math,json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Manta';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
R=bpy.data.objects['VanessaWarfield_Rig'];body=bpy.data.objects['VW_ContinuousBodyAndFace'];R['driving_pose']=0.;R['in_vehicle']=0.;R.update_tag();bpy.context.view_layer.update()
# Restore float interpolation. Integer ID properties had quantized the first timeline.
root=bpy.data.objects['Manta_Control'];root['transform']=0.
act=root.animation_data.action
for layer in act.layers:
 for strip in layer.strips:
  for bag in strip.channelbags:
   for fc in bag.fcurves:
    fc.update_autoflags(root)
    for kp in fc.keyframe_points:kp.interpolation='LINEAR'
# Include fingertips in the arm region instead of assigning low tips to leg bones.
def segdist(p,b):
 a=b.head_local;v=b.tail_local-a;t=max(0,min(1,(p-a).dot(v)/v.length_squared));return (p-a-v*t).length
N=len(body.data.vertices);G=len(body.vertex_groups);W=np.zeros((N,G))
for v in body.data.vertices:
 p=v.co;side='L' if p.y>0 else 'R'
 if p.z>1.42:names=['neck','head','chest']
 elif abs(p.y)>.215 and p.z>.60:names=['chest','upper_arm.'+side,'forearm.'+side,'hand.'+side]
 elif p.z<.92:names=['pelvis','thigh.'+side,'shin.'+side,'foot.'+side]
 else:names=['pelvis','spine','chest','neck']
 ranked=sorted([(segdist(p,R.data.bones[n]),n) for n in names])[:2];vals=[1/(d+.015)**5 for d,n in ranked];total=sum(vals)
 for (d,n),w in zip(ranked,vals):W[v.index,body.vertex_groups[n].index]=w/total
ed=np.array([tuple(e.vertices) for e in body.data.edges]);a=ed[:,0];b=ed[:,1];deg=np.bincount(np.r_[a,b],minlength=N);den=np.maximum(1,deg)[:,None]
for k in range(35):
 avg=np.zeros_like(W);np.add.at(avg,a,W[b]);np.add.at(avg,b,W[a]);W=.55*W+.45*avg/den
W/=np.maximum(1e-12,W.sum(axis=1))[:,None]
for g in body.vertex_groups:g.remove(list(range(N)))
for i,ww in enumerate(W):
 for j in np.flatnonzero(ww>.0001):body.vertex_groups[int(j)].add([i],float(ww[j]),'REPLACE')
# Tailored accessory surfaces project to the actual rest-body surface.
tree=BVHTree.FromPolygons([v.co for v in body.data.vertices],[list(f.vertices) for f in body.data.polygons])
for n in ['VW_Belt','VW_CyanCollar_Mesh','VW_CyanCollar_Mesh.001','WH_ConnectedFlaredCollar']:
 ob=bpy.data.objects.get(n)
 if not ob:continue
 for v in ob.data.vertices:
  if n.startswith('WH_') and v.co.z>1.37:continue
  q,no,idx,d=tree.find_nearest(v.co)
  if q is not None:v.co=q+no*(.009 if n.startswith('WH') else .006)
# Finished foot coverings hide toes, retain the same articulated body under them.
CURRENT=bpy.data.collections['Vanessa_Character'];PARENT=None
red=bpy.data.materials['VW_RedLeather'];black=bpy.data.materials['VW_BlackLeather'];silver=bpy.data.materials['VW_SilverBuckle']
def bind(o,bone):
 o.vertex_groups.new(name=bone).add(list(range(len(o.data.vertices))),1,'REPLACE');o.parent=R;m=o.modifiers.new('VanessaEditableSkin','ARMATURE');m.object=R;m.use_deform_preserve_volume=True;return o
for s,l in [(1,'L'),(-1,'R')]:
 vv=[];ss=[(-.08,.018,.065),(-.045,.055,.14),(.025,.060,.13),(.115,.056,.095),(.183,.035,.065),(.205,.003,.04)];K=32
 for x,w,top in ss:
  for i in range(K):
   a=i*2*pi/K;vv.append((x,s*.105+w*cos(a),.025+(top-.025)*(.5+.5*sin(a))))
 ff=[tuple(reversed(range(K))),tuple((len(ss)-1)*K+i for i in range(K))]+[(j*K+i,j*K+(i+1)%K,(j+1)*K+(i+1)%K,(j+1)*K+i) for j in range(len(ss)-1) for i in range(K)]
 bind(mesh('VW_RedBootFoot_'+l,vv,ff,red,smooth=True,bevel=.005),'foot.'+l)
 bind(box('VW_BootSole_'+l,(.06,s*.105,.018),(.28,.113,.022),black,.02),'foot.'+l)
 # Continuous boot shin follows the actual leg and carries a clean rounded cuff.
 for f in body.data.polygons:
  p=sum((body.data.vertices[i].co for i in f.vertices),Vector())/len(f.vertices)
  if abs(p.y)>.235 and p.z<1.18 and p.z>.60:f.material_index=2
  if p.z<.52:f.material_index=2
# Add fine fabric relief and reduce plastic hair reflections.
for mat in [bpy.data.materials['VW_RoyalBlueSuit'],bpy.data.materials['VW_CyanSleeve']]:
 ns=mat.node_tree.nodes;links=mat.node_tree.links;p=next(n for n in ns if n.type=='BSDF_PRINCIPLED');p.inputs['Roughness'].default_value=.67;n=ns.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=400;bump=ns.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.00025;bump.inputs['Strength'].default_value=.18;links.new(n.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],p.inputs['Normal'])
for n in ['VW_AuburnHair','VW_CopperHairGlints']:
 mat=bpy.data.materials[n];p=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Metallic'].default_value=0;p.inputs['Roughness'].default_value=.63;p.inputs['Base Color'].default_value=(.075,.005,.003,1);mat.diffuse_color=(.075,.005,.003,1)
# Enlarge panel contact strips to close Whip's moved-front-to-side seams.
for ob in bpy.data.collections['Whip_Mask'].objects:
 if ob.type=='MESH' and ob.name.startswith('WH_SideCheek'):
  for v in ob.data.vertices:
   if v.co.x>.14:v.co.x+=.025
# Lower interpreted cabin floor and seat to accommodate the real evaluated helmet.
for n,dz in [('MA_CabinFloor',-.12),('MA_Underbody',-.06)]:
 for v in bpy.data.objects[n].data.vertices:v.co.z+=dz
for ob in bpy.data.collections['Manta_Interior'].objects:
 if ob.type=='MESH' and ob.name.startswith('MA_SeatBase'):
  for v in ob.data.vertices:v.co.z=.335+(v.co.z-.50)*.65
 if ob.type=='MESH' and ob.name.startswith('MA_SeatBack'):
  for v in ob.data.vertices:v.co.z=.70+(v.co.z-.78)*1.18
 if ob.type=='MESH' and ob.name.startswith('MA_Pedal'):
  for v in ob.data.vertices:v.co.z-=.10
# Re-solve the same skeleton for the lower seat. Reachable hand/foot targets.
for b in R.pose.bones:
 for i in range(4):
  try:R.driver_remove('pose.bones["'+b.name+'"].rotation_quaternion',i)
  except:pass
 b.rotation_quaternion=(1,0,0,0)
bpy.context.view_layer.update()
def orient(name,start,end):
 b=R.pose.bones[name];rest=R.data.bones[name];q=(rest.tail_local-rest.head_local).rotation_difference(Vector(end)-Vector(start));mat=(q.to_matrix()@rest.matrix_local.to_3x3()).to_4x4();mat.translation=start;b.matrix=mat;bpy.context.view_layer.update()
def limb(upper,lower,target,bend):
 a=R.pose.bones[upper].head.copy();axis=(Vector(target)-a).normalized();d=min((Vector(target)-a).length,R.data.bones[upper].length+R.data.bones[lower].length-.001);target=a+axis*d;l1=R.data.bones[upper].length;l2=R.data.bones[lower].length;x=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(max(0,l1*l1-x*x));v=Vector(bend);v=(v-axis*v.dot(axis)).normalized();el=a+axis*x+v*h;orient(upper,a,el);orient(lower,el,target)
for s,l in [(1,'L'),(-1,'R')]:
 limb('thigh.'+l,'shin.'+l,(.69,s*.105,.85),(0,0,1))
 limb('upper_arm.'+l,'forearm.'+l,(.42,s*.13,1.34),(0,s*.2,-1))
 b=R.pose.bones['foot.'+l];p=b.head.copy();orient(b.name,p,p+Vector((.15,0,-.02)))
 b=R.pose.bones['hand.'+l];p=b.head.copy();orient(b.name,p,p+Vector((.035,-s*.045,.015)))
pose={b.name:list(b.rotation_quaternion) for b in R.pose.bones}
for b in R.pose.bones:
 q=pose[b.name];b.rotation_quaternion=(1,0,0,0)
 for i,v in enumerate(q):drive(b,'rotation_quaternion',i,str((1,0,0,0)[i])+'*(1-p)+'+str(v)+'*p',[('p',R,'driving_pose')])
R.animation_data.drivers.find('location',index=2).driver.expression='-.49*v'
R['driving_pose']=1.;R['in_vehicle']=1.;R['mask_on']=False;R.update_tag();S.frame_set(61);bpy.context.view_layer.update();print('MIDPOINT',root['transform']);S.frame_set(1)
(A/'vanessa_driving_pose_v4.json').write_text(json.dumps(pose,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Manta_V4_Assembly.blend'),compress=True)
print('V4_SAVED')
