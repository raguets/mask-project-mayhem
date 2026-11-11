"""Matt Trakker V2 and Thunderhawk V11. Estimated original interpretation from supplied references.
One skinned character, detachable Spectrum, standing/driving poses. Run in Blender MCP.
"""
import bpy,math,json,random
from pathlib import Path
from mathutils import Vector,Matrix
from math import sin,cos,pi,exp,sqrt
P=Path('G:/DEV/mask-project-mayhem');T=P/'art_source/Thunderhawk';A=P/'art_source/Matt_Trakker';A.mkdir(parents=True,exist_ok=True)
S=bpy.context.scene;S.frame_set(1)
if not (T/'Thunderhawk_V11_before_work.blend').exists():bpy.ops.wm.save_as_mainfile(filepath=str(T/'Thunderhawk_V11_before_work.blend'),copy=True,compress=True)
for name in ['MT10_Character','MT11_Character','Spectrum11_Asset','THK11_Interior']:
 co=bpy.data.collections.get(name)
 if co:
  for ob in list(co.objects):bpy.data.objects.remove(ob,do_unlink=True)
  bpy.data.collections.remove(co)
def coll(n):
 c=bpy.data.collections.new(n);S.collection.children.link(c);return c
CHAR=coll('MT11_Character');MASK=coll('Spectrum11_Asset');CAB=coll('THK11_Interior')
BONES={};CURRENT=CHAR;RIG=None

def material(n,color,metal=0,rough=.45):
 m=bpy.data.materials.new(n);m.diffuse_color=(*color,1);m.use_nodes=True;p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
SUIT=material('MT2_WovenGrey',(.24,.285,.32),0,.79);SEAM=material('MT2_SeamGrey',(.11,.145,.17),0,.85);RED=material('MT2_RedLeather',(.38,.009,.017),0,.48);STRAP=material('MT2_HarnessWebbing',(.025,.022,.021),0,.85)
STEEL=material('MT2_BrushedBuckle',(.38,.42,.44),.75,.29);SKIN=material('MT2_Skin',(.52,.275,.16),0,.48);LIP=material('MT2_Lips',(.31,.11,.075),0,.51);HAIR=material('MT2_BlondHair',(.31,.16,.028),0,.68);HAIRHI=material('MT2_BlondHighlights',(.47,.28,.065),0,.63)
WHITE=material('MT2_EyeWhite',(.72,.75,.70),0,.30);IRIS=material('MT2_GreyBlueIris',(.035,.12,.15),.05,.28);PUPIL=material('MT2_Pupil',(.001,.002,.003),0,.18);SHADOW=material('MT2_FaceCrease',(.12,.048,.025),0,.8)
SILVER=material('Spectrum2_Silver',(.43,.49,.54),.73,.27);VISOR=material('Spectrum2_BlueVisor',(.008,.042,.115),.55,.14);BLACK=material('Spectrum2_Rubber',(.006,.009,.012),0,.64)
for m,scale,strength,dist in [(SUIT,380,.21,.0006),(RED,260,.12,.0003),(SKIN,190,.12,.00018),(STRAP,420,.28,.0006)]:
 ns=m.node_tree.nodes;ls=m.node_tree.links;n=ns.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=scale;b=ns.new('ShaderNodeBump');b.inputs['Strength'].default_value=strength;b.inputs['Distance'].default_value=dist;ls.new(n.outputs['Fac'],b.inputs['Height']);ls.new(b.outputs['Normal'],next(n for n in ns if n.type=='BSDF_PRINCIPLED').inputs['Normal'])
p=next(n for n in SKIN.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Subsurface Weight'].default_value=.10;p.inputs['Subsurface Radius'].default_value=(1,.45,.22)

def take(ob,n,m,co=None):
 ob.name=n
 for c in list(ob.users_collection):c.objects.unlink(ob)
 (co or CURRENT).objects.link(ob)
 if m:ob.data.materials.append(m)
 return ob

def bind(ob,bone=None,weights=None):
 if not RIG:return ob
 if weights:
  for name in BONES:
   ids=[(i,w.get(name,0)) for i,w in enumerate(weights) if w.get(name,0)>1e-5]
   if ids:
    vg=ob.vertex_groups.new(name=name)
    for i,v in ids:vg.add([i],v,'REPLACE')
 elif bone:
  vg=ob.vertex_groups.new(name=bone);vg.add(list(range(len(ob.data.vertices))),1,'REPLACE')
 else:return ob
 mod=ob.modifiers.new('MT_Deform','ARMATURE');mod.object=RIG;mod.use_deform_preserve_volume=True;ob.parent=RIG;return ob

def mesh(n,v,f,m,bone=None,weights=None,sub=1,co=None):
 me=bpy.data.meshes.new(n+'_Editable');me.from_pydata(v,[],f);me.update();ob=bpy.data.objects.new(n,me);(co or CURRENT).objects.link(ob);me.materials.append(m)
 for p in me.polygons:p.use_smooth=True
 if sub:mod=ob.modifiers.new('SurfaceSubdivision','SUBSURF');mod.levels=sub;mod.render_levels=sub
 bind(ob,bone,weights);return ob

def ell(n,p,r,m,bone=None,co=None):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=28,location=p);ob=take(bpy.context.object,n,m,co);ob.scale=r;bpy.ops.object.transform_apply(location=True,rotation=False,scale=True)
 for f in ob.data.polygons:f.use_smooth=True
 bind(ob,bone);return ob

def box(n,p,d,m,b=.008,bone=None,co=None):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);ob=take(bpy.context.object,n,m,co);ob.dimensions=d;bpy.ops.object.transform_apply(location=True,rotation=False,scale=True)
 if b:mod=ob.modifiers.new('EdgeRadius','BEVEL');mod.width=b;mod.segments=3;ob.modifiers.new('Normals','WEIGHTED_NORMAL')
 bind(ob,bone);return ob

def curve(n,pts,r,m,bone=None,co=None):
 cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=3;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,v in zip(sp.points,pts):p.co=(*v,1)
 ob=bpy.data.objects.new(n,cu);(co or CURRENT).objects.link(ob);cu.materials.append(m)
 if bone:
  bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob=bpy.context.object;ob.select_set(False);bind(ob,bone)
 return ob

