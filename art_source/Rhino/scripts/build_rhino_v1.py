"""Rhino editable vehicle, from inspected supplied toy and Kenworth photos.
Run once through installed Blender MCP. Hidden mechanics/dimensions estimated.
"""
import bpy,math,json,datetime,re
from pathlib import Path
from mathutils import Vector,Matrix
from math import sin,cos,pi
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Rhino';S=bpy.context.scene
assert not (A/'Rhino_V1.blend').exists(),'A first build must not overwrite a reviewed iteration.'
bpy.ops.wm.save_as_mainfile(filepath=str(A/('Session_before_Rhino_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.blend')),copy=True,compress=True)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.shading.type='SOLID'
for ob in list(bpy.data.objects):bpy.data.objects.remove(ob,do_unlink=True)
for c in list(bpy.data.collections):bpy.data.collections.remove(c)
S.name='Rhino_V1_Assembly';S.unit_settings.system='METRIC';S.unit_settings.scale_length=1
S['asset']='Rhino V1';S['reference_review']='docs/art/Rhino_reference_review_v1.md';S['interpretation']='Dimensions, hidden mechanics, cabin finishes and human anatomy estimated from supplied references.'
def collection(n):
 c=bpy.data.collections.new(n);S.collection.children.link(c);return c
BODY=collection('Rhino_Truck');POD=collection('Rhino_RearVehicle');CAB=collection('Rhino_Interior');STUDIO=collection('Rhino_Studio');CURRENT=BODY
def material(n,c,metal=0,rough=.4):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
RED=material('Rhino_DeepBurgundy',(.205,.012,.038),.65,.26);CHROME=material('Rhino_Chrome',(.62,.69,.76),1,.19);ALU=material('Rhino_SatinAluminium',(.32,.39,.45),.86,.34);BLACK=material('Rhino_ChassisGraphite',(.014,.019,.024),.6,.42);RUBBER=material('Rhino_TireRubber',(.012,.014,.017),0,.76);TREAD=material('Rhino_TreadRubber',(.019,.021,.023),0,.82);DARK=material('Rhino_Recess',(.002,.004,.006),0,.6);ORANGE=material('Rhino_OrangeStripe',(.95,.15,.018),.25,.32);GOLD=material('Rhino_GoldStripe',(1,.58,.025),.35,.32);LEATHER=material('Rhino_CharcoalUpholstery',(.025,.031,.036),0,.78);DASH=material('Rhino_Dashboard',(.044,.053,.056),0,.65);AMBER=material('Rhino_AmberLamp',(1,.26,.008),.1,.2);LAMP=material('Rhino_HeadlightLens',(.72,.86,.94),.35,.15);GLASS=material('Rhino_TintedGlass',(.17,.31,.34),.05,.12);SCREEN=material('Rhino_GreenScreen',(.005,.14,.09),.2,.22)
for m,col,power in [(AMBER,(1,.20,.005,1),.8),(LAMP,(.65,.82,1,1),.55),(SCREEN,(.005,.3,.12,1),.4)]:
 p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Emission Color'].default_value=col;p.inputs['Emission Strength'].default_value=power
p=next(n for n in GLASS.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Transmission Weight'].default_value=1;p.inputs['IOR'].default_value=1.45
for m,scale,dist in [(RED,150,.0002),(RUBBER,135,.0005),(LEATHER,320,.0006)]:
 ns=m.node_tree.nodes;ls=m.node_tree.links;n=ns.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=scale;b=ns.new('ShaderNodeBump');b.inputs['Strength'].default_value=.16;b.inputs['Distance'].default_value=dist;ls.new(n.outputs['Fac'],b.inputs['Height']);ls.new(b.outputs['Normal'],next(n for n in ns if n.type=='BSDF_PRINCIPLED').inputs['Normal'])
def mesh(n,v,f,m,co=None,smooth=False,bevel=0):
 me=bpy.data.meshes.new(n+'_Editable');me.from_pydata(v,[],f);me.update();ob=bpy.data.objects.new(n,me);(co or CURRENT).objects.link(ob)
 if m:me.materials.append(m)
 for p in me.polygons:p.use_smooth=smooth
 if bevel:
  mod=ob.modifiers.new('ManufacturedEdge','BEVEL');mod.width=bevel;mod.segments=3;ob.modifiers.new('WeightedNormals','WEIGHTED_NORMAL')
 return ob
def empty(n,p=(0,0,0),co=None):
 ob=bpy.data.objects.new(n,None);(co or CURRENT).objects.link(ob);ob.location=p;ob.empty_display_type='PLAIN_AXES';ob.empty_display_size=.22;bpy.context.view_layer.update();return ob
def box(n,p,d,m,b=.02,co=None):
 x,y,z=p;a,c,e=(q/2 for q in d);return mesh(n,[(x+i*a,y+j*c,z+k*e) for i,j,k in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]],[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],m,co,bevel=b)
