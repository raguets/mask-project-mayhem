"""Authorized realistic Brad interpretation; same weighted body in every pose."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
from mathutils.bvhtree import BVHTree
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Condor';B=P/'art_source/Brad_Turner';B.mkdir(exist_ok=True)
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
C=bpy.data.collections['BT_Character'];CURRENT=C;PARENT=None;R=bpy.data.objects['BradTurner_Rig'];root=bpy.data.objects['Condor_Control']
R.data=R.data.copy();R.data.name='BT_EditableSkeleton'
for f in list(R.animation_data.drivers):R.driver_remove(f.data_path,f.array_index)
R.animation_data.action=None
for b in R.pose.bones:
 b.rotation_mode='QUATERNION';b.rotation_quaternion=(1,0,0,0);b.location=(0,0,0);b.scale=(1,1,1)
R.parent=root;R.matrix_parent_inverse=Matrix.Identity(4);R.location=(-.17,0,-.10)
R['driving_pose']=1.;R['mask_on']=False;R['in_vehicle']=1.
R['reference_note']='Realistic human interpretation explicitly authorized 2026-11-12. Toy photos and cartoons inspected, no likeness of any real person.'
R['asset_version']='Brad Turner V1';R['anatomy_provenance']='Project CC0 anatomy basis via independently copied Calhoun V2, preserved original source.'
Y=material('BT_YellowFlightFabric',(.70,.41,.012),0,.64);RED=material('BT_BordeauxLeather',(.29,.009,.048),.05,.43);BLACK=material('BT_BlackLeather',(.008,.010,.013),.08,.44);HAIR=material('BT_DarkBrownHair',(.035,.014,.009),0,.61);SKIN=material('BT_InterpretedSkin',(.54,.32,.21),0,.49);GOLD=material('BT_Fasteners',(.50,.27,.055),.7,.28)
for m in [Y,RED]:
 ns=m.node_tree.nodes;n=ns.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=380;b=ns.new('ShaderNodeBump');b.inputs['Distance'].default_value=.0003;b.inputs['Strength'].default_value=.18;m.node_tree.links.new(n.outputs['Fac'],b.inputs['Height']);m.node_tree.links.new(b.outputs['Normal'],next(n for n in ns if n.type=='BSDF_PRINCIPLED').inputs['Normal'])
for o in list(C.all_objects):
 if o==R:continue
 o.name='BT_'+o.name.removeprefix('CB_')
 if o.type=='MESH':
  o.data=o.data.copy();o.data.name=o.name+'_Editable'
  if any(k in o.name for k in ['Harness','KneeGuard','Pauldron','FormedChestYoke','YellowBracer']):bpy.data.objects.remove(o,do_unlink=True);continue
  for mod in o.modifiers:
   if mod.type=='ARMATURE':mod.object=R
  if 'Head_Anatomical' in o.name:
   o.data.materials[0]=SKIN
   for v in o.data.vertices:
    p=v.co;p.y*=1-.06*math.exp(-((p.z-1.62)/.07)**2)
  elif any(k in o.name for k in ['Hair','Brow']):
   for i in range(len(o.data.materials)):o.data.materials[i]=HAIR
  elif any(k in o.name for k in ['Glove','Cuff']):
   for i in range(len(o.data.materials)):o.data.materials[i]=RED
  elif any(k in o.name for k in ['Boot','Belt']):
   for i in range(len(o.data.materials)):o.data.materials[i]=GOLD if 'Buckle' in o.name else BLACK
  elif not any(k in o.name for k in ['Eyeball','Iris']):
   for i in range(len(o.data.materials)):o.data.materials[i]=Y
 if o.animation_data:
  for f in o.animation_data.drivers:
   for v in f.driver.variables:
    for t in v.targets:
     if isinstance(t.id,bpy.types.Object) and t.id.type=='ARMATURE':t.id=R
 if o.type=='MESH' and o.data.shape_keys and o.data.shape_keys.animation_data:
  for f in o.data.shape_keys.animation_data.drivers:
   for v in f.driver.variables:
    for t in v.targets:
     if isinstance(t.id,bpy.types.Object) and t.id.type=='ARMATURE':t.id=R
def bind(o,bone='head',weights=None):
 if weights:
  for i,ww in enumerate(weights):
   for n,w in ww.items():
    g=o.vertex_groups.get(n) or o.vertex_groups.new(name=n);g.add([i],w,'REPLACE')
 else:o.vertex_groups.new(name=bone).add(list(range(len(o.data.vertices))),1,'REPLACE')
 o.parent=R;m=o.modifiers.new('BradEditableSkin','ARMATURE');m.object=R;m.use_deform_preserve_volume=True;return o
def vis(o,mask=False):
 for key in ['hide_render','hide_viewport']:drive(o,key,None,'1-m' if mask else 'm',[('m',R,'mask_on')])
def curve_mesh(o,bone='head'):
 dg=bpy.context.evaluated_depsgraph_get();me=bpy.data.meshes.new_from_object(o.evaluated_get(dg),depsgraph=dg);n=bpy.data.objects.new(o.name+'_Mesh',me);CURRENT.objects.link(n);bpy.data.objects.remove(o,do_unlink=True);return bind(n,bone)
# Fitted chest marking copied from actual cloth surface, retaining weights.
suit=bpy.data.objects['BT_ContinuousFlightSuit'];sv=suit.data.vertices;sf=suit.data.polygons;tree=BVHTree.FromPolygons([v.co for v in sv],[list(f.vertices) for f in sf])
def panel(name,yr,zr,mat):
 vv=[];ww=[];ff=[];N=19
 for y in seq(18,*yr):
  for z in seq(18,*zr):
   hit=tree.ray_cast(Vector((.4,y,z)),Vector((-1,0,0)),.8)
   if not hit[0]:hit=tree.find_nearest(Vector((.12,y,z)))
   p,n,i,d=hit;vv.append(tuple(p+n*.009));nearest=min((sv[k] for k in sf[i].vertices),key=lambda v:(v.co-p).length_squared);ww.append({suit.vertex_groups[g.group].name:g.weight for g in nearest.groups})
 for i in range(18):
  for j in range(18):ff.append((i*N+j,(i+1)*N+j,(i+1)*N+j+1,i*N+j+1))
 o=bind(mesh(name,vv,ff,mat,smooth=True),weights=ww);o.modifiers.new('FabricMarkThickness','SOLIDIFY').thickness=.002
panel('BT_BordeauxChestPanel',(-.105,.105),(1.20,1.395),RED)
for z in [1.13,1.16]:panel('BT_ChestStripe_'+str(z),(-.10,.10),(z,z+.013),RED)
for side in [-1,1]:
 bind(box('BT_CollarFastener',(.043,side*.072,1.475),(.025,.023,.023),RED,.008),'neck')
 # Sunglasses retain the anatomical eyes beneath them.
 o=bind(patch('BT_SunglassLens_'+str(side),seq(12),seq(8),lambda u,t:(.118+.012*sin(pi*u),side*(.013+.080*u),1.681+.038*t-.008*sin(pi*u)),BLACK,thick=.003,sub=1));vis(o)
 o=curve_mesh(path('BT_SunglassTemple_'+str(side),[(.122,side*.090,1.710),(.015,side*.115,1.712),(-.035,side*.106,1.69)],.004,BLACK));vis(o)
o=bind(box('BT_SunglassBridge',(.133,0,1.707),(.012,.032,.007),BLACK,.003));vis(o)
# Hocus Pocus: open lower frame, flared side cheeks, broad dark goggles.
M=collection('BT_Mask');CURRENT=M
SHELL=material('BT_HocusPocusYellow',(.82,.48,.012),.20,.31);DARK=material('BT_HocusPocusVisor',(.008,.016,.025),.48,.14)
rows=[(1.59,.105,.116),(1.67,.137,.138),(1.76,.138,.137),(1.82,.105,.12),(1.855,.025,.035)]
vv=[];ff=[];N=64
for z,rx,ry in rows:
 for i in range(N):a=2*pi*i/N;vv.append((-.014+rx*cos(a),ry*sin(a),z))
for j in range(len(rows)-1):
 for i in range(N):
  a=2*pi*(i+.5)/N
  if j<2 and cos(a)>.3:continue
  ff.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
o=bind(mesh('BT_Hocus_Dome',vv,ff,SHELL,smooth=True));o.modifiers.new('ShellWall','SOLIDIFY').thickness=.004
bind(patch('BT_Hocus_Goggles',seq(24,-1,1),seq(12),lambda u,t:(.143+.024*(1-u*u),.131*u,1.686+.083*t-.015*abs(u)),DARK,thick=.004,sub=1))
poly=[(.167,-.070,1.699),(.167,.070,1.699),(.193,.051,1.645),(.176,.055,1.607),(.176,-.055,1.607),(.193,-.051,1.645)]
o=bind(mesh('BT_Hocus_Respirator',poly,[tuple(range(6))],SHELL,bevel=.004));o.modifiers.new('RespiratorWall','SOLIDIFY').thickness=.009
for y in [-.033,0,.033]:bind(tube('BT_Hocus_BreathingPort',(.193,y,1.641),(.201,y,1.641),.008,DARK,N=16))
for side in [-1,1]:
 poly=[(.12,side*.12,1.72),(.16,side*.10,1.65),(.14,side*.15,1.53),(.08,side*.17,1.51),(-.07,side*.13,1.58),(-.075,side*.14,1.72)]
 o=bind(mesh('BT_Hocus_FlaredCheek_'+str(side),poly,[tuple(range(6))],SHELL,bevel=.006));o.modifiers.new('CheekWall','SOLIDIFY').thickness=.009
 bind(box('BT_Hocus_EarInset',(-.025,side*.149,1.71),(.065,.017,.10),DARK,.008))
 bind(box('BT_Hocus_LowerFrameArm',(.135,side*.101,1.525),(.06,.023,.17),SHELL,.012))
bind(box('BT_Hocus_OpenLowerFrame',(.137,0,1.451),(.063,.215,.026),SHELL,.009))
bind(box('BT_Hocus_UpperFrameCrosspiece',(.146,0,1.558),(.050,.205,.026),SHELL,.008))
bind(box('BT_Hocus_CrownRidge',(-.004,0,1.849),(.17,.020,.020),SHELL,.007))
for o in M.all_objects:vis(o,True)
# Compute articulated riding pose, keeping original lengths and editable weighted meshes.
CURRENT=C
R['driving_pose']=0.;bpy.context.view_layer.update()
def orient(bname,start,end):
 b=R.pose.bones[bname];rest=R.data.bones[bname];q=(rest.tail_local-rest.head_local).rotation_difference(Vector(end)-Vector(start));mat=(q.to_matrix()@rest.matrix_local.to_3x3()).to_4x4();mat.translation=start;b.matrix=mat;bpy.context.view_layer.update()
def limb(upper,lower,target,bend):
 a=R.pose.bones[upper].head.copy();t=Vector(target);L1=R.data.bones[upper].length;L2=R.data.bones[lower].length;d=(t-a).length;axis=(t-a).normalized();d=min(d,L1+L2-.001);t=a+axis*d
 x=(L1*L1-L2*L2+d*d)/(2*d);h=math.sqrt(max(0,L1*L1-x*x));v=Vector(bend);v=(v-axis*v.dot(axis)).normalized();el=a+axis*x+v*h
 orient(upper,a,el);orient(lower,el,t)
# Lean spine forward slightly to meet controls without overstretching arms.
sp=R.pose.bones['spine'];sp.rotation_quaternion=sp.bone.matrix_local.to_quaternion().inverted()@Quaternion((0,1,0),.24)@sp.bone.matrix_local.to_quaternion();bpy.context.view_layer.update()
for side,label in [(1,'L'),(-1,'R')]:
 limb('thigh.'+label,'shin.'+label,(.29,side*.30,.45),(1,side*.7,0))
 limb('upper_arm.'+label,'forearm.'+label,(.56,side*.29,1.06),(0,side*.3,-1))
 # Feet return toward level after lower-leg rotation.
 b=R.pose.bones['foot.'+label];pos=b.head.copy();orient(b.name,pos,pos+Vector((.14,0,-.025)))
pose={b.name:list(b.rotation_quaternion) for b in R.pose.bones}
for b in R.pose.bones:
 q=Quaternion(pose[b.name]);b.rotation_quaternion=(1,0,0,0)
 for i,value in enumerate(q):drive(b,'rotation_quaternion',i,str((1,0,0,0)[i])+'*(1-p)+'+str(value)+'*p',[('p',R,'driving_pose')])
drive(R,'location',0,'-0.17*v',[('v',R,'in_vehicle')]);drive(R,'location',2,'v*(-0.10-0.10*t)',[('v',R,'in_vehicle'),('t',root,'transform')])
R['driving_pose']=1.;R['mask_on']=True;R.update_tag();bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
(A/'brad_riding_pose.json').write_text(json.dumps(pose,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Condor_V2_Assembly.blend'),compress=True)
print('BRAD_AND_HOCUS_BUILT',len(C.all_objects),len(M.all_objects))