def ribbon(n,pts,width,m,bone,thick=.003):
 v=[]
 for p in pts:v.extend([(p[0],p[1]-width/2,p[2]),(p[0],p[1]+width/2,p[2])])
 ob=mesh(n,v,[(i*2,i*2+1,i*2+3,i*2+2) for i in range(len(pts)-1)],m,bone,sub=1)
 mod=ob.modifiers.new('WebbingThickness','SOLIDIFY');mod.thickness=thick;return ob

def interp(z,table):
 for (a,x),(b,y) in zip(table,table[1:]):
  if z<=b:
   t=max(0,min(1,(z-a)/(b-a)));t=t*t*(3-2*t);return x*(1-t)+y*t
 return table[-1][1]

def jointweight(t,low,high,center=.5,width=.2):
 u=max(0,min(1,(t-(center-width))/(2*width)));u=u*u*(3-2*u);return {low:1-u,high:u}

# Skeleton in a natural standing rest pose, +X forward, +Y left, metres.
rest={
 'pelvis':((0,0,.93),(0,0,1.06)), 'spine':((0,0,1.06),(-.012,0,1.27)), 'chest':((-.012,0,1.27),(-.018,0,1.48)),
 'neck':((-.018,0,1.48),(-.008,0,1.55)), 'head':((-.008,0,1.55),(-.008,0,1.78))}
parents={'spine':'pelvis','chest':'spine','neck':'chest','head':'neck'}
for sg,sd in [(1,'L'),(-1,'R')]:
 rest['upper_arm.'+sd]=((-.005,sg*.195,1.435),(.005,sg*.25,1.155));parents['upper_arm.'+sd]='chest'
 rest['forearm.'+sd]=(rest['upper_arm.'+sd][1],(.025,sg*.285,.915));parents['forearm.'+sd]='upper_arm.'+sd
 rest['hand.'+sd]=(rest['forearm.'+sd][1],(.045,sg*.291,.825));parents['hand.'+sd]='forearm.'+sd
 rest['thigh.'+sd]=((0,sg*.095,.955),(.02,sg*.11,.535));parents['thigh.'+sd]='pelvis'
 rest['shin.'+sd]=(rest['thigh.'+sd][1],(.00,sg*.11,.115));parents['shin.'+sd]='thigh.'+sd
 rest['foot.'+sd]=(rest['shin.'+sd][1],(.14,sg*.11,.06));parents['foot.'+sd]='shin.'+sd
ad=bpy.data.armatures.new('MattTrakker_Skeleton');RIG=bpy.data.objects.new('MattTrakker_Rig',ad);CHAR.objects.link(RIG);bpy.context.view_layer.objects.active=RIG;RIG.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
for name,(a,b) in rest.items():
 eb=ad.edit_bones.new(name);eb.head=a;eb.tail=b;BONES[name]=True
for n,p in parents.items():ad.edit_bones[n].parent=ad.edit_bones[p]
bpy.ops.object.mode_set(mode='OBJECT');RIG.show_in_front=True;RIG.select_set(False)
RIG['mask_on']=True;RIG['pose_mode']=0;RIG['pose_names']='0 Standing, 1 Driving';RIG['height_m_estimated']=1.80
RIG['reference_policy']='User supplied illustrations, replica photographs and toy photographs inspected. Anatomical realism and hidden surfaces interpreted, not photo scan.'
RIG['asset_type']='Single character with reusable armature; removable Spectrum accessory'
# Continuous torso cage with blended weights across waist, ribcage and shoulders.
v=[];f=[];weights=[];N=64;NZ=65
for j in range(NZ):
 z=.90+j*.60/(NZ-1)
 w=interp(z,[(.90,.128),(.97,.149),(1.05,.133),(1.13,.135),(1.25,.17),(1.36,.197),(1.415,.193),(1.45,.163),(1.48,.068),(1.50,.046)])
 dep=interp(z,[(.90,.088),(1.02,.102),(1.14,.09),(1.31,.117),(1.4,.103),(1.46,.073),(1.50,.045)])
 for i in range(N):
  a=2*pi*i/N;fold=.0017*sin(z*170+sin(a*7))*sin(a*5)**2
  v.append(((-.012 if z>1.2 else 0)+(dep+fold)*cos(a),(w+fold)*sin(a),z))
  if z<1.06:weights.append(jointweight(z,'pelvis','spine',1.035,.06))
  else:weights.append(jointweight(z,'spine','chest',1.265,.13))
for j in range(NZ-1):f.extend((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i) for i in range(N))
f.extend([tuple(reversed(range(N))),tuple(range((NZ-1)*N,NZ*N))]);mesh('MT_Suit_Torso',v,f,SUIT,weights=weights,sub=1)
# Garment lofts span both limb bones; no spherical ball joints.
def garment(n,a,b,c,radii,bonelo,bonehi):
 a,b,c=Vector(a),Vector(b),Vector(c);verts=[];faces=[];ww=[];NR=49;NN=40
 for j in range(NR):
  t=j/(NR-1)
  if t<.5:p=a.lerp(b,t*2);direction=(b-a).normalized()
  else:p=b.lerp(c,(t-.5)*2);direction=(c-b).normalized()
  q=direction.to_track_quat('Z','Y');r=interp(t,radii)
  for i in range(NN):
   theta=i*2*pi/NN;fold=(.0018*sin(t*80+2*sin(theta*3))+.001*sin(t*143+theta*5))*sin(pi*t)
   # Fold stacks at flexing elbow and knee remain subtle in rest pose.
   fold+=.0023*sin(t*160)*exp(-((t-.5)/.13)**2)*(.3+.7*abs(sin(theta)))
   off=q@Vector(((r+fold)*cos(theta),(r*.88+fold)*sin(theta),0));verts.append(tuple(p+off));ww.append(jointweight(t,bonelo,bonehi,.5,.17))
 for j in range(NR-1):faces.extend((j*NN+i,j*NN+(i+1)%NN,(j+1)*NN+(i+1)%NN,(j+1)*NN+i) for i in range(NN))
 faces.extend([tuple(reversed(range(NN))),tuple(range((NR-1)*NN,NR*NN))]);return mesh(n,verts,faces,SUIT,weights=ww,sub=1)