def tube(n,a,b,r,m,co=None,r2=None,N=32,caps=True):
 a,b=Vector(a),Vector(b);q=(b-a).to_track_quat('Z','Y');v=[]
 for center,rr in [(a,r),(b,r if r2 is None else r2)]:
  v.extend(tuple(center+q@Vector((rr*cos(i*2*pi/N),rr*sin(i*2*pi/N),0))) for i in range(N))
 f=[(i,(i+1)%N,N+(i+1)%N,N+i) for i in range(N)]
 if caps:f.extend([tuple(reversed(range(N))),tuple(range(N,2*N))])
 return mesh(n,v,f,m,co,True)
def path(n,pts,r,m,co=None):
 cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.resolution_u=1;cu.bevel_depth=r;cu.bevel_resolution=3;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for point,p in zip(sp.points,pts):point.co=(*p,1)
 ob=bpy.data.objects.new(n,cu);(co or CURRENT).objects.link(ob);cu.materials.append(m);return ob
def parent(ob,root):
 bpy.context.view_layer.update();ob.parent=root;ob.matrix_parent_inverse=root.matrix_world.inverted();return ob
def children_since(before,root):
 for ob in set(bpy.data.objects)-before:
  if ob!=root and ob.parent is None:parent(ob,root)
def drive(ob,prop,index,expression,variables):
 f=ob.driver_add(prop,index);d=f.driver;d.type='SCRIPTED'
 for name,owner,key in variables:
  v=d.variables.new();v.name=name;v.type='SINGLE_PROP';v.targets[0].id=owner;v.targets[0].data_path='["'+key+'"]'
 d.expression=re.sub(r'(?<![0-9A-Za-z_])\.(\d)',r'0.\1',expression);ob.update_tag()
def text(n,body,p,size,m,rotation,co=None):
 cu=bpy.data.curves.new(n,'FONT');cu.body=body;cu.size=size;cu.align_x='CENTER';cu.extrude=.0015;ob=bpy.data.objects.new(n,cu);(co or CURRENT).objects.link(ob);ob.location=p;ob.rotation_euler=rotation;cu.materials.append(m);return ob
ROOT=empty('Rhino_Control');ROOT['battle_mode']=0.;ROOT['rear_detach']=0.;ROOT['bullbar']=0.;ROOT['cannons']=0.;ROOT['rear_open']=0.;ROOT['launcher_up']=0.;ROOT['estimated_length_m']=9.0
for key in ['battle_mode','rear_detach','bullbar','cannons','rear_open','launcher_up']:ROOT.id_properties_ui(key).update(min=0,max=1,description='0 route / 1 deploye. battle_mode pilote la sequence complete.')
ROOT['wheel_partition']='10 identical persistent tires: truck 2 front + 2 middle outer; rear vehicle 2 middle inner + 4 rear.'
ROOT['reference']='Supplied Rhino toy + W900B photographs; hidden kinematics estimated.'
PODROOT=empty('Rhino_RearVehicle_Root',co=POD)
drive(PODROOT,'location',0,'-4.9*max(d,min(1,max(0,(b-.12)/.43)))',[('d',ROOT,'rear_detach'),('b',ROOT,'battle_mode')])
drive(PODROOT,'location',1,'-3.3*min(1,max(0,(max(d,min(1,max(0,(b-.12)/.43)))-.65)/.35))',[('d',ROOT,'rear_detach'),('b',ROOT,'battle_mode')])
# Main frame ends on its own central wheel pair, independent of rear module.
for y in [-.59,.59]:box('RH_TruckFrame_'+str(y),(.95,y,.94),(6.15,.14,.26),BLACK,.018)
for x in [-1.35,-.5,.6,1.8,2.8,3.8]:box('RH_FrameCrossmember_'+str(x),(x,0,.95),(.12,1.12,.13),BLACK,.01)
tube('RH_FrontAxle',(3.45,-1.12,.58),(3.45,1.12,.58),.095,BLACK)
for sg in [-1,1]:
 y=sg*1.16;tube('RH_TruckMiddleStub_'+str(sg),(-1.88,sg*1.04,.58),(-1.88,sg*1.27,.58),.09,ALU)
 path('RH_TruckAxleOutrigger_'+str(sg),[(-1.88,y,.58),(-1.25,y,.75),(-1.25,sg*.59,.94)],.075,BLACK)
 for z in [.7,.73,.76]:box('RH_LeafSpring_'+str((sg,z)),(3.45,sg*.58,z),(1.15,.11,.022),BLACK,.005)
