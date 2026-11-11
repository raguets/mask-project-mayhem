import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.kdtree import KDTree
from math import sin,cos,pi,exp,sqrt
P=Path('G:/DEV/mask-project-mayhem');T=P/'art_source/Thunderhawk';S=bpy.context.scene
RIG=bpy.data.objects['MattTrakker_Rig'];CHAR=bpy.data.collections['MT11_Character'];MASK=bpy.data.collections['Spectrum11_Asset'];CURRENT=CHAR;BONES={b.name:True for b in RIG.data.bones}
source=(T/'scripts/build_thunderhawk_v11.py').read_text(encoding='utf-8-sig');refine=(T/'scripts/refine_thunderhawk_v11.py').read_text(encoding='utf-8-sig')
helper=source[source.index('def take('):source.index('# Skeleton in')];helper=helper.replace("bpy.context.view_layer.objects.active=ob;ob.select_set(True);", "bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=ob;ob.select_set(True);");exec(helper)
for k,n in {'SUIT':'MT2_WovenGrey','SEAM':'MT2_SeamGrey','HAIR':'MT2_BlondHair','HAIRHI':'MT2_BlondHighlights','DASH':'THK11_Dashboard','INSERT':'THK11_SeatInsert'}.items():globals()[k]=bpy.data.materials[n]
# Footwell is lower than the raised seat platforms; keep all originals in backup.
code=refine[refine.index('# Recompute poses'):refine.index('# Correct upholstery')]
code=code.replace('(.355,sg*.115,.401)','(.430,sg*.115,.430)').replace('(.485,sg*.115,.350)','(.560,sg*.115,.379)')
exec(code)
# Make a continuous cloth sculpt while retaining original editable loft cages.
RIG['driving_pose']=0;RIG.location=(0,0,0);RIG.update_tag();S.frame_set(1);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
parts=[o for o in CHAR.objects if o.name.startswith(('MT_Suit_Torso','MT_ContinuousSleeve','MT_ContinuousTrouser','MT_DeltoidCloth'))]
if parts and not bpy.data.objects.get('MT_ContinuousFlightSuit'):
 vv=[];ff=[];samples=[];sw=[]
 for ob in parts:
  for v in ob.data.vertices:
   samples.append(ob.matrix_world@v.co);sw.append({ob.vertex_groups[g.group].name:g.weight for g in v.groups})
  ev=ob.evaluated_get(dg);me=ev.to_mesh();offset=len(vv);vv.extend(tuple(ev.matrix_world@v.co) for v in me.vertices);ff.extend(tuple(offset+i for i in p.vertices) for p in me.polygons);ev.to_mesh_clear()
 me=bpy.data.meshes.new('MT_ContinuousSuit_Sculpt');me.from_pydata(vv,[],ff);me.update();me.materials.append(SUIT)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new('MT_ContinuousFlightSuit',me);CHAR.objects.link(ob);bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 mod=ob.modifiers.new('UnifiedClothVolume','REMESH');mod.mode='VOXEL';mod.voxel_size=.0045;mod.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=mod.name)
 mod=ob.modifiers.new('ClothVolumeRelax','SMOOTH');mod.factor=.75;mod.iterations=6;bpy.ops.object.modifier_apply(modifier=mod.name)
 kd=KDTree(len(samples))
 for i,p in enumerate(samples):kd.insert(p,i)
 kd.balance();groups={n:ob.vertex_groups.new(name=n) for n in BONES}
 for v in ob.data.vertices:
  found=kd.find_n(v.co,4);acc={};total=0
  for p,i,d in found:
   w=1/max(d,.001)**2;total+=w
   for n,val in sw[i].items():acc[n]=acc.get(n,0)+w*val
  norm=sum(acc.values())
  if norm:
   for n,val in acc.items():
    if val/norm>.001:groups[n].add([v.index],val/norm,'REPLACE')
 mod=ob.modifiers.new('ContinuousSuitSkin','ARMATURE');mod.object=RIG;mod.use_deform_preserve_volume=True;ob.parent=RIG
 for p in ob.data.polygons:p.use_smooth=True
 cages=bpy.data.collections.new('MT_EditableLoftCages');CHAR.children.link(cages);cages.hide_render=True;cages.hide_viewport=True
 for old in parts:CHAR.objects.unlink(old);cages.objects.link(old)
 ob['topology_note']='Voxel-unified cloth sculpt; editable weighted source lofts retained in MT_EditableLoftCages. Retopology required for shipping game asset.'
# Shorter, flatter side-parted hair; remove the raised part line seen in review.
for ob in list(CHAR.objects):
 if ob.name.startswith('MT_Hair'):bpy.data.objects.remove(ob,do_unlink=True)