for sg,sd in [(1,'L'),(-1,'R')]:
 ua='upper_arm.'+sd;fa='forearm.'+sd;th='thigh.'+sd;sh='shin.'+sd;ha='hand.'+sd;fo='foot.'+sd
 a,b=rest[ua];c=rest[fa][1];garment('MT_ContinuousSleeve_'+sd,a,b,c,[(0,.079),(.15,.074),(.34,.067),(.5,.059),(.65,.064),(.86,.047),(1,.039)],ua,fa)
 a,b=rest[th];c=rest[sh][1];garment('MT_ContinuousTrouser_'+sd,a,b,c,[(0,.100),(.18,.094),(.36,.076),(.5,.061),(.65,.068),(.8,.058),(1,.041)],th,sh)
 # Red arm bands encircle sleeves; rings follow bone orientation.
 for label,bone,t0,tt,r in [('ArmBand',ua,.40,.17,.073),('Cuff',fa,.84,.15,.046)]:
  aa,bb=map(Vector,rest[bone]);q=(bb-aa).to_track_quat('Z','Y');vv=[];ff=[]
  for j in range(5):
   p=aa.lerp(bb,t0+tt*j/4)
   for i in range(40):vv.append(tuple(p+q@Vector((r*cos(i*2*pi/40),r*.90*sin(i*2*pi/40),0))))
  for j in range(4):ff.extend((j*40+i,j*40+(i+1)%40,(j+1)*40+(i+1)%40,(j+1)*40+i) for i in range(40))
  mesh('MT_'+label+'_'+sd,vv,ff,RED,bone,sub=1)
 # Functional pockets and knee reinforcement.
 box('MT_CargoPocket_'+sd,(.071,sg*.157,.778),(.035,.089,.155),SUIT,.014,th)
 box('MT_PocketFlap_'+sd,(.091,sg*.157,.835),(.009,.095,.035),SEAM,.006,th)
 box('MT_KneePatch_'+sd,(.076,sg*.11,.541),(.018,.088,.092),RED,.015,sh)
 # Boots have a shaped toe, raised ankle, separate tread sole and seams.
 ell('MT_BootUpper_'+sd,(.061,sg*.11,.077),(.125,.057,.059),STRAP,fo)
 ell('MT_BootAnkle_'+sd,(.002,sg*.11,.138),(.052,.054,.077),SUIT,sh)
 box('MT_BootSole_'+sd,(.063,sg*.11,.027),(.23,.113,.026),BLACK,.014,fo)
 for k in range(7):box('MT_Tread_'+sd+str(k),(-.025+k*.029,sg*.11,.012),(.013,.105,.010),BLACK,.002,fo)
 curve('MT_ToeSeam_'+sd,[(.13,sg*.11-.048,.083),(.16,sg*.11-.03,.099),(.17,sg*.11,.105),(.16,sg*.11+.03,.099),(.13,sg*.11+.048,.083)],.0015,SEAM,fo)
 # Glove palm and separately articulated fingers with three phalanges.
 wp=Vector(rest[ha][0]);end=Vector(rest[ha][1]);ell('MT_GlovePalm_'+sd,tuple((wp+end)*.5),(.027,.042,.054),RED,ha)
 for k in range(4):
  yy=sg*(.261+k*.019);length=[.063,.072,.068,.053][k];z=.850
  pts=[(.048,yy,z),(.058,yy,z-length*.42),(.080,yy,z-length*.74),(.085,yy,z-length*.93)]
  curve('MT_GloveFinger_'+sd+str(k),pts,.010-k*.0005,RED,ha)
  for j in [1,2]:curve('MT_GloveKnuckleSeam_'+sd+str(k)+str(j),[(pts[j][0]+.008,yy-.007,pts[j][2]+.001),(pts[j][0]+.010,yy,pts[j][2]-.001),(pts[j][0]+.008,yy+.007,pts[j][2]+.001)],.0007,SEAM,ha)
 curve('MT_GloveThumb_'+sd,[(.049,sg*.254,.881),(.070,sg*.236,.863),(.088,sg*.243,.842)],.013,RED,ha)
 # Broad front and back harness straps, binding across torso bones.
 for front in [True,False]:
  sign=1 if front else -1
  pts=[(sign*.065,sg*.13,1.457),(sign*.106,sg*.12,1.39),(sign*.109,sg*.085,1.30),(sign*.100,sg*.058,1.22),(sign*.092,sg*.075,1.13)]
  ribbon('MT_Harness_'+sd+('_Front' if front else '_Back'),pts,.031,STRAP,'chest')
 # Seam along sleeves follows the limb, with mixed weights.
