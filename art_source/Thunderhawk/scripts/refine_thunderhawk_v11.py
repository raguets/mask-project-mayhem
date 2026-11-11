"""Visual corrections after inspected V11 renders; single character retained."""
import bpy,math,json,random
from pathlib import Path
from mathutils import Vector,Matrix
from math import sin,cos,pi,exp,sqrt
P=Path('G:/DEV/mask-project-mayhem');T=P/'art_source/Thunderhawk';S=bpy.context.scene
RIG=bpy.data.objects['MattTrakker_Rig'];CHAR=bpy.data.collections['MT11_Character'];MASK=bpy.data.collections['Spectrum11_Asset'];CURRENT=CHAR;BONES={b.name:True for b in RIG.data.bones}
source=(T/'scripts/build_thunderhawk_v11.py').read_text(encoding='utf-8-sig')
helper=source[source.index('def take('):source.index('# Skeleton in')]
helper=helper.replace("bpy.context.view_layer.objects.active=ob;ob.select_set(True);", "bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=ob;ob.select_set(True);")
exec(helper)
for key,name in {'SUIT':'MT2_WovenGrey','SEAM':'MT2_SeamGrey','RED':'MT2_RedLeather','STRAP':'MT2_HarnessWebbing','STEEL':'MT2_BrushedBuckle','SKIN':'MT2_Skin','LIP':'MT2_Lips','HAIR':'MT2_BlondHair','HAIRHI':'MT2_BlondHighlights','WHITE':'MT2_EyeWhite','IRIS':'MT2_GreyBlueIris','PUPIL':'MT2_Pupil','SHADOW':'MT2_FaceCrease'}.items():globals()[key]=bpy.data.materials[name]
# Restore modifiers accidentally baked by multi-selection during curve conversion.
for ob in list(CHAR.objects)+list(MASK.objects):
 if ob.type=='MESH' and ob.vertex_groups and not any(m.type=='ARMATURE' for m in ob.modifiers):
  mod=ob.modifiers.new('MT_Deform','ARMATURE');mod.object=RIG;mod.use_deform_preserve_volume=True
# Preserve first pass for comparison, edit only new V11 source scene.
if not (T/'Thunderhawk_V11_before_fidelity_refinement.blend').exists():bpy.ops.wm.save_as_mainfile(filepath=str(T/'Thunderhawk_V11_before_fidelity_refinement.blend'),copy=True,compress=True)
# Recompute poses including bone length scale; eliminate disconnected wrist gaps.
for pb in RIG.pose.bones:
 for prop in ['location','rotation_quaternion','scale']:
  try:pb.driver_remove(prop)
  except Exception:pass
 pb.location=(0,0,0);pb.rotation_mode='QUATERNION';pb.rotation_quaternion=(1,0,0,0);pb.scale=(1,1,1)
for b in RIG.data.bones:b.inherit_scale='NONE'
rest={n:(tuple(b.head_local),tuple(b.tail_local)) for n,b in RIG.data.bones.items()}
restpose={p.name:(tuple(p.location),tuple(p.rotation_quaternion),tuple(p.scale)) for p in RIG.pose.bones}
seated={'pelvis':((-.39,0,.51),(-.43,0,.63)),'spine':((-.43,0,.63),(-.51,0,.80)),'chest':((-.51,0,.80),(-.58,0,.94)),'neck':((-.58,0,.94),(-.60,0,.985)),'head':((-.60,0,.985),(-.60,0,1.215))}
for sg,sd in [(1,'L'),(-1,'R')]:
 seated['upper_arm.'+sd]=((-.51,sg*.195,.88),(-.17,sg*.215,.735))
 seated['forearm.'+sd]=((-.17,sg*.215,.735),(.135,sg*.143,.790))
 seated['hand.'+sd]=((.135,sg*.143,.790),(.223,sg*.138,.790))
 seated['thigh.'+sd]=((-.39,sg*.095,.51),(.025,sg*.115,.525))
 seated['shin.'+sd]=((.025,sg*.115,.525),(.355,sg*.115,.401))
 seated['foot.'+sd]=((.355,sg*.115,.401),(.485,sg*.115,.350))