CURRENT=POD;start=set(bpy.data.objects)
for y in [-.36,.36]:box('RH_PodFrame_'+str(y),(-2.8,y,.78),(2.7,.13,.22),BLACK,.018)
for x in [-1.88,-3.35]:tube('RH_PodAxle_'+str(x),(x,-.91,.58),(x,.91,.58),.09,BLACK)
box('RH_PodDeck',(-2.8,0,1.01),(2.78,1.25,.10),BLACK)
for x in [-1.65,-2,-2.35,-2.7,-3.05,-3.4,-3.75]:box('RH_PodCrossRib_'+str(x),(x,0,1.075),(.055,1.34,.08),ALU,.01)
# Low independent cockpit, facing rear: recessed to fit beneath the coupled deck silhouette.
box('RH_PodSeatBase',(-2.91,0,1.2),(.57,.55,.20),LEATHER,.07)
box('RH_PodSeatBack',(-2.64,0,1.43),(.14,.58,.56),LEATHER,.07)
box('RH_PodControlPanel',(-3.50,0,1.27),(.27,.70,.20),DASH,.04)
box('RH_PodScreen',(-3.63,0,1.32),(.012,.28,.10),SCREEN,.004)
tube('RH_PodJoystick',(-3.38,.28,1.25),(-3.40,.28,1.52),.025,BLACK)
for sg in [-1,1]:
 path('RH_PodSideGuard_'+str(sg),[(-3.9,sg*.63,1.14),(-3.7,sg*.63,1.38),(-3.05,sg*.63,1.40)],.035,BLACK)
 box('RH_PodRearLamp_'+str(sg),(-4.16,sg*.52,.96),(.04,.20,.10),RED,.015)
children_since(start,PODROOT)
# Tire and rim meshes; tread blocks joined into one editable object per tire.
wheel_manifest=[]
def wheel(n,x,y,r=.58,w=.29,owner=None):
 center=Vector((x,y,r));N=80;v=[];f=[]
 profile=[(-w/2,.31),(-w/2,.45),(-w*.43,r*.97),(-w*.32,r),(w*.32,r),(w*.43,r*.97),(w/2,.45),(w/2,.31)]
 for yy,rr in profile:
  v.extend((x+rr*cos(i*2*pi/N),y+yy,r+rr*sin(i*2*pi/N)) for i in range(N))
 for j in range(len(profile)):
  k=(j+1)%len(profile);f.extend((j*N+i,j*N+(i+1)%N,k*N+(i+1)%N,k*N+i) for i in range(N))
 tire=mesh(n+'_Tire',v,f,RUBBER,smooth=True);tire['wheel_owner']='rear_vehicle' if owner else 'truck';tire['wheel_role']=n;wheel_manifest.append({'name':tire.name,'owner':tire['wheel_owner'],'x':x,'y':y})
 objs=[tire];vv=[];ff=[]
 for row in range(4):
  for i in range(56):
   angle=2*pi*(i+(row%2)*.5)/56;rr=r+.004;yy=y+(row-1.5)*w*.20;offset=len(vv)
   for da,dy,dr in [(-.043,-w*.074,-.010),(-.043,-w*.074,.009),(-.043,w*.074,-.010),(-.043,w*.074,.009),(.043,-w*.074,-.010),(.043,-w*.074,.009),(.043,w*.074,-.010),(.043,w*.074,.009)]:vv.append((x+(rr+dr)*cos(angle+da),yy+dy,r+(rr+dr)*sin(angle+da)))
   ff.extend(tuple(offset+k for k in face) for face in [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)])
 objs.append(mesh(n+'_Tread',vv,ff,TREAD,bevel=.003))
 sg=1 if y>0 else -1;outside=y+sg*(w/2+.005)
 objs.append(tube(n+'_WheelRim',(x,y-w/2-.01,r),(x,y+w/2+.01,r),.318,CHROME))
 objs.append(tube(n+'_RimDish',(x,outside,r),(x,outside+sg*.022,r),.255,ALU))
 objs.append(tube(n+'_Hub',(x,outside,r),(x,outside+sg*.075,r),.112,CHROME))
 for i in range(10):
  a=i*2*pi/10;xx=x+.185*cos(a);zz=r+.185*sin(a);objs.append(tube(n+'_RimVent'+str(i),(xx,outside+sg*.024,zz),(xx,outside+sg*.027,zz),.034,DARK,N=16));xx=x+.143*cos(a);zz=r+.143*sin(a);objs.append(tube(n+'_Lug'+str(i),(xx,outside+sg*.025,zz),(xx,outside+sg*.043,zz),.014,CHROME,N=8))
 if owner:
  for ob in objs:parent(ob,owner)
