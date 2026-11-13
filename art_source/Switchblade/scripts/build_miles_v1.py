"""MCP only: independently copied CC0-derived project anatomy, adapted to Miles."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
from mathutils.bvhtree import BVHTree
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Switchblade'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
root=bpy.data.objects['Switchblade_Control']
edge=bpy.data.materials['SB_EdgeBlue']
with bpy.data.libraries.load(str(P/'art_source/Calhoun_Burns/CalhounBurns_V2.blend'),link=False) as (src,dst):
 dst.collections=['CB_Character']
C=dst.collections[0];bpy.context.scene.collection.children.link(C);C.name='Miles_Character';CURRENT=C;PARENT=None
R=next(o for o in C.all_objects if o.type=='ARMATURE');R.name='MilesMayhem_Rig';R.data=R.data.copy();R.data.name='Miles_EditableSkeleton'
for f in list(R.animation_data.drivers):R.driver_remove(f.data_path,f.array_index)
R.animation_data.action=None;R.parent=None;R.matrix_parent_inverse=Matrix.Identity(4);R.location=(0,0,0)
for b in R.pose.bones:b.rotation_mode='QUATERNION';b.rotation_quaternion=(1,0,0,0);b.location=(0,0,0);b.scale=(1,1,1)
R['driving_pose']=0.;R['mask_on']=False;R['in_vehicle']=0.
R['reference_note']='Realistic interpretation authorized 2026-11-13, supplied Miles illustration and figurines. No likeness to a particular real person.'
R['anatomy_provenance']='Independent copy of project CC0-derived Calhoun basis; Blender Human Base Meshes, see art_source/AnatomyBase/README.md. Original unchanged.'
NAVY=material('MM_NavalUniform',(.015,.028,.065),0,.65);CYAN=material('MM_LightBlueLeather',(.07,.37,.52),0,.46)
GOLD=material('MM_GoldBraid',(.63,.34,.055),.75,.30);BLACK=material('MM_BootLeather',(.009,.013,.019),.05,.39)
GREY=material('MM_SilverGreyHair',(.25,.29,.31),.08,.53);SKIN=material('MM_InterpretedSkin',(.55,.32,.20),0,.48)
WHITE=material('MM_Shirt',(.63,.70,.73),0,.67)
for o in list(C.all_objects):
 if o==R:continue
 o.name='MM_'+o.name.removeprefix('CB_')
 if any(k in o.name for k in ['Harness','KneeGuard','YellowBracer','Pauldron','ChestYoke','OrangeGaiter']):bpy.data.objects.remove(o,do_unlink=True);continue
 if o.type=='MESH':
  o.data=o.data.copy();o.data.name=o.name+'_Editable'
  for m in o.modifiers:
   if m.type=='ARMATURE':m.object=R
  mat=None
  if 'Head_Anatomical' in o.name:mat=SKIN
  elif any(k in o.name for k in ['Hair','Scalp','Brow']):mat=GREY
  elif any(k in o.name for k in ['Glove','Cuff','Belt']):mat=CYAN
  elif 'Boot' in o.name:mat=BLACK
  elif not any(k in o.name for k in ['Eyeball','Iris']):mat=NAVY
  if mat:
   for i in range(len(o.data.materials)):o.data.materials[i]=GOLD if 'Buckle' in o.name else mat
  # Broader abdomen/jaw for Miles, smoothly tapered to preserve neck and limbs.
  for v in o.data.vertices:
   p=v.co
   if 'ContinuousFlightSuit' in o.name:
    w=math.exp(-((p.z-1.17)/.22)**4)*max(0,1-(abs(p.y)/.34)**4)
    p.y*=1+.13*w
    if p.x>0:p.x+=.028*w
   if 'Head_Anatomical' in o.name:
    w=math.exp(-((p.z-1.63)/.075)**2);p.y*=1+.12*w
    if p.x>0:p.x+=.009*w
  o.data.update()
 if o.animation_data:
  for f in o.animation_data.drivers:
   for var in f.driver.variables:
    for t in var.targets:
     if isinstance(t.id,bpy.types.Object) and t.id.type=='ARMATURE':t.id=R
 if o.type=='MESH' and o.data.shape_keys and o.data.shape_keys.animation_data:
  for f in o.data.shape_keys.animation_data.drivers:
   for var in f.driver.variables:
    for t in var.targets:
     if isinstance(t.id,bpy.types.Object) and t.id.type=='ARMATURE':t.id=R

def bind(o,bone='head',weights=None):
 if weights:
  for i,ww in enumerate(weights):
   total=sum(ww.values()) or 1
   for n,w in ww.items():g=o.vertex_groups.get(n) or o.vertex_groups.new(name=n);g.add([i],w/total,'REPLACE')
 else:o.vertex_groups.new(name=bone).add(list(range(len(o.data.vertices))),1,'REPLACE')
 o.parent=R;m=o.modifiers.new('MilesEditableSkin','ARMATURE');m.object=R;m.use_deform_preserve_volume=True;return o
def vis(o,mask=False):
 for k in ['hide_render','hide_viewport']:drive(o,k,None,'1-m' if mask else 'm',[('m',R,'mask_on')])
def cmesh(o,bone='head'):
 dg=bpy.context.evaluated_depsgraph_get();me=bpy.data.meshes.new_from_object(o.evaluated_get(dg),depsgraph=dg);n=bpy.data.objects.new(o.name+'_Mesh',me);CURRENT.objects.link(n);bpy.data.objects.remove(o,do_unlink=True);return bind(n,bone)

# Project uniform panels onto the actual weighted garment, retaining its deformation.
suit=bpy.data.objects['MM_ContinuousFlightSuit'];sv=suit.data.vertices;sf=suit.data.polygons
tree=BVHTree.FromPolygons([v.co for v in sv],[list(f.vertices) for f in sf])
def fitted(name,corners,mat):
 vv=[];ww=[];ff=[];N=17
 for i in range(N):
  t=i/(N-1);a=Vector(corners[0]).lerp(Vector(corners[3]),t);b=Vector(corners[1]).lerp(Vector(corners[2]),t)
  for j in range(N):
   p=a.lerp(b,j/(N-1));hit=tree.ray_cast(Vector((.5,p.y,p.z)),Vector((-1,0,0)),1.)
   if hit[0] is None:hit=tree.find_nearest(p)
   q,n,idx,d=hit;vv.append(tuple(q+n*.007));v=min((sv[k] for k in sf[idx].vertices),key=lambda v:(v.co-q).length_squared);ww.append({suit.vertex_groups[g.group].name:g.weight for g in v.groups})
 for i in range(N-1):
  for j in range(N-1):ff.append((i*N+j,i*N+j+1,(i+1)*N+j+1,(i+1)*N+j))
 o=bind(mesh(name,vv,ff,mat,smooth=True),weights=ww);o.modifiers.new('TailoredPanelThickness','SOLIDIFY').thickness=.002;return o
fitted('MM_ShirtFront',[(.1,-.065,1.47),(.1,.065,1.47),(.1,.045,1.28),(.1,-.045,1.28)],WHITE)
for s in [-1,1]:
 fitted('MM_JacketLapel_'+str(s),[(.1,s*.065,1.47),(.1,s*.15,1.42),(.1,s*.08,1.28),(.1,s*.018,1.34)],NAVY)
 bind(box('MM_GoldEpaulette',(-.01,s*.19,1.46),(.13,.085,.025),GOLD,.012),'upper_arm.'+('L' if s==1 else 'R'))
 for z in [1.07,1.15,1.23]:bind(tube('MM_JacketButton',(.18,s*.035,z),(.188,s*.035,z),.012,GOLD,N=20),'spine')
fitted('MM_NarrowTie',[(.1,-.018,1.45),(.1,.018,1.45),(.1,.027,1.30),(.1,-.027,1.30)],BLACK)
for y in [-.13,-.08,-.03]:
 bind(box('MM_MedalRibbon',(.18,y,1.34),(.018,.035,.015),GOLD,.004),'spine')
 bind(tube('MM_Medal',(.185,y,1.305),(.196,y,1.305),.014,GOLD,N=20),'spine')
for k in range(3):
 o=cmesh(path('MM_ShoulderAiguillette',[(.04,.19,1.46),(.16,.21+k*.006,1.37),(.20,.17+k*.006,1.23),(.19,.10,1.22),(.17,.08,1.34)],.004,GOLD),'spine')
# Distinctive moustache, formed over the preserved anatomical upper lip.
head=bpy.data.objects['MM_Head_AnatomicalSurface'];ht=BVHTree.FromPolygons([v.co for v in head.data.vertices],[list(f.vertices) for f in head.data.polygons])
vv=[];ff=[]
for i in range(37):
 y=-.063+i*.126/36;u=y/.063
 bottom=1.627-.018*abs(u)**1.5;top=1.653-.015*abs(u)
 for j in range(5):
  z=bottom+(top-bottom)*j/4;hit=ht.ray_cast(Vector((.4,y,z)),Vector((-1,0,0)),.6)
  x=hit[0].x if hit[0] else .11;vv.append((x+.004+.007*math.sin(math.pi*j/4),y,z))
for i in range(36):
 for j in range(4):ff.append((i*5+j,(i+1)*5+j,(i+1)*5+j+1,i*5+j+1))
o=bind(mesh('MM_HeavyGreyMoustache',vv,ff,GREY,smooth=True));o.modifiers.new('MoustacheVolume','SOLIDIFY').thickness=.004;vis(o)

# Viper: connected shell from flared shoulder collar to crown, separate visor/details.
M=collection('Miles_ViperMask');CURRENT=M
SHELL=material('MM_ViperNavyShell',(.013,.028,.070),.36,.30);VISOR=material('MM_ViperAmberVisor',(.85,.42,.012),.55,.17);ACC=material('MM_ViperOrange',(.86,.15,.015),.35,.32)
rows=[(1.40,.215,.235),(1.48,.20,.22),(1.56,.145,.16),(1.64,.145,.147),(1.73,.153,.15),(1.81,.135,.145),(1.87,.095,.105),(1.895,.01,.015)]
vv=[];ff=[];weights=[];N=64
for z,rx,ry in rows:
 for i in range(N):
  a=2*pi*i/N;xx=-.012+rx*math.copysign(abs(math.cos(a))**.70,math.cos(a));yy=ry*math.copysign(abs(math.sin(a))**.78,math.sin(a));vv.append((xx,yy,z))
  t=max(0,min(1,(z-1.43)/.15));weights.append({'head':t,'spine':1-t})
for j in range(len(rows)-1):
 for i in range(N):ff.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
ff.append(tuple((len(rows)-1)*N+i for i in range(N)))
o=bind(mesh('MM_Viper_ContinuousShell',vv,ff,SHELL,smooth=True),weights=weights);o.modifiers.new('ViperShellWall','SOLIDIFY').thickness=.005
o['design_note']='Collar lower weights follow torso; upper helmet follows same head. Hidden shell surfaces interpreted.'
o=bind(patch('MM_Viper_AmberVisor',seq(28,-1,1),seq(10),lambda u,t:(.157+.013*(1-u*u),.128*u,1.677+.072*t-.011*abs(u)),VISOR,thick=.004,sub=1))
for s in [-1,1]:
 cmesh(path('MM_Viper_CrownRidge',[(.10,s*.077,1.77),(.09,s*.095,1.84),(-.05,s*.080,1.885),(-.11,s*.07,1.82)],.008,edge))
 for i in range(2):bind(box('MM_Viper_CollarBadge',(.17,s*(.12+i*.047),1.46+i*.015),(.021,.025,.018),ACC,.004),'spine')
 for i in range(2):bind(tube('MM_Viper_CollarStud',(.197,s*(.09+i*.04),1.421),(.207,s*(.09+i*.04),1.421),.010,edge,N=16),'spine')
for i in range(7):
 z=1.405+i*.015;bind(box('MM_Viper_VocalGrille',(.209-i*.003,0,z),(.012,.080-i*.006,.010),ACC,.003),'spine')
for o in M.all_objects:vis(o,True)

# Solve seated arms/legs with unchanged bone lengths. Store editable quaternion pose controls.
CURRENT=C;R.update_tag();bpy.context.view_layer.update()
def orient(name,start,end):
 b=R.pose.bones[name];rest=R.data.bones[name];q=(rest.tail_local-rest.head_local).rotation_difference(Vector(end)-Vector(start));mat=(q.to_matrix()@rest.matrix_local.to_3x3()).to_4x4();mat.translation=start;b.matrix=mat;bpy.context.view_layer.update()
def limb(upper,lower,target,bend):
 a=R.pose.bones[upper].head.copy();axis=(Vector(target)-a).normalized();d=min((Vector(target)-a).length,R.data.bones[upper].length+R.data.bones[lower].length-.001);target=a+axis*d
 l1=R.data.bones[upper].length;l2=R.data.bones[lower].length;x=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(max(0,l1*l1-x*x));v=Vector(bend);v=(v-axis*v.dot(axis)).normalized();el=a+axis*x+v*h;orient(upper,a,el);orient(lower,el,target)
sp=R.pose.bones['spine'];sp.rotation_quaternion=sp.bone.matrix_local.to_quaternion().inverted()@Quaternion((0,1,0),.12)@sp.bone.matrix_local.to_quaternion();bpy.context.view_layer.update()
for s,label in [(1,'L'),(-1,'R')]:
 limb('thigh.'+label,'shin.'+label,(.85,s*.18,.61),(1,s*.25,.4))
 limb('upper_arm.'+label,'forearm.'+label,(.73,s*.24,1.19),(0,s*.3,-1))
 b=R.pose.bones['foot.'+label];pos=b.head.copy();orient(b.name,pos,pos+Vector((.14,0,-.015)))
pose={b.name:list(b.rotation_quaternion) for b in R.pose.bones}
for b in R.pose.bones:
 q=pose[b.name];b.rotation_quaternion=(1,0,0,0)
 for i,val in enumerate(q):drive(b,'rotation_quaternion',i,str((1,0,0,0)[i])+'*(1-p)+'+str(val)+'*p',[('p',R,'driving_pose')])
R.parent=root;R.matrix_parent_inverse=Matrix.Identity(4)
drive(R,'location',0,'0.25*v',[('v',R,'in_vehicle')]);drive(R,'location',2,'0.65*v',[('v',R,'in_vehicle')])
R['driving_pose']=1.;R['mask_on']=True;R['in_vehicle']=1.;R.update_tag();bpy.context.view_layer.update()
(A/'miles_seated_pose_v1.json').write_text(json.dumps(pose,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Switchblade_V1_Assembly.blend'),compress=True)
print('MILES_VIPER_SAVED',len(C.all_objects),len(M.all_objects))
