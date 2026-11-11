"""User-directed V2: lower hood/canopy, splayed glass, rotating radar, sliding cabinet.
Visible supplied toy forms inspected again. Dimensions and hidden linkages estimated.
"""
import bpy,ast,math,json,re
from pathlib import Path
from mathutils import Vector
from math import sin,cos,pi
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Rhino';S=bpy.context.scene;R=bpy.data.objects['Rhino_Control'];assert not (A/'Rhino_V2.blend').exists()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Rhino_V1_before_user_revision.blend'),copy=True,compress=True)
for file in ['build_rhino_v1.py','build_characters_v1.py']:
 tree=ast.parse((A/'scripts'/file).read_text(encoding='utf-8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'<helpers>','exec'))
S.frame_set(1);R.update_tag();bpy.context.view_layer.update()
BODY=bpy.data.collections['Rhino_Truck'];CAB=bpy.data.collections['Rhino_Interior'];CURRENT=BODY
RED=bpy.data.materials['Rhino_DeepBurgundy'];CHROME=bpy.data.materials['Rhino_Chrome'];ALU=bpy.data.materials['Rhino_SatinAluminium'];BLACK=bpy.data.materials['Rhino_ChassisGraphite'];DARK=bpy.data.materials['Rhino_Recess'];GLASS=bpy.data.materials['Rhino_TintedGlass'];GOLD=bpy.data.materials['Rhino_GoldStripe']
def map_world_geometry(ob,fn):
 matrix=ob.matrix_world.copy();inv=matrix.inverted()
 if ob.type=='MESH':
  for v in ob.data.vertices:v.co=inv@fn(matrix@v.co)
  ob.data.update()
 elif ob.type=='CURVE':
  for spline in ob.data.splines:
   for point in spline.points:
    p=fn(matrix@Vector(point.co[:3]));point.co=(*(inv@p),point.co[3])
 elif ob.type=='FONT':ob.location=fn(ob.location.copy())
def hood_height(p):p=p.copy();p.z=1.31+(p.z-1.31)*(1.04/1.46);return p
for ob in list(BODY.objects):
 if ob.name.startswith('RH_Hood'):map_world_geometry(ob,hood_height)
def grille_height(p):p=p.copy();p.z=1.10+(p.z-1.10)*(1.37/1.80);return p
for ob in list(BODY.objects):
 if ob.name.startswith('RH_Grille'):map_world_geometry(ob,grille_height)
# Lower the upper housing as a coherent shell; cabin windshield/roof stay at their established level.
def tower_height(p):p=p.copy();p.z=1.27+(p.z-1.27)*(.902);return p
housing=[]
for ob in list(S.objects):
 if ob.name.startswith(('RH_UpperCockpitSide_','RH_UpperCockpitRoof','RH_TowerSeam_','RH_TowerStripe_','RH_SideBadge_','RH_RearCabinetWing_','RH_UpperCockpitFloor','RH_UpperCommand')):
  map_world_geometry(ob,tower_height);housing.append(ob)
ramp=bpy.data.objects['RH_RearCockpitHatchPivot']
for ob in list(ramp.children):map_world_geometry(ob,tower_height)
ramp.driver_remove('rotation_euler',1)
drive(ramp,'rotation_euler',1,'-2.199*max(v,min(1,max(0,(b-0.42)/0.36)))',[('v',R,'rear_open'),('b',R,'battle_mode')])
# Two upper panes, lowered and splayed in plan: outside edges recede by 160mm (~9 degrees).
for ob in list(BODY.objects):
 if ob.name.startswith(('RH_UpperCockpitGlass_','RH_UpperWindowFrame_','RH_UpperWindowBottom')):bpy.data.objects.remove(ob,do_unlink=True)
for sg in [-1,1]:
 vertices=[(1.04,sg*.055,3.15),(.88,sg*1.09,3.15),(.29,sg*1.09,3.985),(.45,sg*.055,3.985)]
 ob=mesh('RH_UpperCockpitGlass_'+str(sg),vertices,[(0,1,2,3)],GLASS);mod=ob.modifiers.new('GlazingThickness','SOLIDIFY');mod.thickness=.012;parent(ob,R)
 for edge,(a,b) in enumerate([(0,1),(1,2),(2,3),(3,0)]):parent(path('RH_UpperWindowFrame_'+str((sg,edge)),[vertices[a],vertices[b]],.027,RED),R)
# Rear cabinet translates aft, independently of the fixed front glazing.
R['cabinet_slide']=0.;R.id_properties_ui('cabinet_slide').update(min=0,max=1,description='Recul du grand coffre : 0 ferme / 1 recule de 0.80m')
slide=empty('RH_RearCabinetSlide');parent(slide,R)
for ob in housing+[ramp]+[bpy.data.objects['RH_HatchHinge_'+str(sg)] for sg in [-1,1]]:
 matrix=ob.matrix_world.copy();ob.parent=slide;ob.matrix_parent_inverse=slide.matrix_world.inverted();ob.matrix_world=matrix
drive(slide,'location',0,'-0.80*max(v,min(1,max(0,(b-0.50)/0.33)))',[('v',R,'cabinet_slide'),('b',R,'battle_mode')])
for sg in [-1,1]:
 parent(tube('RH_CabinetSlideRail_'+str(sg),(-1.55,sg*.87,1.21),(.75,sg*.87,1.21),.038,ALU),R)
 parent(box('RH_CabinetCarriage_'+str(sg),(-.24,sg*.87,1.25),(1.05,.10,.085),BLACK,.014),slide)
# Replace the former light bar with the small rotating scanner visible on the toy roof.
old=bpy.data.objects.get('RH_RoofScannerPivot')
if old:
 for ob in list(old.children):bpy.data.objects.remove(ob,do_unlink=True)
 bpy.data.objects.remove(old,do_unlink=True)
base=tube('RH_RadarFixedBase',(-.20,0,4.035),(-.20,0,4.15),.085,CHROME);parent(base,slide)
radar=empty('RH_RadarRotation',(-.20,0,4.15));parent(radar,slide);before=set(bpy.data.objects)
tube('RH_RadarShaft',(-.20,0,4.13),(-.20,0,4.25),.033,ALU)
verts=[];faces=[];N=24
for z in [4.23,4.46]:
 for i in range(N):
  y=-.34+.68*i/(N-1);verts.append((-.16+.038*(1-(y/.34)**2),y,z))
for i in range(N-1):faces.append((i,i+1,N+i+1,N+i))
ob=mesh('RH_RadarAntenna',verts,faces,GOLD,smooth=True);mod=ob.modifiers.new('RadarPanelThickness','SOLIDIFY');mod.thickness=.035
for z in [4.23,4.46]:path('RH_RadarRim_'+str(z),[(-.16+.038*(1-(y/.34)**2),y,z) for y in [-.34+.68*i/24 for i in range(25)]],.013,ALU)
for y in [-.25,0,.25]:path('RH_RadarBackRib_'+str(y),[(-.215,y,4.24),(-.215,y,4.45)],.014,ALU)
children_since(before,radar)
R['radar_spin']=1.;R.id_properties_ui('radar_spin').update(min=0,max=1,description='Rotation independante du petit radar de toit')
drive(radar,'rotation_euler',2,'frame*0.05235987756*s',[('s',R,'radar_spin')])
# A single dark, ribbed projectile, matching the loose toy missile and promotional launch view.
launch=bpy.data.objects['RH_MissileLauncherLift']
for ob in list(launch.children):bpy.data.objects.remove(ob,do_unlink=True)
launch.animation_data_clear();launch.location=(-.10,-.30,2.74);bpy.context.view_layer.update();before=set(bpy.data.objects)
box('RH_LauncherCradle',(-.10,-.30,2.76),(.38,.42,.10),ALU,.02)
tube('RH_LauncherElevator',(-.10,-.30,2.48),(-.10,-.30,2.74),.072,CHROME)
tube('RH_MissileBody',(-.10,-.30,2.84),(-.10,-.30,3.50),.143,BLACK,N=48)
tube('RH_MissileNose',(-.10,-.30,3.50),(-.10,-.30,3.82),.143,BLACK,r2=.007,N=48)
for i in range(7):
 z=2.91+i*.072;tube('RH_MissileRib_'+str(i),(-.10,-.30,z-.012),(-.10,-.30,z+.012),.153,DARK,N=48)
for sg in [-1,1]:
 box('RH_MissileFin_'+str(sg),(-.10,-.30+sg*.163,3.10),(.045,.14,.45),BLACK,.015)
children_since(before,launch)
v=[('v',R,'launcher_up'),('h',R,'rear_open'),('c',R,'cabinet_slide'),('b',R,'battle_mode')]
u='min(max(v,min(1,max(0,(b-0.85)/0.15))),min(1,max(0,(max(h,min(1,max(0,(b-0.42)/0.36)))-0.92)/0.08))),min(1,max(0,(max(c,min(1,max(0,(b-0.50)/0.33)))-0.95)/0.05))))'
# Explicit nested min, no Python callbacks or external dependencies in the saved control.
drive(launch,'location',2,'2.74+0.90*('+u+')',v)
# Rebind surface-following knee pads after the garment topology change; stale binds stretched across the torso.
for code,person,yy in [('AS','AlexSector_Rig',-.6),('BS','BruceSato_Rig',.6)]:
 r=bpy.data.objects[person];r['driving_pose']=0;r['mask_on']=False;r.location=(0,0,0);r.update_tag();bpy.context.view_layer.update()
 for ob in bpy.data.collections[code+'_Character'].all_objects:
  for mod in ob.modifiers:
   if mod.type=='SURFACE_DEFORM':
    mod.target=bpy.data.objects[code+'_ContinuousFlightSuit'];bpy.context.view_layer.objects.active=ob
    if mod.is_bound:bpy.ops.object.surfacedeform_bind(modifier=mod.name)
    bpy.ops.object.surfacedeform_bind(modifier=mod.name)
 r.location=(2,yy,1.37);r['driving_pose']=1;r['mask_on']=False;r.update_tag()
S.name='Rhino_V2_LowerHood_SlidingCabinet';S['asset']='Rhino V2';S['V2_user_revision']='Lower hood 2.35m; lower upper glazing 3.15..3.985m, panes splayed ~9deg in plan; independent rotating roof radar; rear cabinet travels aft 0.80m before single missile rises.'
S['estimated_kinematics']='Cabinet travel, rail geometry, radar speed and pane angles estimated from supplied images and explicit user corrections.'
S.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Rhino_V2.blend'),compress=True)
print('RHINO_V2_USER_CORRECTIONS_SAVED')