CURRENT=BODY
for sg in [-1,1]:wheel('RH_Front_'+str(sg),3.45,sg*1.07,w=.34);wheel('RH_MiddleOuter_Truck_'+str(sg),-1.88,sg*1.16)
CURRENT=POD
for sg in [-1,1]:
 wheel('RH_MiddleInner_Pod_'+str(sg),-1.88,sg*.84,owner=PODROOT)
 for kind,yy in [('Inner',.84),('Outer',1.16)]:wheel('RH_Rear'+kind+'_Pod_'+str(sg),-3.35,sg*yy,owner=PODROOT)
# Fifth wheel with slot, carried by rear vehicle.
start=set(bpy.data.objects)
for sg in [-1,1]:
 a=[pi*.10+i*pi*.78/31 for i in range(32)];pts=[(-2.93+.49*cos(t),sg*.49*sin(t),1.15) for t in a];path('RH_FifthWheelHalf_'+str(sg),pts,.095,ALU)
box('RH_FifthWheelMount',(-2.93,0,1.08),(.72,.8,.12),BLACK,.03);children_since(start,PODROOT)
CURRENT=BODY
# Raised rounded wheel arches, two skins, no filled circles over tires.
for sg in [-1,1]:
 v=[];f=[];N=48
 for yy,rr in [(sg*.85,.66),(sg*1.31,.66),(sg*.85,.73),(sg*1.31,.73)]:
  v.extend((3.45+rr*cos(-.08+pi*1.16*i/(N-1)),yy,.58+rr*sin(-.08+pi*1.16*i/(N-1))) for i in range(N))
 for a,b in [(0,1),(1,3),(3,2),(2,0)]:f.extend((a*N+i,a*N+i+1,b*N+i+1,b*N+i) for i in range(N-1))
 mesh('RH_FrontFender_'+str(sg),v,f,RED,smooth=True,bevel=.014)
box('RH_Hood',(3.56,0,2.04),(1.98,1.55,1.46),RED,.11)
# Slightly sloped side hood lines and central twin stripes.
for y,m in [(-.105,ORANGE),(.035,GOLD)]:
 box('RH_HoodStripeTop_'+str(y),(3.56,y,2.774),(1.95,.07,.008),m,.002)
 box('RH_HoodStripeNose_'+str(y),(4.555,y,2.04),(.008,.07,1.37),m,.002)
for sg in [-1,1]:
 for j,z in enumerate([1.7,1.79]):box('RH_HoodSideStripe_'+str((sg,j)),(3.53,sg*.781,z),(1.93,.008,.047),GOLD if j else ORANGE,.002)
 for i in range(7):box('RH_HoodVent_'+str((sg,i)),(2.86+i*.075,sg*.786,2.23),(.025,.012,.26),DARK,.009)
 box('RH_HeadlightHousing_'+str(sg),(4.52,sg*.99,1.29),(.25,.45,.31),CHROME,.035)
 for i in [-1,1]:box('RH_Headlight_'+str((sg,i)),(4.654,sg*.99+i*.105,1.3),(.018,.18,.19),LAMP,.018)
# Grille and fixed bumper; bullbar is a separate sliding assembly.
box('RH_GrilleShadow',(4.60,0,1.98),(.10,1.49,1.60),DARK,.02)
for y in [-.82,.82]:box('RH_GrilleSide_'+str(y),(4.67,y,2.0),(.13,.12,1.83),CHROME,.035)
for z in [1.1,2.9]:box('RH_GrilleCross_'+str(z),(4.67,0,z),(.13,1.76,.11),CHROME,.03)
for i in range(28):box('RH_GrilleSlat_'+str(i),(4.675,0,1.19+i*.058),(.065,1.52,.019),CHROME,.003)
for y in [-.38,0,.38]:box('RH_GrilleStiffener_'+str(y),(4.64,y,2.0),(.045,.02,1.7),ALU,.002)
box('RH_FixedBumper',(4.66,0,.86),(.23,2.55,.38),CHROME,.055)
BULL=empty('RH_BullbarSlide');start=set(bpy.data.objects)
for sg in [-1,1]:
 path('RH_BullbarUpright_'+str(sg),[(4.89,sg*.94,.75),(4.94,sg*.94,2.92)],.055,CHROME)
 box('RH_BullbarPostCap_'+str(sg),(4.94,sg*.94,2.93),(.12,.12,.10),CHROME,.025)