bpy.context.view_layer.update()
for n in rest:
 pb=RIG.pose.bones[n];a,b=map(Vector,seated[n]);ra,rb=map(Vector,rest[n]);rot=(rb-ra).rotation_difference(b-a)@RIG.data.bones[n].matrix_local.to_quaternion();scale=Vector((1,(b-a).length/(rb-ra).length,1))
 pb.matrix=Matrix.LocRotScale(a,rot,scale);bpy.context.view_layer.update()
seatpose={p.name:(tuple(p.location),tuple(p.rotation_quaternion),tuple(p.scale)) for p in RIG.pose.bones}
for n in rest:
 pb=RIG.pose.bones[n]
 for idx,prop in enumerate(['location','rotation_quaternion','scale']):
  aa=restpose[n][idx];bb=list(seatpose[n][idx])
  if prop=='rotation_quaternion' and sum(a*b for a,b in zip(aa,bb))<0:bb=[-v for v in bb]
  for k,(a,b) in enumerate(zip(aa,bb)):
   dr=pb.driver_add(prop,k).driver;v=dr.variables.new();v.name='pose';v.type='SINGLE_PROP';v.targets[0].id=RIG;v.targets[0].data_path='["driving_pose"]';dr.expression=f'{a:.12g}+pose*({b-a:.12g})'
# Correct upholstery rotations around their own centers, not global origin.
for ob in bpy.data.collections['THK11_Interior'].objects:
 if ob.type=='MESH' and sum(abs(a) for a in ob.rotation_euler)>.001 and len(ob.data.vertices):
  center=sum((v.co for v in ob.data.vertices),Vector())/len(ob.data.vertices)
  if ob.location.length<.0001:
   for v in ob.data.vertices:v.co-=center
   ob.location=center
# Sculpt a broader, straight-jawed head matching the supplied portrait.
for ob in list(CHAR.objects):
 if ob.name.startswith(('MT_Head_','MT_Eye','MT_Iris','MT_Pupil','MT_Brow','MT_Ear','MT_Concha','MT_Nostril','MT_Nasolabial','MT_Lip_','MT_Mouth','MT_Philtrum','MT_Hair','MT_Sideburn','MT_Lash')):bpy.data.objects.remove(ob,do_unlink=True)
def profile(z,table):
 # Cubic Hermite profile with finite slopes avoids horizontal bands on the face.
 for j,((a,x),(b,y)) in enumerate(zip(table,table[1:])):
  if z<=b:
   t=max(0,min(1,(z-a)/(b-a)));d=(y-x)/(b-a)
   m0=d if j==0 else (y-table[j-1][1])/(b-table[j-1][0]);m1=d if j+2==len(table) else (table[j+2][1]-x)/(table[j+2][0]-a)
   return (2*t**3-3*t*t+1)*x+(t**3-2*t*t+t)*(b-a)*m0+(-2*t**3+3*t*t)*y+(t**3-t*t)*(b-a)*m1
 return table[-1][1]
def headpoint(z,a,hair=False):
 w=profile(z,[(1.55,.040),(1.575,.055),(1.595,.067),(1.62,.073),(1.66,.077),(1.70,.075),(1.75,.075),(1.78,.064),(1.80,.041),(1.817,.001)])
 front=profile(z,[(1.55,.028),(1.575,.065),(1.595,.079),(1.62,.078),(1.65,.073),(1.68,.073),(1.705,.071),(1.733,.078),(1.76,.074),(1.79,.052),(1.817,.001)])
 back=profile(z,[(1.55,.037),(1.59,.064),(1.65,.087),(1.71,.092),(1.76,.080),(1.80,.046),(1.817,.001)])
 ca=cos(a);yy=w*sin(a);xx=(front*max(0,ca)**.35 if ca>=0 else back*ca)-.008
 facing=max(0,ca)**10
 bump=.025*exp(-((z-1.674)/.017)**2-(yy/.012)**2)+.018*exp(-((z-1.702)/.030)**2-(yy/.010)**2)
 bump+=.005*exp(-((z-1.663)/.008)**2-((abs(yy)-.012)/.006)**2)
 bump-=.006*exp(-((z-1.708)/.011)**2-((abs(yy)-.034)/.017)**2)
 bump+=.005*exp(-((z-1.724)/.008)**2-((abs(yy)-.034)/.024)**2)
 return(xx+bump*facing,yy,z)