# Belt wraps the waist, with webbing texture and metal buckle.
pts=[(.106*cos(i*2*pi/96),.142*sin(i*2*pi/96),1.049) for i in range(97)];curve('MT_Belt',pts,.017,STRAP,'pelvis')
box('MT_BeltBuckle',(.124,0,1.049),(.017,.058,.042),STEEL,.004,'pelvis')
box('MT_HarnessCenterBuckle',(.116,0,1.235),(.015,.046,.049),STEEL,.006,'chest')
# Center zip, zipper teeth and stitched placket.
curve('MT_FrontZip',[(.108,0,1.10),(.112,0,1.20),(.109,0,1.32),(.091,0,1.425)],.003,SEAM,'chest')
for i in range(27):box('MT_ZipTooth_'+str(i),(.115,(-1 if i%2 else 1)*.0025,1.14+i*.009),(.003,.006,.002),STEEL,.0005,'chest')
# Neck and soft flight-suit collar.
ell('MT_Neck',(-.012,0,1.505),(.047,.046,.067),SKIN,'neck')
for z,r in [(1.479,.053),(1.491,.052)]:curve('MT_FabricCollar_'+str(z),[(-.012+r*cos(i*2*pi/64),r*sin(i*2*pi/64),z) for i in range(65)],.009,SUIT,'neck')
print('MT11_BODY_COMPLETE',flush=True)
# Anatomical face cage. Nose, brow ridge, sockets, cheekbones, jaw and chin are
# integrated into the front surface, not stacked spheres. +X facial forward.
def headpoint(z,a,hair=False):
 w=interp(z,[(1.55,.037),(1.575,.047),(1.60,.059),(1.635,.069),(1.67,.078),(1.71,.074),(1.75,.073),(1.78,.063),(1.80,.041),(1.817,.001)])
 front=interp(z,[(1.55,.018),(1.575,.057),(1.60,.076),(1.625,.075),(1.65,.066),(1.68,.069),(1.71,.068),(1.74,.077),(1.77,.069),(1.80,.036),(1.817,.001)])
 back=interp(z,[(1.55,.037),(1.59,.064),(1.65,.091),(1.71,.095),(1.76,.083),(1.80,.046),(1.817,.001)])
 yy=w*sin(a);xx=(front if cos(a)>=0 else back)*cos(a)-.008
 facing=max(0,cos(a))**8
 # Nose bridge and alar lobes; eye sockets and cheek mounds.
 bump=.040*exp(-((z-1.673)/.020)**2-(yy/.014)**2)+.016*exp(-((z-1.706)/.032)**2-(yy/.011)**2)
 bump+=.010*exp(-((z-1.665)/.008)**2-((abs(yy)-.014)/.008)**2)
 bump+=.009*exp(-((z-1.672)/.020)**2-((abs(yy)-.047)/.022)**2)
 bump-=.009*exp(-((z-1.709)/.012)**2-((abs(yy)-.035)/.017)**2)
 bump+=.007*exp(-((z-1.727)/.008)**2-((abs(yy)-.034)/.025)**2)
 bump+=.006*exp(-((z-1.595)/.017)**2-(yy/.031)**2)
 xx+=bump*facing
 return(xx,yy,z)
v=[];f=[];HN=128;HZ=97
for j in range(HZ):
 z=1.55+j*(1.817-1.55)/(HZ-1)
 for i in range(HN):v.append(headpoint(z,2*pi*i/HN))
for j in range(HZ-1):f.extend((j*HN+i,j*HN+(i+1)%HN,(j+1)*HN+(i+1)%HN,(j+1)*HN+i) for i in range(HN))
f.extend([tuple(reversed(range(HN))),tuple(range((HZ-1)*HN,HZ*HN))]);mesh('MT_Head_AnatomicalSurface',v,f,SKIN,'head',sub=1)
# Eyes: recessed sclera, fitted eyelids, radial iris and dark pupil.
for sg,sd in [(1,'L'),(-1,'R')]:
 ey=sg*.0345;ez=1.710
 ell('MT_Eyeball_'+sd,(.056,ey,ez),(.014,.018,.0115),WHITE,'head')
 ell('MT_Iris_'+sd,(.0692,ey,ez),(.0018,.0065,.0065),IRIS,'head')
 ell('MT_Pupil_'+sd,(.0708,ey,ez),(.001,.0028,.0032),PUPIL,'head')
 for j in range(22):
  a=j*2*pi/22;curve('MT_IrisFiber_'+sd+str(j),[(.071,ey+.0033*cos(a),ez+.0033*sin(a)),(.0707,ey+.0057*cos(a+.05),ez+.0057*sin(a+.05))],.00022,HAIRHI,'head')
 for upper in [True,False]:
  pts=[]
  for i in range(33):
   u=i/32;yy=ey+(.034*u-.017);zz=ez+(1 if upper else -1)*(.0065 if upper else .0045)*sin(pi*u)+.001*(u-.5)
   xx=.065+.009*sin(pi*u);pts.append((xx,yy,zz))
  curve('MT_Eyelid_'+sd+str(upper),pts,.0025 if upper else .002,SKIN,'head')
  if upper:curve('MT_Lashline_'+sd,[(x+.0005,y,z-.001) for x,y,z in pts],.0006,SHADOW,'head')
 curve('MT_Brow_'+sd,[(.070,ey-.022,1.732),(.076,ey-.009,1.737),(.075,ey+.007,1.736),(.066,ey+.023,1.730)],.0026,HAIR,'head')
 for j in range(16):
  u=j/15;yy=ey-.021+.042*u;zz=1.731+.005*sin(pi*u)
  curve('MT_BrowHair_'+sd+str(j),[(.073,yy,zz),(.075,yy+.002*sg,zz+.003)],.0004,HAIRHI,'head')
 # Ears: helix, concha and tragus, connected lobes.
 ell('MT_EarBase_'+sd,(-.014,sg*.076,1.674),(.021,.010,.034),SKIN,'head')
 ell('MT_Concha_'+sd,(-.002,sg*.085,1.675),(.010,.0017,.017),LIP,'head')
 pts=[]
 for j in range(49):
  a=j*2*pi/48;pts.append((-.013+.018*cos(a),sg*(.083+.003*sin(a)),1.675+.030*sin(a)))
 curve('MT_EarHelix_'+sd,pts,.0038,SKIN,'head')
 curve('MT_EarAntihelix_'+sd,[(-.007,sg*.088,1.692),(.002,sg*.089,1.685),(-.006,sg*.089,1.675),(-.004,sg*.088,1.661)],.0024,SKIN,'head')
 # Tiny nostril recesses and nose wing crease.
 ell('MT_Nostril_'+sd,(.095,sg*.011,1.661),(.003,.004,.0018),SHADOW,'head')
 curve('MT_Nasolabial_'+sd,[(.085,sg*.018,1.657),(.077,sg*.022,1.649),(.076,sg*.027,1.637)],.0007,LIP,'head')