path('RH_BullbarLower',[(4.89,-1.12,.87),(4.95,-.92,.67),(4.95,.92,.67),(4.89,1.12,.87)],.065,CHROME)
path('RH_BullbarCross',[(4.95,-.94,1.26),(4.95,.94,1.26)],.042,CHROME)
children_since(start,BULL)
drive(BULL,'location',0,'.80*max(v,min(1,max(0,b/.25)))',[('v',ROOT,'bullbar'),('b',ROOT,'battle_mode')])
for sg in [-1,1]:
 tube('RH_BullbarGuide_'+str(sg),(4.6,sg*.65,.85),(5.52,sg*.65,.85),.045,ALU)
 # Air cleaners and chromed pipework, distinct from exhaust/cannon tubes.
 tube('RH_AirCleaner_'+str(sg),(3.09,sg*1.0,1.87),(3.09,sg*1.0,2.62),.17,CHROME)
 for z in [1.92,2.29,2.57]:tube('RH_AirCleanerBand_'+str((sg,z)),(3.09,sg*1.0,z-.025),(3.09,sg*1.0,z+.025),.183,ALU)
 path('RH_AirIntake_'+str(sg),[(3.09,sg*1.0,2.37),(2.78,sg*1.0,2.37),(2.70,sg*.77,2.37)],.065,CHROME)
# Cab is a shell built around actual window openings, not a solid cube with white rectangles.
box('RH_CabFloor',(1.77,0,1.23),(1.86,2.26,.14),BLACK,.035,co=CAB)
box('RH_CabLowerFront',(2.72,0,1.81),(.11,2.23,1.08),RED,.035)
box('RH_CabRoof',(1.79,0,3.20),(1.95,2.34,.12),RED,.04)
for sg in [-1,1]:
 y=sg*1.14
 box('RH_DoorLower_'+str(sg),(1.87,y,1.90),(1.66,.09,1.04),RED,.04)
 box('RH_DoorAFrame_'+str(sg),(2.68,y,2.77),(.09,.10,.79),RED,.02)
 box('RH_DoorBFrame_'+str(sg),(1.04,y,2.76),(.13,.10,.82),RED,.02)
 box('RH_DoorWindowRail_'+str(sg),(1.87,y,2.37),(1.7,.10,.06),CHROME,.014)
 box('RH_DoorGlass_'+str(sg),(1.86,y,2.77),(1.49,.014,.66),GLASS,.01)
 for j,z in enumerate([1.52,1.61]):box('RH_CabSideStripe_'+str((sg,j)),(1.83,sg*1.192,z),(1.67,.008,.045),GOLD if j else ORANGE,.002)
 box('RH_DoorHandleRecess_'+str(sg),(1.29,sg*1.194,2.27),(.18,.018,.075),DARK,.018)
 box('RH_DoorHandle_'+str(sg),(1.29,sg*1.213,2.28),(.15,.022,.025),CHROME,.008)
 box('RH_StepBox_'+str(sg),(1.77,sg*1.02,.91),(1.66,.59,.59),ALU,.045)
 for j in range(10):box('RH_StepGrip_'+str((sg,j)),(1.1+j*.145,sg*1.28,1.225),(.055,.35,.015),DARK,.004)
 box('RH_LowerStep_'+str(sg),(2.05,sg*1.34,.71),(1.06,.25,.08),CHROME,.015)
 for z in [2.55,3.08]:path('RH_MirrorArm_'+str((sg,z)),[(2.48,y,z),(2.6,sg*1.55,z),(2.21,sg*1.55,z)],.016,CHROME)
 box('RH_MirrorHousing_'+str(sg),(2.21,sg*1.55,2.82),(.15,.09,.65),CHROME,.045)
 box('RH_MirrorGlass_'+str(sg),(2.12,sg*1.55,2.82),(.008,.067,.57),CHROME,.02)
 path('RH_DoorSeal_'+str(sg),[(1.0,sg*1.195,1.4),(1.0,sg*1.195,3.12),(2.66,sg*1.195,3.12),(2.66,sg*1.195,1.4),(1,sg*1.195,1.4)],.009,DARK)
for sg in [-1,1]:
 box('RH_Windshield_'+str(sg),(2.73,sg*.568,2.78),(.018,1.02,.67),GLASS,.01)
 box('RH_WindshieldSeal_'+str(sg),(2.75,sg*1.10,2.78),(.045,.035,.77),DARK,.008)
 path('RH_Wiper_'+str(sg),[(2.77,sg*.18,2.43),(2.78,sg*.71,2.64),(2.78,sg*.82,2.78)],.012,BLACK)