facepart=source[source.index('v=[];f=[];HN=128;HZ=97'):source.index('# Eyes: recessed')]
exec(facepart)
# Eyes with actual almond apertures: no exposed white spheres or floating brows.
for sg,sd in [(1,'L'),(-1,'R')]:
 ey=sg*.034;ez=1.708;vv=[];ff=[];cols=[];NU=49;NV=13
 def eyept(u,t):
  zz=ez+(.0055*sin(pi*(u+1)/2) if t>=0 else .0038*sin(pi*(u+1)/2))*t
  yy=ey+.0165*u
  x,y,z=headpoint(zz,math.asin(max(-.99,min(.99,yy/.075))))
  return (x+.0018+.0015*(1-u*u)*(1-t*t),yy,zz)
 for j in range(NV):
  t=j/(NV-1)*2-1
  for i in range(NU):vv.append(eyept(i/(NU-1)*2-1,t))
 for j in range(NV-1):
  for i in range(NU-1):
   ids=(j*NU+i,j*NU+i+1,(j+1)*NU+i+1,(j+1)*NU+i);ff.append(ids)
   center=sum((Vector(vv[k]) for k in ids),Vector())/4;rr=sqrt((center.y-ey)**2+(center.z-ez)**2);cols.append(2 if rr<.0024 else 1 if rr<.0053 else 0)
 ob=mesh('MT_EyeAlmond_'+sd,vv,ff,WHITE,'head',sub=1);ob.data.materials.append(IRIS);ob.data.materials.append(PUPIL)
 for p,idx in zip(ob.data.polygons,cols):p.material_index=idx
 for upper in [True,False]:
  pts=[eyept(i/32*2-1,1 if upper else -1) for i in range(33)];curve('MT_Eyelid_'+sd+str(upper),[(x+.0006,y,z) for x,y,z in pts],.00145,SKIN,'head')
  if upper:curve('MT_Lashline_'+sd,[(x+.0009,y,z-.0004) for x,y,z in pts],.0003,SHADOW,'head')
 # Low straighter blond brows are fitted directly on the supraorbital ridge.
 pts=[]
 for j in range(25):
  u=j/24;yy=ey-.022+.044*u;z=1.725+.0025*sin(pi*u);x,_,_=headpoint(z,math.asin(max(-.99,min(.99,yy/.075))));pts.append((x+.001,yy,z))
 curve('MT_Brow_'+sd,pts,.0015,HAIR,'head')
 ell('MT_EarBase_'+sd,(-.020,sg*.078,1.677),(.014,.008,.028),SKIN,'head')
 ell('MT_Concha_'+sd,(-.011,sg*.084,1.677),(.007,.001,.012),LIP,'head')
 curve('MT_EarHelix_'+sd,[(-.02+.012*cos(i*2*pi/48),sg*.086,1.678+.024*sin(i*2*pi/48)) for i in range(49)],.0027,SKIN,'head')
 curve('MT_EarAntihelix_'+sd,[(-.018,sg*.087,1.691),(-.009,sg*.088,1.685),(-.017,sg*.088,1.67)],.0018,SKIN,'head')
 ell('MT_Nostril_'+sd,(.087,sg*.010,1.663),(.0025,.003,.0012),SHADOW,'head')
# Reuse narrow lips, with less protrusion and no wire-like face creases.
lippart=source[source.index('# Lips are narrow'):source.index('# Short swept blond hair')]
lippart=lippart[:lippart.index("curve('MT_PhiltrumL'")];lippart=lippart.replace('.070+.009*(1-u*u)','.065+.005*(1-u*u)').replace('.080-.009*(u*u)','.071-.005*(u*u)')
exec(lippart)
# Short side-parted blond cap. More angular hairline and broad low crown.
vv=[];ff=[];NN=96;RR=33
for j in range(RR):
 t=j/(RR-1)
 for i in range(NN):
  a=2*pi*i/NN;front=max(0,cos(a));base=1.709+.052*front
  zz=base+(1.821-base)*sin(t*pi/2);x,y,_=headpoint(min(1.816,zz),a);off=.0025+.002*sin(pi*t)
  # Swept top, bounded crown rather than a pointed tuft.
  vv.append((x+off*cos(a),y+off*sin(a),zz+.004*front*sin(pi*t)))