headcode=refine[refine.index('def profile('):refine.index('facepart=')];exec(headcode)
base_head=headpoint
def hairpoint(z,a):
 x,y,_=base_head(min(z,1.816),a)
 if z>1.75:
  rr=sqrt(max(0,1-((z-1.735)/.083)**2));x=-.008+.077*rr*cos(a);y=.075*rr*sin(a)
 return x,y,z
vv=[];ff=[];NN=96;RR=33
for j in range(RR):
 t=j/(RR-1)
 for i in range(NN):
  a=2*pi*i/NN;u=max(0,min(1,(cos(a)-.22)/.48));u=u*u*(3-2*u);base=1.711+.046*u;z=base+(1.8175-base)*sin(t*pi/2);x,y,_=hairpoint(z,a);off=.0025
  vv.append((x+off*cos(a),y+off*sin(a),z+.002*u*sin(pi*t)))
for j in range(RR-1):ff.extend((j*NN+i,j*NN+(i+1)%NN,(j+1)*NN+(i+1)%NN,(j+1)*NN+i) for i in range(NN))
mesh('MT_Hair_ShortSidePart',vv,ff,HAIR,'head',sub=2)
for k in range(130):
 a=2*pi*k/130;u=max(0,min(1,(cos(a)-.22)/.48));u=u*u*(3-2*u);base=1.711+.046*u;pts=[]
 for j in range(19):
  t=j/18*.90;angle=a+.42*sin(pi*t);z=base+(1.8175-base)*sin(t*pi/2);x,y,_=hairpoint(z,angle);pts.append((x+.0028*cos(angle),y+.0028*sin(angle),z+.002*u*sin(pi*t)))
 curve('MT_HairLock_'+str(k),pts,.00022,HAIRHI if k%6==0 else HAIR,'head')
# Side part lies on the cap, not above it.
pts=[]
for i in range(33):
 x=.051-.103*i/32;y=-.022;z=1.735+.083*sqrt(max(0,1-((x+.008)/.077)**2-(y/.075)**2))+.0027;pts.append((x,y,z))
curve('MT_HairPart',pts,.0004,HAIR,'head')
for ob in CHAR.objects:
 if ob.name.startswith('MT_Hair'):
  for prop in ['hide_render','hide_viewport']:
   d=ob.driver_add(prop).driver;v=d.variables.new();v.name='mask';v.type='SINGLE_PROP';v.targets[0].id=RIG;v.targets[0].data_path='["mask_on"]';d.expression='mask'
# Recess footwells; legacy exterior blackout would otherwise bisect the boots.
for name in ['THK_ExteriorBlackout']:
 ob=bpy.data.objects.get(name)
 if ob:ob.hide_render=True;ob.hide_viewport=True;ob['superseded_by']='THK11 interior footwells'
floor=bpy.data.objects['THK_CabinCarpet']
# Mesh coordinates are world-space, so reduce the old slab to rear seat platforms.
for v in floor.data.vertices:
 v.co.x=-.45+(v.co.x+.02)*.57
CURRENT=bpy.data.collections['THK11_Interior'];oldrig=RIG;RIG=None
for sg,sd in [(1,'L'),(-1,'R')]:
 box('THK_RecessedFootwell_'+sd,(.53,sg*.40,.310),(.79,.61,.018),INSERT,.007)
 box('THK_FootwellStep_'+sd,(.12,sg*.40,.365),(.025,.61,.105),DASH,.005)
for ob in CURRENT.objects:
 if ob.name.startswith(('THK_Pedal','THK_PedalStem','THK_PedalGrip')):ob.location.x+=.125;ob.location.z-=.025
RIG=oldrig;RIG.location=(0,.4,0);RIG['driving_pose']=1;RIG['mask_on']=False;RIG.update_tag();S.frame_set(97);bpy.context.view_layer.update()
# Technical and artistic limits remain explicit.
S['MT_ArtStatus']='Reference-based semi-realistic interpretation, not validated photorealistic replica'
S['MT_SourcePortrait']='Images de reference/Matt Trakker/images (7).jpg: angular jaw, short blond hair, blue-grey eyes'
S['THK11_CockpitStatus']='Interpreted cockpit, user authorized 2026-11-02'
# Ensure interior moves with vehicle root except door cards already parented.
for ob in CURRENT.objects:
 if ob.parent is None:
  mw=ob.matrix_world.copy();ob.parent=bpy.data.objects['THK_Root'];ob.matrix_world=mw
bpy.ops.wm.save_as_mainfile(filepath=str(T/'Thunderhawk_V11.blend'),compress=True)
print('V11_CONTINUOUS_SUIT_HAIR_FOOTWELL_SAVED',flush=True)
