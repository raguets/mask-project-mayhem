"""Correct the visible first review defects, keeping every weighted character."""
import bpy,math,json,ast,re,random
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from math import sin,cos,pi
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Rhino';S=bpy.context.scene
assert not S.get('Rhino_refinement_v1')
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Rhino_V1_first_review.blend'),copy=True,compress=True)
for name in ['build_rhino_v1.py','build_characters_v1.py']:
 tree=ast.parse((A/'scripts'/name).read_text(encoding='utf-8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'<geometry_helpers>','exec'))
ROOT=bpy.data.objects['Rhino_Control'];S.frame_set(1);ROOT.update_tag();bpy.context.view_layer.update()
# Recess the bullbar guides in road state, extending only with the bullbar.
for sg in [-1,1]:
 ob=bpy.data.objects['RH_BullbarGuide_'+str(sg)]
 for v in ob.data.vertices:v.co.x-=4.6
 ob.location.x=4.6
 drive(ob,'scale',0,'(0.30+0.80*max(v,min(1,max(0,b/0.25))))/0.92',[('v',ROOT,'bullbar'),('b',ROOT,'battle_mode')])
# Dock ends clear of the module deck; the truck retains outboard axle outriggers.
for y in [-.59,.59]:
 ob=bpy.data.objects['RH_TruckFrame_'+str(y)]
 for v in ob.data.vertices:
  if v.co.x<0:v.co.x=-1.32
ob=bpy.data.objects['RH_FrameCrossmember_-1.35']
for v in ob.data.vertices:v.co.x+=.10
# Keep missile noses inside the closed hatch, deploy aft under the fixed roof.
launch=bpy.data.objects['RH_MissileLauncherLift'];launch.driver_remove('location',2)
variables=[('v',ROOT,'launcher_up'),('h',ROOT,'rear_open'),('b',ROOT,'battle_mode')]
u='min(max(v,min(1,max(0,(b-0.80)/0.20))),min(1,max(0,(max(h,min(1,max(0,(b-0.42)/0.36)))-0.92)/0.08)))'
drive(launch,'location',0,'0.42-1.30*('+u+')',variables)
drive(launch,'location',2,'2.72+0.55*('+u+')',variables)
# Fold the auxiliary seat back in road mode rather than showing a tall chair above the fifth wheel.
CURRENT=bpy.data.collections['Rhino_RearVehicle'];pod=bpy.data.objects['Rhino_RearVehicle_Root']
pivot=empty('RH_PodSeatBackFold',(-2.64,0,1.22));parent(pivot,pod)
ob=bpy.data.objects['RH_PodSeatBack'];matrix=ob.matrix_world.copy();ob.parent=pivot;ob.matrix_parent_inverse=pivot.matrix_world.inverted();ob.matrix_world=matrix
drive(pivot,'rotation_euler',1,'-1.57079632679*(1-min(1,max(0,(max(d,min(1,max(0,(b-0.12)/0.43)))-0.70)/0.30)))',[('d',ROOT,'rear_detach'),('b',ROOT,'battle_mode')])
# Plain hand skin, since the anatomical face shader expects face-specific color attributes.
hand=material('Character_HandSkin',(.57,.34,.225),0,.5);p=next(n for n in hand.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Subsurface Weight'].default_value=.08
for code in ['AS','BS']:
 char=bpy.data.collections[code+'_Character'];CURRENT=char;r=bpy.data.objects['AlexSector_Rig' if code=='AS' else 'BruceSato_Rig'];r['driving_pose']=0;r.location=(0,0,0);r['mask_on']=False;r.update_tag();bpy.context.view_layer.update()
 suit=bpy.data.objects[code+'_ContinuousFlightSuit'];head=bpy.data.objects[code+'_Head_AnatomicalSurface'];shirt=bpy.data.materials[code+'_WovenShirt'];vest=bpy.data.materials[code+'_Vest'];accent=bpy.data.materials[code+'_Leather']
 for ob in list(char.all_objects):
  if ob.type!='MESH':continue
  if 'FittedVest' in ob.name or (code=='AS' and 'KneePatch' in ob.name):bpy.data.objects.remove(ob,do_unlink=True);continue
  if 'GloveSkin' in ob.name:
   for i in range(len(ob.data.materials)):ob.data.materials[i]=hand
  if code=='AS' and any(k in ob.name for k in ['ArmBand','Cuff']):
   for i in range(len(ob.data.materials)):ob.data.materials[i]=shirt
 # A regular surface grid avoids jagged cut edges and accidental sleeves.
 bv=BVHTree.FromPolygons([v.co for v in suit.data.vertices],[list(f.vertices) for f in suit.data.polygons])
 def width(z):return .145+.048*max(0,min(1,(z-1.09)/.30))
 def garment_panel(name,side,sg=1):
  v=[];f=[];ww=[];NR=38;NC=20
  for j in range(NR):
   z=1.075+j*.366/(NR-1);w=width(z)
   for i in range(NC):
    t=i/(NC-1);y=sg*(.065+t*(w-.065)) if side=='front' else -w+2*w*t
    sign=1 if side=='front' else -1;hit=bv.ray_cast(Vector((sign*.7,y,z)),Vector((-sign,0,0)),1.5)
    x=hit[0].x+sign*.010 if hit[0] else sign*(.105 if z>1.2 else .095)
    v.append((x,y,z));u=max(0,min(1,(z-1.16)/.22));ww.append({'spine':1-u,'chest':u})
  for j in range(NR-1):f.extend((j*NC+i,j*NC+i+1,(j+1)*NC+i+1,(j+1)*NC+i) for i in range(NC-1))
  ob=mesh(name,v,f,vest,smooth=True);bind(ob,r,weights=ww);mod=ob.modifiers.new('ClothThickness','SOLIDIFY');mod.thickness=.004;return ob
 for sg in [-1,1]:garment_panel(code+'_VestFront_'+str(sg),'front',sg)
 garment_panel(code+'_VestBack','back')
 # Distinct outfit neckline and pocket lips, fitted to torso rather than forearms.
 for sg in [-1,1]:
  bind(box(code+'_VestPocket_'+str(sg),(.108,sg*.116,1.13),(.022,.085,.095),vest,.01),r,'spine')
 if code=='AS':
  for name in ['AS_FittedRedBeard','AS_RedMoustache']:
   ob=bpy.data.objects.get(name)
   if ob:bpy.data.objects.remove(ob,do_unlink=True)
  beard=bpy.data.materials['AS_RedBeard'];head.data.update()
  def beard_selection(face):
   p=face.center;upper=1.623+.043*min(1,abs(p.y)/.073)
   mouth=(p.y/.034)**2+((p.z-1.604)/.012)**2<1
   return p.x>.018 and 1.552<p.z<upper and not mouth and not(abs(p.y)<.032 and p.z>1.618)
  ob=skin_shell('AS_FittedRedBeard',head,beard_selection,beard,.0038,r)
  for mod in list(ob.modifiers):
   if mod.type=='SOLIDIFY':ob.modifiers.remove(mod)
  sub=ob.modifiers.new('SoftBeardBoundary','SUBSURF');sub.levels=1;sub.render_levels=1
  ob=skin_shell('AS_RedMoustache',head,lambda face:face.center.x>.074 and abs(face.center.y)<.043 and 1.615<face.center.z<1.633,beard,.004,r)
  for mod in list(ob.modifiers):
   if mod.type=='SOLIDIFY':ob.modifiers.remove(mod)
  sub=ob.modifiers.new('SoftMoustacheBoundary','SUBSURF');sub.levels=1;sub.render_levels=1
  # Short real strands over the fitted beard, no red coating on the nose.
  rng=random.Random(21);vv=[];ff=[]
  for face in head.data.polygons:
   if not beard_selection(face) or rng.random()>.32:continue
   center=face.center+face.normal*.0045;direction=Vector((.05,.05*center.y,-1)).normalized();length=rng.uniform(.003,.007);side=Vector((0,.00024,0));idx=len(vv);vv.extend([tuple(center-side),tuple(center+side),tuple(center+direction*length)]);ff.append((idx,idx+1,idx+2))
  bind(mesh('AS_BeardShortFibers',vv,ff,beard),r)
  for ob in bpy.data.collections['AS_Mask'].all_objects:
   if 'CurvedBlueVisor' in ob.name:
    for v in ob.data.vertices:v.co.z-=.043
   if 'SilverCrown' in ob.name:
    for v in ob.data.vertices:v.co.z-=.025
   if 'FlaredHood' in ob.name:
    for v in ob.data.vertices:
     if v.co.z>1.70:v.co.z-=.015
 else:
  # Remove jagged shell edges in the first chest armor draft; retain fitted grid vest and ribs.
  for name in ['BS_ChestArmorSurface','BS_ShoulderArmor_L','BS_ShoulderArmor_R']:
   ob=bpy.data.objects.get(name)
   if ob:bpy.data.objects.remove(ob,do_unlink=True)
  skin_shell('BS_ChestArmorSurface',suit,lambda f:1.14<f.center.z<1.405 and f.center.x>.071 and abs(f.center.y)<.15,vest,.023,r)
  for sg,sd in [(1,'L'),(-1,'R')]:
   ob=cap('BS_SmoothShoulderPlate_'+sd,(-.005,sg*.20,1.404),(.095,.105,.091),accent,r)
   ob.vertex_groups.clear();ob.vertex_groups.new(name='upper_arm.'+sd).add(list(range(len(ob.data.vertices))),1,'REPLACE')
  # Character-specific nose/cheek proportions and dark brown irises.
  for v in head.data.vertices:
   p=v.co;p.x-=.012*math.exp(-(p.y/.027)**2-((p.z-1.651)/.030)**2);p.y*=1+.020*math.exp(-((p.z-1.659)/.035)**2)
  head.data.update()
  for ob in char.all_objects:
   if 'Iris_' in ob.name and ob.type=='MESH':
    attr=ob.data.color_attributes.get('IrisColor')
    if attr:
     for value in attr.data:
      grain=max(.35,min(1,value.color[1]/.115));value.color=(.075*grain,.040*grain,.016*grain,1)
  accent.diffuse_color=(.60,.065,.005,1)
  next(n for n in accent.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'].default_value=accent.diffuse_color
  for ob in bpy.data.collections['BS_Mask'].all_objects:
   if any(k in ob.name for k in ['Goggle','OrangeCrown']):
    for v in ob.data.vertices:v.co.z-=.035 if 'Goggle' in ob.name else .022
 r.location=(2.0,-.60 if code=='AS' else .60,1.37);r['driving_pose']=1.;r['mask_on']=False;r.update_tag()
# Transparent windows need a readable neutral transmission tint.
glass=bpy.data.materials.get('Rhino_TintedGlass');p=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(.68,.81,.84,1);p.inputs['Roughness'].default_value=.08
S['Rhino_refinement_v1']='Driver evaluation corrected, guide telescoping, dock clear, launcher aft lift, fitted vest grids, hands, beard/visor landmarks.'
bpy.data.objects['Review_Floor'].location.z+=.025
S.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Rhino_V1.blend'),compress=True);print('RHINO_V1_VISUAL_CORRECTIONS_SAVED')