box('RH_WindshieldCenter',(2.76,0,2.78),(.07,.045,.79),CHROME,.01)
box('RH_CabVisor',(2.77,0,3.19),(.38,2.45,.065),CHROME,.025)
for i in range(5):
 y=(i-2)*.36;box('RH_RoofMarkerBase_'+str(i),(2.38,y,3.30),(.22,.12,.05),CHROME,.012);box('RH_RoofMarker_'+str(i),(2.43,y,3.34),(.13,.09,.065),AMBER,.022)
for sg in [-1,1]:
 path('RH_RoofHorn_'+str(sg),[(2.05,sg*.88,3.32),(2.52,sg*.88,3.32)],.045,CHROME);tube('RH_HornBell_'+str(sg),(2.48,sg*.88,3.32),(2.62,sg*.88,3.32),.045,CHROME,r2=.095)
# High rear cockpit: polygonal side profile, with sloping forward upper glazing.
profile=[(-.68,1.27),(.97,1.27),(.97,3.18),(.25,4.30),(-.68,4.30)]
for sg in [-1,1]:
 yy=sg*1.13;v=[(x,yy+off,z) for off in [-.045,.045] for x,z in profile];N=len(profile);f=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,N+(i+1)%N,N+i) for i in range(N)];mesh('RH_UpperCockpitSide_'+str(sg),v,f,RED,bevel=.035)
 path('RH_TowerSeam_'+str(sg),[(-.59,sg*1.18,1.4),(-.59,sg*1.18,4.18),(.19,sg*1.18,4.18)],.009,DARK)
 for j,m in enumerate([ORANGE,GOLD]):
  path('RH_TowerStripe_'+str((sg,j)),[(.84,sg*(1.184+j*.001),1.49+j*.08),(.1,sg*(1.184+j*.001),1.49+j*.08),(-.51+j*.08,sg*(1.184+j*.001),3.87)],.025,m)
 box('RH_FuelTankBracket_'+str(sg),(.10,sg*.79,.90),(1.40,.16,.20),BLACK,.01)
 tube('RH_FuelTank_'+str(sg),(-.57,sg*1.03,.95),(.72,sg*1.03,.95),.265,CHROME)
 for x in [-.42,.50]:tube('RH_FuelTankBand_'+str((sg,x)),(x-.035,sg*1.03,.95),(x+.035,sg*1.03,.95),.277,ALU)
 tube('RH_TankCap_'+str(sg),(.4,sg*1.03,1.19),(.4,sg*1.03,1.25),.055,CHROME)
box('RH_UpperCockpitRoof',(-.22,0,4.32),(1.05,2.34,.10),RED,.035)
for sg in [-1,1]:
 v=[(.98,sg*.06,3.23),(.98,sg*1.06,3.23),(.29,sg*1.06,4.27),(.29,sg*.06,4.27)]
 ob=mesh('RH_UpperCockpitGlass_'+str(sg),v,[(0,1,2,3)],GLASS);mod=ob.modifiers.new('GlazingThickness','SOLIDIFY');mod.thickness=.012
for y in [-1.12,0,1.12]:path('RH_UpperWindowFrame_'+str(y),[(.99,y,3.19),(.27,y,4.32)],.035,RED)
path('RH_UpperWindowBottom',[(.99,-1.14,3.19),(.99,1.14,3.19)],.04,RED)
SIGN=empty('RH_RoofScannerPivot',(.12,0,4.37));start=set(bpy.data.objects)
box('RH_RoofScanner',(.11,0,4.49),(.22,1.46,.24),RED,.035);box('RH_RoofScannerLens',(.235,0,4.5),(.018,1.24,.12),AMBER,.014);children_since(start,SIGN)
# Rear ramp opens before the launcher is permitted to rise.
RAMP=empty('RH_RearCockpitHatchPivot',(-.72,0,1.29));start=set(bpy.data.objects)
box('RH_RearCockpitHatch',(-.72,0,2.79),(.10,2.15,2.94),RED,.025)
for z in [1.45,4.12]:box('RH_RearHatchFrame_'+str(z),(-.78,0,z),(.06,2.03,.065),ALU,.01)
for i in range(15):box('RH_RampGrip_'+str(i),(-.65,0,1.40+i*.19),(.03,1.65,.035),BLACK,.004)
for y in [-.75,.75]:box('RH_HatchLatch_'+str(y),(-.79,y,2.30),(.06,.15,.22),ALU,.018)
children_since(start,RAMP)
drive(RAMP,'rotation_euler',1,'-1.99*max(v,min(1,max(0,(b-.42)/.36)))',[('v',ROOT,'rear_open'),('b',ROOT,'battle_mode')])
for sg in [-1,1]:tube('RH_HatchHinge_'+str(sg),(-.72,sg*.75,1.29),(-.72,sg*1.03,1.29),.065,CHROME)
CURRENT=CAB
box('RH_UpperCockpitFloor',(-.08,0,2.48),(1.08,2.14,.10),BLACK,.025)
box('RH_UpperCommandSeat',(-.30,.65,2.68),(.48,.53,.23),LEATHER,.055)
box('RH_UpperCommandSeatBack',(-.55,.65,3.0),(.12,.53,.64),LEATHER,.05)
box('RH_UpperCommandConsole',(.59,.64,2.85),(.36,.60,.34),DASH,.04)
box('RH_UpperCommandScreen',(.40,.64,2.98),(.012,.4,.14),SCREEN,.005)
CURRENT=BODY
LAUNCH=empty('RH_MissileLauncherLift',(.02,-.30,2.72));start=set(bpy.data.objects)
box('RH_LauncherPedestal',(.01,-.32,2.72),(.38,.48,.30),BLACK,.04)
tube('RH_LauncherElevator',(.01,-.32,2.62),(.01,-.32,3.22),.10,CHROME)
box('RH_LauncherCradle',(-.10,-.32,3.22),(1.10,.88,.13),ALU,.035)
for j in [-1,1]:
 y=-.32+j*.23
 tube('RH_LaunchTube_'+str(j),(-.55,y,3.44),(.58,y,3.44),.17,BLACK)
 tube('RH_MissileBody_'+str(j),(-.53,y,3.44),(.54,y,3.44),.10,ALU)
 tube('RH_MissileNose_'+str(j),(-.53,y,3.44),(-.82,y,3.44),.10,ORANGE,r2=.006)
 for sg in [-1,1]:box('RH_MissileFin_'+str((j,sg)),(.44,y+sg*.10,3.44),(.22,.13,.025),RED,.005)