for j in range(RR-1):ff.extend((j*NN+i,j*NN+(i+1)%NN,(j+1)*NN+(i+1)%NN,(j+1)*NN+i) for i in range(NN))
mesh('MT_Hair_SidePartCap',vv,ff,HAIR,'head',sub=2)
for k in range(112):
 a=2*pi*k/112;front=max(0,cos(a));base=1.709+.052*front;pts=[]
 for j in range(17):
  t=j/16*.91;angle=a+.52*sin(pi*t);zz=base+(1.821-base)*sin(t*pi/2);x,y,_=headpoint(min(1.816,zz),angle);off=.003+.002*sin(pi*t)
  pts.append((x+off*cos(angle),y+off*sin(angle),zz+.004*front*sin(pi*t)))
 curve('MT_HairSweptLock_'+str(k),pts,.00025,HAIRHI if k%5==0 else HAIR,'head')
curve('MT_HairSidePart',[(.055,-.033,1.778),(.029,-.031,1.807),(0,-.025,1.819),(-.036,-.018,1.809),(-.064,-.012,1.786)],.0011,SEAM,'head')
# Rounded deltoids replace flat shoulder caps; graded bone weights follow sleeves.
for sg,sd in [(1,'L'),(-1,'R')]:
 ob=ell('MT_DeltoidCloth_'+sd,(-.006,sg*.181,1.427),(.079,.080,.084),SUIT,'upper_arm.'+sd)
 for v in ob.data.vertices:
  if v.co.z<1.407:v.co.z=1.407+(v.co.z-1.407)*.6
# Smooth excessive periodic folds while retaining the editable cages.
for ob in CHAR.objects:
 if ob.name.startswith(('MT_ContinuousSleeve','MT_ContinuousTrouser')):
  mod=ob.modifiers.new('ClothFoldRelax','SMOOTH');mod.factor=.65;mod.iterations=4
# Skin and hair tones: light warm skin and golden blond rather than brown.
for m,col in [(SKIN,(.63,.40,.27)),(LIP,(.34,.155,.105)),(HAIR,(.43,.255,.045)),(HAIRHI,(.52,.33,.075))]:
 m.diffuse_color=(*col,1);next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'].default_value=(*col,1)
# Reattach restored hair visibility drivers.
for ob in CHAR.objects:
 if ob.name.startswith('MT_Hair'):
  for prop in ['hide_render','hide_viewport']:
   dr=ob.driver_add(prop).driver;v=dr.variables.new();v.name='mask';v.type='SINGLE_PROP';v.targets[0].id=RIG;v.targets[0].data_path='["mask_on"]';dr.expression='mask'
# Flatten small crown point on Spectrum, and remove open jaw plate intersections.
for ob in MASK.objects:
 if ob.type=='MESH' and ob.name=='Spectrum_SilverHelmetShell':
  for v in ob.data.vertices:
   if v.co.z>1.835:v.co.z=1.835+(v.co.z-1.835)*.45
 if ob.name.startswith('Spectrum_JawShell'):
  for mod in list(ob.modifiers):
   if mod.type=='SUBSURF':mod.levels=0;mod.render_levels=0
  mod=ob.modifiers.new('JawFillet','BEVEL');mod.width=.008;mod.segments=4
RIG['driving_pose']=1;RIG['mask_on']=False;RIG.update_tag();S.frame_set(97);bpy.context.view_layer.update();S.name='THK_V11_Cockpit_Matt_Spectrum'
bpy.ops.wm.save_as_mainfile(filepath=str(T/'Thunderhawk_V11.blend'),compress=True)
print('V11_FIDELITY_REFINEMENT_SAVED')