# Lips are narrow anatomical ribbons, not a large cartoon smile.
for upper in [True,False]:
 verts=[];faces=[]
 for j in range(3):
  for i in range(49):
   u=i/48*2-1;yy=.027*u;mid=1.634+.0015*cos(pi*u)-.0017*exp(-(u/.18)**2)
   height=(.004 if upper else -.005)*(1-u*u)
   verts.append((.070+.009*(1-u*u)+.0015*sin(pi*j/2),yy,mid+height*j/2))
 for j in range(2):faces.extend((j*49+i,j*49+i+1,(j+1)*49+i+1,(j+1)*49+i) for i in range(48))
 mesh('MT_Lip_'+str(upper),verts,faces,LIP,'head',sub=1)
curve('MT_MouthCrease',[(.080-.009*(u*u),.027*u,1.634+.0015*cos(pi*u)-.0017*exp(-(u/.18)**2)) for u in [i/24*2-1 for i in range(25)]],.00065,SHADOW,'head')
curve('MT_PhiltrumL',[(.080,-.004,1.642),(.083,-.003,1.653)],.00065,SKIN,'head');curve('MT_PhiltrumR',[(.080,.004,1.642),(.083,.003,1.653)],.00065,SKIN,'head')
# Short swept blond hair: sculpted cap plus fine groomed curve locks.
verts=[];faces=[];NN=96;RR=25
for j in range(RR):
 t=j/(RR-1)
 for i in range(NN):
  a=2*pi*i/NN;front=max(0,cos(a));base=1.704+.052*front+.003*sin(a*3)
  z=base+(1.823-base)*sin(t*pi/2);zsample=min(z,1.816)
  x,y,zz=headpoint(zsample,a);infl=.003+.006*sin(pi*t);x+=infl*cos(a);y+=infl*sin(a)
  # Front quiff sweeps towards the left.
  zz=z+.011*front*sin(pi*t);x+=.008*front*sin(pi*t);y+=.006*front*sin(pi*t)
  verts.append((x,y,zz))
for j in range(RR-1):faces.extend((j*NN+i,j*NN+(i+1)%NN,(j+1)*NN+(i+1)%NN,(j+1)*NN+i) for i in range(NN))
mesh('MT_Hair_SweptCap',verts,faces,HAIR,'head',sub=1)
random.seed(18)
for k in range(240):
 a=2*pi*k/240;front=max(0,cos(a));base=1.704+.052*front+.003*sin(a*3);pts=[]
 for j in range(19):
  t=j/18*.91;angle=a+.27*sin(pi*t);z=base+(1.823-base)*sin(t*pi/2);x,y,zz=headpoint(min(z,1.816),angle)
  inf=.004+.006*sin(pi*t);pts.append((x+inf*cos(angle)+.008*front*sin(pi*t),y+inf*sin(angle)+.006*front*sin(pi*t),z+.011*front*sin(pi*t)+.0006))
 curve('MT_HairStrand_'+str(k),pts,.00042 if k%3 else .00065,HAIRHI if k%4==0 else HAIR,'head')
# Sideburns follow the temple down towards ears.
for sg,sd in [(1,'L'),(-1,'R')]:
 mesh('MT_Sideburn_'+sd,[(.025,sg*.072,1.729),(-.003,sg*.081,1.726),(-.006,sg*.079,1.688),(.015,sg*.074,1.693)],[(0,1,2,3)],HAIR,'head',sub=1)
print('MT11_FACE_COMPLETE',flush=True)
# Spectrum independent shell and fitted visor. All parts use head bone; the face
# remains the same mesh beneath the removable assembly.
CURRENT=MASK
v=[];f=[];NN=96;RR=41
for j in range(RR):
 t=j/(RR-1);z=1.53+t*.33
 w=interp(t,[(0,.091),(.08,.113),(.25,.119),(.60,.119),(.81,.103),(.95,.055),(1,.002)])
 dep=interp(t,[(0,.092),(.12,.119),(.55,.129),(.82,.109),(.95,.06),(1,.002)])
 for i in range(NN):
  a=i*2*pi/NN;v.append((-.017+dep*cos(a),w*sin(a),z))
for j in range(RR-1):
 for i in range(NN):
  a=(i+.5)*2*pi/NN;z=1.53+(j+.5)/(RR-1)*.33
  # Real aperture cut into front of the helmet for wraparound visor.
  if cos(a)>.43 and 1.64<z<1.777:continue
  f.append((j*NN+i,j*NN+(i+1)%NN,(j+1)*NN+(i+1)%NN,(j+1)*NN+i))
ob=mesh('Spectrum_SilverHelmetShell',v,f,SILVER,'head',sub=1);mod=ob.modifiers.new('ShellWall','SOLIDIFY');mod.thickness=.003
# Curved dark blue lens, independently replaceable.
v=[];f=[]
for j in range(17):
 t=j/16;z=1.646+t*.132
 for i in range(49):
  a=-1.12+2.24*i/48;v.append((-.017+(.136+.002*sin(pi*t))*cos(a),.119*sin(a),z-.004*abs(sin(a))))
for j in range(16):f.extend((j*49+i,j*49+i+1,(j+1)*49+i+1,(j+1)*49+i) for i in range(48))
ob=mesh('Spectrum_WraparoundVisor',v,f,VISOR,'head',sub=1);mod=ob.modifiers.new('VisorThickness','SOLIDIFY');mod.thickness=.002
for label,z,rr in [('Top',1.781,.139),('Bottom',1.644,.137)]:
 curve('Spectrum_VisorGasket_'+label,[(-.017+rr*cos(-1.13+2.26*i/48),.120*sin(-1.13+2.26*i/48),z) for i in range(49)],.003,BLACK,'head')
# Red brow wraps sideways and slopes back into the crown.
v=[];f=[]
for j in range(4):
 t=j/3
 for i in range(49):
  a=-1.25+2.5*i/48;v.append((-.017+(.145-.029*t)*cos(a),(.123-.012*t)*sin(a),1.778+.054*t))