children_since(start,LAUNCH)
drive(LAUNCH,'location',2,'2.72+.70*min(max(v,min(1,max(0,(b-.80)/.20))),min(1,max(0,(max(h,min(1,max(0,(b-.42)/.36)))-.92)/.08)))',[('v',ROOT,'launcher_up'),('h',ROOT,'rear_open'),('b',ROOT,'battle_mode')])
# Vertical stacks become the actual same forward pointing cannon meshes.
for sg in [-1,1]:
 pivot=empty('RH_ExhaustCannonPivot_'+str(sg),(.94,sg*1.29,1.47));start=set(bpy.data.objects)
 tube('RH_ExhaustCannonTube_'+str(sg),(.94,sg*1.29,1.47),(.94,sg*1.29,4.13),.085,CHROME,caps=False)
 tube('RH_CannonBore_'+str(sg),(.94,sg*1.29,3.95),(.94,sg*1.29,4.14),.064,DARK)
 tube('RH_ExhaustHeatShield_'+str(sg),(.94,sg*1.29,1.78),(.94,sg*1.29,3.51),.118,ALU)
 for row in range(20):
  z=1.85+row*.080
  for col in range(7):
   a=2*pi*col/7;tube('RH_ShieldPerforation_'+str((sg,row,col)),(.94+.119*cos(a),sg*1.29+.119*sin(a),z),(.94+.121*cos(a),sg*1.29+.121*sin(a),z),.017,DARK,N=8)
 for z in [1.70,3.55]:tube('RH_StackBand_'+str((sg,z)),(.94,sg*1.29,z-.035),(.94,sg*1.29,z+.035),.13,CHROME)
 children_since(start,pivot)
 drive(pivot,'rotation_euler',1,'1.57079632679*max(v,min(1,max(0,(b-.05)/.36)))',[('v',ROOT,'cannons'),('b',ROOT,'battle_mode')])
 tube('RH_StackFixedHinge_'+str(sg),(.94,sg*1.20,1.47),(.94,sg*1.38,1.47),.15,BLACK)
# Cabin details adapted to seated rig target space, editable and physically enclosed.
CURRENT=CAB
box('RH_Dashboard',(2.49,0,2.23),(.40,2.08,.30),DASH,.045)
for yy in [-.60,.60]:
 box('RH_SeatCushion_'+str(yy),(1.51,yy,1.87),(.57,.52,.13),LEATHER,.06)
 box('RH_SeatBack_'+str(yy),(1.24,yy,2.15),(.15,.56,.67),LEATHER,.06)
 box('RH_SeatHeadrest_'+str(yy),(1.20,yy,2.61),(.14,.35,.25),LEATHER,.05)
 tube('RH_SeatPedestal_'+str(yy),(1.48,yy,1.3),(1.48,yy,1.8),.11,BLACK)
 for sg in [-1,1]:path('RH_SeatStitch_'+str((yy,sg)),[(1.72,yy+sg*.21,1.95),(1.31,yy+sg*.21,1.95),(1.30,yy+sg*.21,2.42)],.004,ALU)
 for i in range(4):
  y=yy+(i-1.5)*.13;tube('RH_GaugeRim_'+str((yy,i)),(2.27,y,2.29),(2.25,y,2.29),.052,CHROME);tube('RH_GaugeFace_'+str((yy,i)),(2.247,y,2.29),(2.245,y,2.29),.044,DARK);path('RH_GaugeNeedle_'+str((yy,i)),[(2.242,y,2.29),(2.242,y+.02,2.31)],.0025,LAMP)