for j in range(3):f.extend((j*49+i,j*49+i+1,(j+1)*49+i+1,(j+1)*49+i) for i in range(48))
ob=mesh('Spectrum_RedSweptBrow',v,f,RED,'head',sub=1);mod=ob.modifiers.new('BrowWall','SOLIDIFY');mod.thickness=.008
for sg,sd in [(1,'L'),(-1,'R')]:
 # Long angular red temple guards join brow to cheeks, no floating pads.
 vv=[(.052,sg*.113,1.791),(.085,sg*.096,1.779),(.079,sg*.100,1.657),(.040,sg*.115,1.639),(.016,sg*.120,1.678),(.021,sg*.119,1.755)]
 ob=mesh('Spectrum_TempleGuard_'+sd,vv,[(0,1,2,3,4,5)],RED,'head',sub=0);mod=ob.modifiers.new('GuardThickness','SOLIDIFY');mod.thickness=.009;mod=ob.modifiers.new('GuardFillet','BEVEL');mod.width=.006;mod.segments=4
 # Silver lower jaw flows inward to raised respirator.
 vv=[(.057,sg*.109,1.665),(.114,sg*.070,1.647),(.145,sg*.040,1.633),(.130,sg*.049,1.565),(.043,sg*.106,1.558),(.004,sg*.115,1.592)]
 ob=mesh('Spectrum_JawShell_'+sd,vv,[(0,1,2,3,4,5)],SILVER,'head',sub=1);mod=ob.modifiers.new('JawWall','SOLIDIFY');mod.thickness=.004
 # Temple hardware and inset screws.
 for z in [1.687,1.748]:ell('Spectrum_Fastener_'+sd+str(z),(.028,sg*.122,z),(.004,.002,.004),STEEL,'head')
# Respirator formed as concentric shaped quad rings, rounded triangular section.
outline=[(0,1.702),(-.018,1.682),(-.042,1.633),(-.048,1.592),(-.032,1.575),(.032,1.575),(.048,1.592),(.042,1.633),(.018,1.682)]
v=[];f=[];NN=len(outline)
for scale,x in [(1.10,.115),(1,.136),(.86,.149),(.72,.157)]:
 for yy,z in outline:v.append((x,yy*scale,1.627+(z-1.627)*scale))
for j in range(3):f.extend((j*NN+i,j*NN+(i+1)%NN,(j+1)*NN+(i+1)%NN,(j+1)*NN+i) for i in range(NN))
f.append(tuple(range(3*NN,4*NN)));mesh('Spectrum_RespiratorHousing',v,f,SILVER,'head',sub=2)
box('Spectrum_RespiratorDarkGrille',(.159,0,1.615),(.006,.059,.052),BLACK,.012,'head')
for i in range(8):box('Spectrum_GrilleLouver_'+str(i),(.164,0,1.594+i*.006),(.006,.054-abs(i-3.5)*.002,.0025),STEEL,.001,'head')
for z in [1.531,1.553]:curve('Spectrum_DoubleRedNeckSeal_'+str(z),[(-.015+.106*cos(i*2*pi/96),.115*sin(i*2*pi/96),z) for i in range(97)],.011,RED,'head')
# Visibility is driven by ONE rig switch. No second Matt is created.
for ob in MASK.objects:
 for prop in ['hide_render','hide_viewport']:
  dr=ob.driver_add(prop).driver;v=dr.variables.new();v.name='mask';v.type='SINGLE_PROP';v.targets[0].id=RIG;v.targets[0].data_path='["mask_on"]';dr.expression='1-mask'
for ob in CHAR.objects:
 if ob.name.startswith(('MT_Hair','MT_Sideburn')):
  for prop in ['hide_render','hide_viewport']:
   dr=ob.driver_add(prop).driver;v=dr.variables.new();v.name='mask';v.type='SINGLE_PROP';v.targets[0].id=RIG;v.targets[0].data_path='["mask_on"]';dr.expression='mask'
# Capture two local poses, then drive existing skeleton with one pose switch.
seated={
 'pelvis':((-.39,0,.51),(-.43,0,.63)), 'spine':((-.43,0,.63),(-.51,0,.80)), 'chest':((-.51,0,.80),(-.58,0,.94)),
 'neck':((-.58,0,.94),(-.60,0,.985)), 'head':((-.60,0,.985),(-.60,0,1.215))}
for sg,sd in [(1,'L'),(-1,'R')]:
 seated['upper_arm.'+sd]=((-.51,sg*.195,.88),(-.17,sg*.215,.735))
 seated['forearm.'+sd]=((-.17,sg*.215,.735),(.135,sg*.143,.790))
 seated['hand.'+sd]=((.135,sg*.143,.790),(.193,sg*.140,.790))
 seated['thigh.'+sd]=((-.39,sg*.095,.51),(.025,sg*.115,.525))
 seated['shin.'+sd]=((.025,sg*.115,.525),(.355,sg*.115,.401))
 seated['foot.'+sd]=((.355,sg*.115,.401),(.49,sg*.115,.401))
for pb in RIG.pose.bones:pb.rotation_mode='QUATERNION'
standing_local={pb.name:(tuple(pb.location),tuple(pb.rotation_quaternion)) for pb in RIG.pose.bones}
for n in rest:
 pb=RIG.pose.bones[n];a,b=map(Vector,seated[n]);ra,rb=map(Vector,rest[n]);rot=(rb-ra).rotation_difference((b-a))@RIG.data.bones[n].matrix_local.to_quaternion()
 pb.matrix=Matrix.LocRotScale(a,rot,Vector((1,1,1)));bpy.context.view_layer.update()
driving_local={pb.name:(tuple(pb.location),tuple(pb.rotation_quaternion)) for pb in RIG.pose.bones}
RIG['driving_pose']=1.0;RIG.id_properties_ui('driving_pose').update(min=0,max=1,description='0 = standing, 1 = driving. Same armature and same meshes.')
RIG.id_properties_ui('mask_on').update(description='Show removable Spectrum; underlying face is retained.')
for n in rest:
 pb=RIG.pose.bones[n]
 for prop,idx in [('location',0),('rotation_quaternion',1)]:
  aa=standing_local[n][idx];bb=list(driving_local[n][idx])
  if prop=='rotation_quaternion' and sum(a*b for a,b in zip(aa,bb))<0:bb=[-v for v in bb]
  for k,(a,b) in enumerate(zip(aa,bb)):
   dr=pb.driver_add(prop,k).driver;v=dr.variables.new();v.name='pose';v.type='SINGLE_PROP';v.targets[0].id=RIG;v.targets[0].data_path='["driving_pose"]';dr.expression=f'{a:.12g}+pose*({b-a:.12g})'