box('RH_CenterRadio',(2.26,0,2.24),(.018,.32,.12),BLACK,.01)
for i in range(4):box('RH_RadioButton_'+str(i),(2.245,(i-1.5)*.058,2.23),(.01,.03,.025),ALU,.003)
path('RH_GearLever',[(1.85,0,1.32),(1.9,0,1.89),(1.79,0,2.02)],.018,BLACK)
tube('RH_GearKnob',(1.79,0,1.98),(1.79,0,2.06),.035,ALU)
CURRENT=BODY
# Branding stays editable typography, not a false claim of an official logo reconstruction.
text('RH_GrilleBadge','RHINO',(4.754,0,2.62),.115,RED,(pi/2,0,pi/2))
for sg in [-1,1]:text('RH_SideBadge_'+str(sg),'M.A.S.K.',(.04,sg*1.193,4.02),.16,GOLD,(pi/2,0,0 if sg<0 else pi))
# Scene presentation and timeline.
CURRENT=STUDIO
floor=box('Review_Floor',(0,0,-.075),(200,200,.10),material('Rhino_StudioFloor',(.055,.072,.09),.05,.48),.005)
world=bpy.data.worlds.new('Rhino_StudioWorld');S.world=world;world.use_nodes=True;bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.17,.21,.27,1);bg.inputs[1].default_value=.45
for n,p,power,size in [('Key',(7,6,10),2300,5),('Fill',(3,-7,6),1800,4),('Rim',(-6,4,8),2600,4)]:
 ld=bpy.data.lights.new('RH_Studio'+n,'AREA');ld.energy=power;ld.shape='DISK';ld.size=size;ob=bpy.data.objects.new(ld.name,ld);STUDIO.objects.link(ob);ob.location=p;ob.rotation_euler=(Vector((.3,0,1.7))-ob.location).to_track_quat('-Z','Y').to_euler()
cd=bpy.data.cameras.new('Rhino_ReviewCamera');cam=bpy.data.objects.new('Rhino_ReviewCamera',cd);STUDIO.objects.link(cam);cam.location=(13,12,8);cam.rotation_euler=(Vector((.25,0,1.9))-cam.location).to_track_quat('-Z','Y').to_euler();cd.lens=52;S.camera=cam
S.render.engine='CYCLES';S.cycles.samples=24;S.cycles.use_denoising=True
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.get_devices();S.cycles.device='GPU'
except Exception:S.cycles.device='CPU'
S.render.resolution_x=1100;S.render.resolution_y=800;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';S.view_settings.view_transform='AgX'
S.frame_start=1;S.frame_end=241;S.render.fps=30
for f,value in [(1,0.),(31,0.),(151,1.),(181,1.),(241,0.)]:ROOT['battle_mode']=value;ROOT.keyframe_insert(data_path='["battle_mode"]',frame=f)
if ROOT.animation_data and ROOT.animation_data.action:
 try:
  for fc in ROOT.animation_data.action.fcurves:
   for kp in fc.keyframe_points:kp.interpolation='LINEAR'
 except Exception:pass
for name,f in [('ROUTE',1),('DEPLOIEMENT',31),('TRANSFORME',151),('RETOUR',181),('ROUTE_RETOUR',241)]:S.timeline_markers.new(name,frame=f)
S.frame_set(1);bpy.context.view_layer.update()
for ob in BODY.objects:
 if ob!=ROOT and ob.parent is None:parent(ob,ROOT)
for ob in CAB.objects:
 if ob.parent is None:parent(ob,ROOT)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.shading.type='MATERIAL';area.spaces.active.overlay.show_overlays=False;rv=area.spaces.active.region_3d;rv.view_location=(.2,0,1.8);rv.view_distance=14;rv.view_rotation=cam.rotation_euler.to_quaternion()
(A/'wheel_partition_v1.json').write_text(json.dumps(wheel_manifest,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Rhino_V1.blend'),compress=True)
print('RHINO_V1_VEHICLE_SAVED',len(S.objects),'persistent tires',len(wheel_manifest))