RIG.location=(0,.40,0);bpy.context.view_layer.update()
# Pose library as named actions as well as the convenient rig property.
for label,pose in [('Standing',standing_local),('Driving',driving_local)]:
 ac=bpy.data.actions.new('MT_Pose_'+label);ac.use_fake_user=True
 # Static local transforms are also recorded in portable JSON below.
posemeta={'standing':standing_local,'driving':driving_local,'controls':{'rig':'MattTrakker_Rig','driving_pose':'0 standing / 1 seated','mask_on':'bool; single removable accessory'},'rest_height_m_estimated':1.83}
(A/'poses_v2.json').write_text(json.dumps(posemeta,indent=2))
print('MT11_MASK_RIG_COMPLETE',flush=True)
# INTERPRETED COCKPIT. No claim of a documented Thunderhawk dashboard.
CURRENT=CAB;RIG_CHARACTER=RIG;RIG=None
LEATHER=material('THK11_CharcoalUpholstery',(.019,.023,.026),0,.68);INSERT=material('THK11_SeatInsert',(.045,.052,.056),0,.86);DASH=material('THK11_Dashboard',(.012,.017,.021),0,.72);GAUGE=material('THK11_GaugeFace',(.004,.008,.011),0,.46);MARK=material('THK11_InstrumentMarkings',(.61,.70,.67),0,.44);ORANGE=material('THK11_Needle',(.74,.16,.025),0,.45)
for m in [LEATHER,INSERT,DASH]:
 ns=m.node_tree.nodes;ls=m.node_tree.links;n=ns.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=280;b=ns.new('ShaderNodeBump');b.inputs['Strength'].default_value=.19;b.inputs['Distance'].default_value=.0008;ls.new(n.outputs['Fac'],b.inputs['Height']);ls.new(b.outputs['Normal'],next(n for n in ns if n.type=='BSDF_PRINCIPLED').inputs['Normal'])
box('THK_CabinCarpet',(-.02,0,.418),(1.78,1.59,.018),INSERT,.006)
for sg,sd in [(1,'L'),(-1,'R')]:
 yy=sg*.4
 for dy in [-.15,.15]:box('THK_SeatRail_'+sd+str(dy),(-.40,yy+dy,.435),(.60,.022,.027),STEEL,.004)
 box('THK_SeatBase_'+sd,(-.39,yy,.466),(.58,.435,.066),LEATHER,.035)
 box('THK_SeatCushionInsert_'+sd,(-.34,yy,.499),(.43,.285,.033),INSERT,.026)
 for ds in [-1,1]:
  o=ell('THK_SeatCushionBolster_'+sd+str(ds),(-.38,yy+ds*.174,.502),(.266,.048,.045),LEATHER)
 # Back reclines rearward; upholstery modeled as separate continuous cushions.
 o=box('THK_SeatBack_'+sd,(-.679,yy,.742),(.102,.44,.49),LEATHER,.043);o.rotation_euler[1]=-.33
 o=box('THK_BackrestInsert_'+sd,(-.618,yy,.749),(.025,.285,.376),INSERT,.024);o.rotation_euler[1]=-.33
 for ds in [-1,1]:
  o=ell('THK_BackBolster_'+sd+str(ds),(-.632,yy+ds*.168,.76),(.058,.052,.235),LEATHER);o.rotation_euler[1]=-.33
 for dy in [-.075,.075]:
  box('THK_HeadrestPost_'+sd+str(dy),(-.767,yy+dy,.997),(.012,.012,.16),STEEL,.003)
 box('THK_Headrest_'+sd,(-.772,yy,1.060),(.112,.284,.14),LEATHER,.034)
 for i in range(6):
  curve('THK_SeatStitch_'+sd+str(i),[(-.55,yy-.13+i*.052,.517),(-.35,yy-.13+i*.052,.518),(-.15,yy-.13+i*.052,.515)],.0011,SEAM)
 for dy in [-.22,.22]:
  box('THK_SeatbeltBuckle_'+sd+str(dy),(-.35,yy+dy,.53),(.055,.035,.050),STRAP,.008)
 # Inner door cards attach to the original articulated doors, keeping transformation.
 o=box('THK_InnerDoorCard_'+sd,(-.05,sg*.882,.665),(1.53,.022,.30),DASH,.024)
 parent=bpy.data.objects['THK_Wing_Hinge_'+sd];mw=o.matrix_world.copy();o.parent=parent;o.matrix_world=mw
 o=box('THK_InnerArmrest_'+sd,(-.14,sg*.849,.727),(.45,.065,.043),LEATHER,.015);mw=o.matrix_world.copy();o.parent=parent;o.matrix_world=mw
 o=box('THK_InnerRelease_'+sd,(.13,sg*.842,.766),(.10,.015,.024),STEEL,.006);mw=o.matrix_world.copy();o.parent=parent;o.matrix_world=mw
# Swept dashboard mesh closes at the cowl, with a driver instrument hood.
v=[(.37,-.77,.64),(.37,.77,.64),(.38,-.77,.78),(.38,.77,.78),(.60,-.81,.854),(.60,.81,.854),(.88,-.82,.868),(.88,.82,.868),(.88,-.78,.65),(.88,.78,.65)]
f=[(0,1,3,2),(2,3,5,4),(4,5,7,6),(6,7,9,8),(0,8,9,1),(0,2,4,6,8),(1,9,7,5,3)]
ob=mesh('THK_InterpretedDashboard',v,f,DASH,sub=0);mod=ob.modifiers.new('PaddedDashEdges','BEVEL');mod.width=.018;mod.segments=4;ob.modifiers.new('DashNormals','WEIGHTED_NORMAL')
box('THK_InstrumentBinnacle',(.391,.40,.809),(.18,.48,.153),DASH,.025)
# Gauges oriented along X, facing the seated driver at -X.
def cylinder(n,a,b,r,m):
 a=Vector(a);b=Vector(b);d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r,depth=d.length,location=(a+b)/2);o=take(bpy.context.object,n,m);o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return o
for i,(yy,rr) in enumerate([(.28,.053),(.43,.053),(.555,.031)]):
 cylinder('THK_GaugeBezel'+str(i),(.291,yy,.818),(.302,yy,.818),rr+ .004,STEEL)
 cylinder('THK_GaugeFace'+str(i),(.286,yy,.818),(.291,yy,.818),rr,GAUGE)
 for k in range(25):
  a=math.radians(-135+k*270/24);r0=rr*.76;r1=rr*.91
  curve('THK_GaugeTick'+str(i)+'_'+str(k),[(.284,yy+r0*sin(a),.818+r0*cos(a)),(.284,yy+r1*sin(a),.818+r1*cos(a))],.0009 if k%5==0 else .00045,MARK)
 a=math.radians(-70+i*40);curve('THK_GaugeNeedle'+str(i),[(.281,yy,.818),(.281,yy+rr*.75*sin(a),.818+rr*.75*cos(a))],.001,ORANGE)
 # Tiny numerals are actual editable text, not random technical decoration.
 for k,label in enumerate(['0','40','80','120','160'] if i<2 else ['E','F']):
  a=math.radians(-125+k*(250/(4 if i<2 else 1)));data=bpy.data.curves.new('GaugeNumeral','FONT');data.body=label;data.size=.007 if i<2 else .005;data.align_x='CENTER';data.align_y='CENTER';o=bpy.data.objects.new('THK_GaugeNumeral'+str(i)+str(k),data);CAB.objects.link(o);o.location=(.282,yy+rr*.60*sin(a),.818+rr*.60*cos(a));o.rotation_euler=(pi/2,0,-pi/2);data.materials.append(MARK)
# Center vents, radio, switches and flight control bank.
for yy in [-.16,.03]:
 box('THK_VentFrame'+str(yy),(.365,yy,.80),(.024,.15,.067),BLACK,.008)
 for k in range(5):box('THK_VentSlat'+str(yy)+str(k),(.350,yy,.778+k*.011),(.010,.131,.003),STEEL,.001)
box('THK_RadioPanel',(.368,-.08,.693),(.028,.275,.084),BLACK,.006)
box('THK_RadioDisplay',(.350,-.086,.71),(.003,.143,.021),VISOR,.002)
for yy in [-.19,.03]:cylinder('THK_RadioKnob'+str(yy),(.334,yy,.68),(.352,yy,.68),.012,STRAP)
box('THK_CenterTunnel',(-.05,0,.51),(.99,.245,.17),DASH,.024)
box('THK_ShifterBoot',(.13,0,.609),(.15,.136,.035),LEATHER,.018)
cylinder('THK_Shifter',(.13,0,.62),(.10,0,.715),.009,STEEL);ell('THK_ShifterKnob',(.10,0,.72),(.025,.022,.025),STRAP)
box('THK_Handbrake',(-.13,-.065,.619),(.22,.026,.027),STRAP,.008)
for i in range(5):box('THK_FlightToggle_'+str(i),(.275,-.07+i*.033,.626),(.025,.017,.025),RED if i==0 else STEEL,.003)
# Steering: 3 spokes, leather rim, column and stalk. Rim matches hand centers.
cylinder('THK_SteeringColumn',(.48,.40,.69),(.16,.40,.79),.023,DASH)
pts=[(.162,.40+.151*cos(i*2*pi/96),.79+.151*sin(i*2*pi/96)) for i in range(97)];curve('THK_SteeringRim',pts,.012,LEATHER)
cylinder('THK_SteeringHub',(.147,.4,.79),(.18,.4,.79),.043,DASH)
for a in [0,2*pi/3,4*pi/3]:
 curve('THK_SteeringSpoke'+str(a),[(.162,.4+.035*cos(a),.79+.035*sin(a)),(.162,.4+.137*cos(a),.79+.137*sin(a))],.014,STEEL)
box('THK_HornPad',(.142,.4,.79),(.016,.065,.052),LEATHER,.014)
curve('THK_IndicatorStalk',[(.23,.40,.76),(.23,.58,.75),(.21,.60,.75)],.007,DASH)
for i,yy in enumerate([.29,.41,.52]):
 cylinder('THK_PedalStem'+str(i),(.56,yy,.46),(.47,yy,.445),.006,STEEL)
 o=box('THK_Pedal'+str(i),(.462,yy,.447),(.019,.056,.064),BLACK,.006);o.rotation_euler[1]=-.4
 for k in range(4):box('THK_PedalGrip'+str(i)+str(k),(.450,yy,.426+k*.013),(.003,.047,.003),STEEL,.001)
# Cabin visibility through physically transmitting glass, keeps originals intact.
for ob in bpy.data.collections['THK9_Exterior'].objects:
 if ob.type=='MESH' and any(k in ob.name for k in ['Windshield','DoorGlass','RearGlass','QuarterGlass','RoofInset']) and 'Frame' not in ob.name:
  if ob.data.materials:
   original=ob.data.materials[0]
   if 'Glass' in original.name:
    m=bpy.data.materials.get('THK11_TransmittingGlass')
    if not m:
     m=original.copy();m.name='THK11_TransmittingGlass';p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(.80,.89,.94,1);p.inputs['Metallic'].default_value=0;p.inputs['Roughness'].default_value=.065;p.inputs['Transmission Weight'].default_value=1;p.inputs['IOR'].default_value=1.45
    ob.data.materials[0]=m
RIG=RIG_CHARACTER
S['THK_Version']='V11';S['THK11_Interior']='User-authorized interpretation, not documented replica';S['MT_Character']='Single rig, mask_on and driving_pose controls'
S.frame_set(97);RIG['driving_pose']=1.0;RIG['mask_on']=False;bpy.context.view_layer.update()
# Save vehicle and independent editable library assets without duplicating Matt.
bpy.ops.wm.save_as_mainfile(filepath=str(T/'Thunderhawk_V11.blend'),compress=True)
# Independent assets are exported by export_characters_v11.py after visual refinements.
print('THK11_BASE_BUILD_SAVED')

