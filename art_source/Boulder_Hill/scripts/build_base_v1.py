"""Boulder Hill editable environment, from inspected toy views and user video 1-13s.
Reference forms retained. Hidden mechanisms, enlarged hangar and routes interpreted.
Run through installed Blender MCP, starting from prepared measured vehicle scene.
"""
import bpy,bmesh,ast,math,json,random,re
from pathlib import Path
from mathutils import Vector,Matrix
from math import sin,cos,pi,sqrt,exp
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Boulder_Hill';S=bpy.context.scene
assert Path(bpy.data.filepath).name=='BoulderHill_prepared_v1.blend'
assert not (A/'BoulderHill_V1_Assembly.blend').exists()
tree=ast.parse((P/'art_source/Rhino/scripts/build_rhino_v1.py').read_text(encoding='utf-8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'<geometry_helpers>','exec'))
def parent(ob,root):ob.parent=root;ob.matrix_parent_inverse=root.matrix_world.inverted();return ob
def children_since(before,root):
 for ob in set(bpy.data.objects)-before:
  if ob!=root and ob.parent is None:parent(ob,root)
GROUP='static';MODULE='structure';original_mesh=mesh;original_path=path
def mesh(n,v,f,m,co=None,smooth=False,bevel=0):
 ob=original_mesh(n,v,f,m,co,smooth,bevel);ob['BH_group']=GROUP;ob['BH_module']=MODULE;return ob
def path(n,pts,r,m,co=None):
 ob=original_path(n,pts,r,m,co);ob['BH_group']=GROUP;ob['BH_module']=MODULE;return ob
GROUND=collection('BH_Ground');SHOP=collection('BH_Shop');GARAGE=collection('BH_QuarterGarage');PUMPS=collection('BH_Pumps');SIGN=collection('BH_Sign');ROCK=collection('BH_Rock');TURRET=collection('BH_Turret');HANGAR=collection('BH_Hangar');ROUTES=collection('BH_Demo_Routes');STUDIO=collection('BH_Studio');CURRENT=GROUND
BLUE=material('BH_WeatheredAzure',(.008,.20,.47),.38,.42);CREAM=material('BH_PumpIvory',(.68,.64,.47),.18,.52);WHITE=material('BH_StationPaint',(.58,.61,.58),.10,.56);STEEL=material('BH_ArmorSteel',(.23,.29,.30),.75,.42);EDGE=material('BH_ArmorEdges',(.39,.45,.45),.70,.33);BLACK=material('BH_Gunmetal',(.018,.026,.031),.72,.39);DARK=material('BH_Recess',(.003,.007,.009),0,.68);CHROME=material('BH_PolishedFittings',(.54,.61,.63),.95,.21);RUBBER=material('BH_HoseRubber',(.009,.013,.014),0,.78);ASPHALT=material('BH_Asphalt',(.044,.054,.059),0,.94);CONCRETE=material('BH_Concrete',(.25,.28,.28),0,.9);SAND=material('BH_DesertSand',(.35,.22,.115),0,.98);YELLOW=material('BH_FadedSafetyYellow',(.69,.43,.025),.1,.59);RED=material('BH_DecalRed',(.42,.014,.008),0,.55);STONE=material('BH_Sandstone',(.31,.105,.037),0,.94);GLASS=material('BH_StationGlass',(.65,.77,.79),.02,.085);SCREEN=material('BH_ControlScreen',(.005,.09,.075),.1,.25);SEAT=material('BH_SeatVinyl',(.025,.031,.034),0,.7)
p=next(n for n in GLASS.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Transmission Weight'].default_value=1;p.inputs['IOR'].default_value=1.45
p=next(n for n in SCREEN.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Emission Color'].default_value=(.005,.2,.10,1);p.inputs['Emission Strength'].default_value=.7
for mat,scale,distance,strength in [(ASPHALT,14,.025,.30),(CONCRETE,8,.012,.2),(SAND,2.6,.06,.3),(STEEL,90,.0009,.13),(BLUE,130,.0006,.12),(STONE,2.0,.095,.4)]:
 ns=mat.node_tree.nodes;ls=mat.node_tree.links;n=ns.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=scale;b=ns.new('ShaderNodeBump');b.inputs['Distance'].default_value=distance;b.inputs['Strength'].default_value=strength;ls.new(n.outputs['Fac'],b.inputs['Height']);ls.new(b.outputs['Normal'],next(n for n in ns if n.type=='BSDF_PRINCIPLED').inputs['Normal'])
ns=STONE.node_tree.nodes;ls=STONE.node_tree.links;tex=ns.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=.63;tex.inputs['Detail'].default_value=4;ramp=ns.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.12,.041,.013,1);ramp.color_ramp.elements[1].color=(.49,.25,.10,1);ls.new(tex.outputs['Fac'],ramp.inputs[0]);ls.new(ramp.outputs['Color'],next(n for n in ns if n.type=='BSDF_PRINCIPLED').inputs['Base Color'])
ROOT=empty('BoulderHill_Control');ROOT['battle_mode']=0.
for key in ['pumps','sign_open','sign_guns','store_armor','garage_deploy','gate_open','boulder_fall','turret_lift','turret_extension','thunderhawk_exit','rhino_exit']:
 ROOT[key]=0.;ROOT.id_properties_ui(key).update(min=0,max=1,description='0 normal / 1 deploye ; commande native editable')
ROOT['turret_yaw']=0.;ROOT.id_properties_ui('turret_yaw').update(min=-180,max=180,description='Azimut du canon sommital en degres')
ROOT['capacity_bays']=4;ROOT['layout_note']='Enlarged interpreted rear hangar: four 10.8 x 4.5m bays, 6m row spacing, broad manoeuvring aisle. Dimensions estimated, not official.'
def progress(key,a,b):return f'max(v,min(1,max(0,(b-{a})/{b-a})))',[('v',ROOT,key),('b',ROOT,'battle_mode')]
def add_driver(ob,prop,index,expr,variables):drive(ob,prop,index,expr,variables)
def slab(n,outline,top,thickness,mat):
 N=len(outline);v=[(x,y,z) for z in [top-thickness,top] for x,y in outline];f=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,N+(i+1)%N,N+i) for i in range(N)];return mesh(n,v,f,mat,bevel=.03)
# Forecourt L footprint and a real diagonal exit lane, not a decorative blocked aperture.
GROUP='floor';MODULE='ground'
slab('BH_StationSlab',[(-13.5,-21.5),(1.0,-21.5),(1,-13),(13.7,-13),(13.7,38.5),(-13.5,38.5)],0,.30,ASPHALT)
slab('BH_ExitApron',[(5.5,-6.0),(12.0,-6.0),(27,-21),(20,-28),(3.0,-11.0)],.005,.20,CONCRETE)
box('BH_DesertGround',(4,5,-.48),(250,250,.30),SAND,.01)
for xy in [(-10,-19),(-2,-19),(4,-9)]:
 tube('BH_DrainCover_'+str(xy),(xy[0],xy[1],.005),(xy[0],xy[1],.025),.21,EDGE)
 for j in range(5):box('BH_DrainSlot_'+str((xy,j)),(xy[0]+(j-2)*.055,xy[1],.029),(.020,.30,.006),DARK,.003)
# Shop volume: two-sided moving facade; protective sheets telescope behind its opaque header.
CURRENT=SHOP;GROUP='shop_static';MODULE='shop';start=set(bpy.data.objects)
box('BH_ShopFloor',(-5,-5.5,.10),(10.0,11,.20),CONCRETE,.04)
for x in [-9.92,-.08]:box('BH_ShopSideWall_'+str(x),(x,-5.45,2.95),(.16,11.1,5.8),WHITE,.025)
box('BH_ShopBackWall',(-5,.0,2.9),(10,.16,5.8),WHITE,.025)
box('BH_ShopCeiling',(-5,-5.5,5.84),(10.12,11.10,.18),WHITE,.035)
box('BH_AzureRoof',(-5,-5.5,6.12),(10.35,11.35,.48),BLUE,.055)
for i in range(29):box('BH_RoofFasciaRib_'+str(i),(-10.05+i*.365,-11.18,6.12),(.04,.08,.43),BLUE,.006)
for y in [-10.7,-.3]:box('BH_RoofGutter_'+str(y),(-5,y,6.37),(9.9,.10,.07),EDGE,.015)
# Octagonal rooftop marking, editable paint geometry inspired by the supplied toy decal.
pad=[(-5+2.28*cos(pi/8+i*pi/4),-5.5+2.28*sin(pi/8+i*pi/4),6.368) for i in range(8)]
mesh('BH_RoofOctagonalMark',pad,[tuple(range(8))],YELLOW)
path('BH_RoofOctagonRim',pad+[pad[0]],.032,DARK)
for radius in [1.10,1.38]:path('BH_RoofLandingCircle_'+str(radius),[(-5+radius*cos(i*2*pi/80),-5.5+radius*sin(i*2*pi/80),6.39) for i in range(81)],.045,WHITE)
for i in range(8):
 a=i*pi/4;path('BH_RoofRadialMark_'+str(i),[(-5+1.4*cos(a),-5.5+1.4*sin(a),6.39),(-5+2.1*cos(a),-5.5+2.1*sin(a),6.39)],.045,DARK)
text('BH_RoofH','H',(-5,-6.1,6.4),1.4,BLUE,(0,0,0))
# Visible rear shop furnishings remain beyond the facade sweep.
box('BH_ServiceCounter',(-5,-6.3,.78),(5.7,.85,1.30),WHITE,.045)
box('BH_Countertop',(-5,-6.3,1.46),(5.85,.95,.10),EDGE,.025)
for i in range(4):
 x=-8+i*1.8;box('BH_ShopShelfFrame_'+str(i),(x,-.42,1.7),(1.55,.60,3.1),EDGE,.03)
 for z in [.4,1.15,1.9,2.65]:
  box('BH_ShopShelf_'+str((i,z)),(x,-.52,z),(1.5,.68,.055),WHITE,.01)
  for j in range(5):box('BH_SparePartsBox_'+str((i,z,j)),(x+(j-2)*.25,-.60,z+.20),(.20,.27,.34),CREAM if j%2 else BLUE,.008)
for x in [-9.82,-.18]:box('BH_StoreJamb_'+str(x),(x,-11.02,2.95),(.16,.22,5.72),WHITE,.02)
children_since(start,ROOT)
facade=empty('BH_StorefrontPivot',(-5,-11,2.95));parent(facade,ROOT);GROUP='store_armor';start=set(bpy.data.objects)
for x in [-9.65,-6.6,-3.4,-.35]:box('BH_StorefrontMullion_'+str(x),(x,-11,2.87),(.13,.19,5.35),WHITE,.018)
for z in [.25,4.68,5.58]:box('BH_StorefrontRail_'+str(z),(-5,-11,z),(9.45,.22,.14),WHITE,.018)
box('BH_StorefrontHeader',(-5,-11.0,5.15),(9.45,.20,.80),WHITE,.02)
for x,w in [(-8.15,2.85),(-5,3.0),(-1.85,2.8)]:box('BH_StoreGlass_'+str(x),(x,-11.065,2.44),(w,.018,4.1),GLASS,.009)
text('BH_ChampionPlaque','CHAMPION',(-8.3,-11.095,4.14),.27,DARK,(pi/2,0,0))
box('BH_ChampionUnderline',(-8.3,-11.104,4.02),(1.55,.008,.055),RED,.002)
path('BH_StoreDoorHandle',[(-1.15,-11.2,1.9),(-1.15,-11.2,2.65)],.030,CHROME)
children_since(start,facade)
for j in range(5):
 z=.78+j*.97;panel=empty('BH_ArmorSheetCarrier_'+str(j));parent(panel,facade);before=set(bpy.data.objects)
 box('BH_ArmorSheet_'+str(j),(-5,-10.88,z),(9.35,.065,1.0),STEEL,.025)
 for x in [-8.1,-5,-1.9]:
  box('BH_ArmorPanelRib_'+str((j,x)),(x,-10.82,z),(.085,.08,.92),EDGE,.012)
  for k in [-1,1]:tube('BH_ArmorRivet_'+str((j,x,k)),(x,-10.83,z+k*.35),(x,-10.79,z+k*.35),.025,CHROME,N=12)
 children_since(before,panel)
 expression,variables=progress('store_armor',.05,.40);add_driver(panel,'location',2,f'{5.10-z}*(1-({expression}))',variables)
before=set(bpy.data.objects);text('BH_ArmorMaskWordmark','M.A.S.K.',(-5,-10.73,5.31),.48,YELLOW,(-pi/2,0,0));children_since(before,facade)
expression,variables=progress('store_armor',.05,.40)
add_driver(facade,'rotation_euler',0,'2.60*('+expression+')',variables);add_driver(facade,'location',1,'-11-1.50*('+expression+')',variables);add_driver(facade,'location',2,'2.95+0.40*('+expression+')',variables)
# Two flared ivory pumps; the same blue columns pivot into barrels.
CURRENT=PUMPS;MODULE='pumps';GROUP='pump_static';start=set(bpy.data.objects)
box('BH_PumpIsland',(-5.3,-18.8,.12),(9.3,2.5,.24),CONCRETE,.22)
for x in [-8.5,-2.1]:
 for sg in [-1,1]:box('BH_IslandReflector_'+str((x,sg)),(x,-18.8+sg*1.20,.16),(.23,.05,.10),YELLOW,.01)
children_since(start,ROOT)
for idx,x in enumerate([-8.5,-2.1],1):
 GROUP='pump_static';pump=empty('BH_Pump_'+str(idx),(x,-18.8,0));parent(pump,ROOT);before=set(bpy.data.objects)
 box('BH_PumpFoot_'+str(idx),(x,-18.8,.28),(1.45,1.1,.23),CREAM,.12)
 for sg in [-1,1]:
  v=[]
  for z,hw,hd in [(.35,.70,.45),(1.65,.49,.33)]:v.extend([(x+sg*.40-hw*.28,-18.8-hd,z),(x+sg*.40+hw*.28,-18.8-hd,z),(x+sg*.40+hw*.28,-18.8+hd,z),(x+sg*.40-hw*.28,-18.8+hd,z)])
  mesh('BH_PumpIvoryFlank_'+str((idx,sg)),v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],CREAM,bevel=.035)
 box('BH_PumpMeter_'+str(idx),(x,-18.8,2.00),(1.26,.64,.51),BLUE,.055)
 box('BH_PumpDisplay_'+str(idx),(x,-19.135,2.04),(1.10,.015,.31),CREAM,.01)
 text('BH_PumpDigits_'+str(idx),'8.89  3.79',(x,-19.15,2.01),.16,DARK,(pi/2,0,0))
 text('BH_PumpPremium_'+str(idx),'PREMIUM',(x,-19.151,2.15),.10,RED,(pi/2,0,0))
 path('BH_FuelHose_'+str(idx),[(x+.63,-18.7,1.65),(x+1.0,-18.6,1.45),(x+1.05,-18.9,.40),(x+.95,-19.1,.30),(x+.70,-19.0,1.2)],.032,RUBBER)
 box('BH_FuelNozzle_'+str(idx),(x+.70,-19.0,1.35),(.14,.15,.37),BLACK,.025)
 children_since(before,pump)
 GROUP='pump_gun_'+str(idx);pivot=empty('BH_PumpCannonPivot_'+str(idx),(x,-19.13,1.99));parent(pivot,pump);before=set(bpy.data.objects)
 tube('BH_PumpBlueBarrel_'+str(idx),(x,-19.15,1.95),(x,-19.15,.38),.105,BLUE,r2=.075,N=32,caps=False)
 for zz in [.45,.80,1.55,1.9]:tube('BH_PumpBarrelBand_'+str((idx,zz)),(x,-19.15,zz-.035),(x,-19.15,zz+.035),.12,EDGE,N=24)
 tube('BH_PumpCannonBore_'+str(idx),(x,-19.15,.47),(x,-19.15,.375),.053,DARK,N=24)
 for sg in [-1,1]:path('BH_PumpBlueFlute_'+str((idx,sg)),[(x+sg*.13,-19.15,1.90),(x+sg*.10,-19.15,.45)],.024,BLUE)
 children_since(before,pivot);expression,variables=progress('pumps',.43,.65);add_driver(pivot,'rotation_euler',0,'-1.36*('+expression+')',variables)
# Tall GAS sign: hinged face swings down, two cannons extend only after clearance.
CURRENT=SIGN;MODULE='sign';GROUP='sign_static';before=set(bpy.data.objects);sx,sy=-11.7,1.7
box('BH_SignFoundation',(sx,sy,.18),(1.4,1.4,.36),CONCRETE,.1);tube('BH_SignPole',(sx,sy,.3),(sx,sy,10.20),.20,BLACK)
for z in [1,2.5,4,5.5,7,8.5]:tube('BH_SignPoleBand_'+str(z),(sx,sy,z-.035),(sx,sy,z+.035),.225,EDGE)
box('BH_SignHousing',(sx,sy+.18,11.42),(3.14,.70,2.40),BLUE,.065)
box('BH_SignInnerBack',(sx,sy-.185,11.42),(2.87,.018,2.12),DARK,.015)
for z in [10.45+i*.14 for i in range(15)]:box('BH_SignBackSlat_'+str(z),(sx,sy-.205,z),(2.8,.035,.026),EDGE,.004)
children_since(before,ROOT)
GROUP='sign_panel';panel=empty('BH_SignFaceHinge',(sx,sy-.23,10.24));parent(panel,ROOT);before=set(bpy.data.objects)
box('BH_SignFacePanel',(sx,sy-.23,11.42),(3.05,.13,2.34),BLUE,.045);box('BH_SignIvoryFace',(sx,sy-.305,11.42),(2.73,.015,2.02),CREAM,.012)
text('BH_SignTitle','BOULDER HILL',(sx,sy-.322,11.95),.25,DARK,(pi/2,0,0));text('BH_SignGasShadow','GAS',(sx+.035,sy-.33,10.66),1.03,YELLOW,(pi/2,0,0));text('BH_SignGAS','GAS',(sx,sy-.345,10.70),1.03,BLACK,(pi/2,0,0))
for z in [10.48+i*.14 for i in range(14)]:box('BH_SignPanelBackGrille_'+str(z),(sx,sy-.15,z),(2.70,.018,.030),EDGE,.004)
children_since(before,panel);expression,variables=progress('sign_open',.20,.42);add_driver(panel,'rotation_euler',0,'3.14159265359*('+expression+')',variables)
GROUP='sign_guns';gun=empty('BH_SignCannonSlide',(sx,sy+.05,11.25));parent(gun,ROOT);before=set(bpy.data.objects)
for sg in [-1,1]:
 xx=sx+sg*.74;tube('BH_SignGun_'+str(sg),(xx,sy+.10,11.32),(xx,sy-.85,11.32),.10,BLACK,caps=False);tube('BH_SignGunBore_'+str(sg),(xx,sy-.78,11.32),(xx,sy-.86,11.32),.065,DARK)
 box('BH_SignGunMount_'+str(sg),(xx,sy+.08,11.32),(.33,.24,.37),BLACK,.035)
children_since(before,gun)
requested,variables=progress('sign_guns',.40,.55);variables+=[('h',ROOT,'sign_open')];open_expr='max(h,min(1,max(0,(b-0.20)/0.22)))';add_driver(gun,'location',1,f'{sy+.05}-.44*min(({requested}),min(1,max(0,(({open_expr})-.85)/.15)))',variables)
# Quarter-circle garage: same shell and station facade rotate 90 degrees in plan.
CURRENT=GARAGE;MODULE='garage';GROUP='garage_shell';garage=empty('BH_GarageQuarterPivot',(.20,0,0));parent(garage,ROOT);RADIUS=12.;GATE_HALF=math.asin(3.0/RADIUS);a0=pi/4-GATE_HALF;a1=pi/4+GATE_HALF
def annular_panel(name,amin,amax,rinner,router,zmin,zmax,mat,segments=24):
 v=[]
 for z,r in [(zmin,rinner),(zmin,router),(zmax,rinner),(zmax,router)]:v.extend((.20+r*cos(amin+(amax-amin)*i/segments),r*sin(amin+(amax-amin)*i/segments),z) for i in range(segments+1))
 n=segments+1;f=[]
 for j,k in [(0,1),(1,3),(3,2),(2,0)]:f.extend((j*n+i,j*n+i+1,k*n+i+1,k*n+i) for i in range(segments))
 f.extend([(0,n,3*n,2*n),(n-1,2*n-1,4*n-1,3*n-1)]);return mesh(name,v,f,mat,bevel=.012)
before=set(bpy.data.objects)
for idx,(lo,hi) in enumerate([(0,a0),(a1,pi/2)]):annular_panel('BH_QuarterArmorWall_'+str(idx),lo,hi,11.82,12.,.08,5.62,STEEL)
annular_panel('BH_GateLintel',a0,a1,11.82,12.,5.47,5.62,STEEL)
# Roof skin with the chamfered outside edge visible in all supplied deployed views.
N=64;v=[]
for r,z in [(0,6.40),(11.35,6.40),(12,5.67),(0,6.23),(11.35,6.23),(12,5.50)]:v.extend((.20+r*cos(i*pi/2/N),r*sin(i*pi/2/N),z) for i in range(N+1))
n=N+1;f=[]
for first,second in [(0,1),(1,2),(3,4),(4,5),(2,5)]:f.extend((first*n+i,first*n+i+1,second*n+i+1,second*n+i) for i in range(N))
for k in [0,N]:f.append(tuple(j*n+k for j in [0,1,2,5,4,3]))
mesh('BH_QuarterRoof',v,f,STEEL,bevel=.018)
for a in [pi/4]:path('BH_QuarterRoofRadialSeam',[(.20+r*cos(a),r*sin(a),6.425) for r in [.15,3,6,9,11.32]],.023,DARK)
for row,z in enumerate([.22,1.20,2.20,3.25,4.35,5.42]):
 for idx,(lo,hi) in enumerate([(0,a0),(a1,pi/2)]):path('BH_QuarterHorizontalSeam_'+str((row,idx)),[(.20+12.017*cos(lo+(hi-lo)*i/32),12.017*sin(lo+(hi-lo)*i/32),z) for i in range(33)],.012,DARK)
for idx,a in enumerate([i*pi/2/12 for i in range(13)]):
 if a0<a<a1:continue
 path('BH_QuarterVerticalSeam_'+str(idx),[(.20+12.018*cos(a),12.018*sin(a),z) for z in [.15,5.45]],.012,DARK)
# The original flat garage frontage is the leading radial bulkhead, stowed beside the shop after rotation.
box('BH_StationGarageBulkhead',(6.20,.10,3.05),(11.80,.16,5.92),WHITE,.035)
box('BH_StationGarageDarkPanel',(5.0,-.001,3.06),(8.15,.018,5.30),DARK,.015)
for j in range(16):
 z=.57+j*.318;box('BH_StationGarageShutterSlat_'+str(j),(5.0,-.035,z),(8.05,.08,.275),EDGE,.014)
 for x in [1.02,3.67,6.33,8.98]:box('BH_StationGarageSlatFrame_'+str((j,x)),(x,-.085,z),(.035,.03,.28),WHITE,.004)
box('BH_GarageSideServicePanel',(10.35,-.015,3.05),(2.12,.04,5.38),STEEL,.02)
for z in [1.1,2.5,3.9,5.2]:box('BH_GarageSidePanelSeam_'+str(z),(10.35,-.041,z),(2.05,.015,.024),DARK,.003)
children_since(before,garage)
doors=[]
for idx,(lo,hi,hinge_angle,sign) in enumerate([(a0,pi/4,a0,-1),(pi/4,a1,a1,1)],1):
 GROUP='gate_'+str(idx);hinge=empty('BH_ExitGateHinge_'+str(idx),(.20+12*cos(hinge_angle),12*sin(hinge_angle),0));parent(hinge,garage);before=set(bpy.data.objects)
 annular_panel('BH_ExitGateLeaf_'+str(idx),lo,hi,11.79,12.03,.12,5.43,STEEL,14)
 for z in [1.2,2.4,3.6,4.8]:path('BH_ExitGateHorizontalRib_'+str((idx,z)),[(.20+12.05*cos(lo+(hi-lo)*i/15),12.05*sin(lo+(hi-lo)*i/15),z) for i in range(16)],.025,EDGE)
 for j in [1,2,3]:
  a=lo+(hi-lo)*j/4;path('BH_ExitGateVerticalRib_'+str((idx,j)),[(.20+12.05*cos(a),12.05*sin(a),.30),(.20+12.05*cos(a),12.05*sin(a),5.25)],.024,EDGE)
 children_since(before,hinge);doors.append((hinge,sign))
# Travel safety opens garage/doors during vehicle movement; no Python namespace dependency after reopen.
travel='max(min(1,max(0,t*100))*min(1,max(0,(1-t)*100)),min(1,max(0,r*100))*min(1,max(0,(1-r)*100)))'
variables=[('v',ROOT,'garage_deploy'),('b',ROOT,'battle_mode'),('t',ROOT,'thunderhawk_exit'),('r',ROOT,'rhino_exit')];garage_expr=f'max(v,min(1,max(0,b/.32)),({travel}))';add_driver(garage,'rotation_euler',2,'-1.57079632679*('+garage_expr+')',variables)
for hinge,sg in doors:
 variables=[('g',ROOT,'gate_open'),('d',ROOT,'garage_deploy'),('b',ROOT,'battle_mode'),('t',ROOT,'thunderhawk_exit'),('r',ROOT,'rhino_exit')];dexpr=f'max(d,min(1,max(0,b/.32)),({travel}))';gexpr=f'min(max(g,({travel})),min(1,max(0,({dexpr}-.98)/.02)))';add_driver(hinge,'rotation_euler',2,f'{sg*1.78}*('+gexpr+')',variables)
# Interpreted rear hangar: four full-size parking berths and an independent manoeuvring aisle.
CURRENT=HANGAR;MODULE='hangar';GROUP='hangar_static';before=set(bpy.data.objects)
box('BH_HangarFloor',(.2,19.0,-.10),(25.8,38.0,.20),CONCRETE,.04)
for x in [-12.5,13.0]:box('BH_HangarSideWall_'+str(x),(x,19.0,3.30),(.25,38.0,6.6),STEEL,.045)
box('BH_HangarRearWall',(.2,37.9,3.30),(25.6,.25,6.6),STEEL,.045);box('BH_HangarCeiling',(.2,19.0,6.70),(25.8,38.0,.20),STEEL,.035)
for y in [2,9,16,23,30,37]:
 box('BH_HangarRoofBeam_'+str(y),(.2,y,6.42),(25.25,.18,.28),EDGE,.02)
 for x in [-12.25,12.75]:box('BH_HangarColumn_'+str((x,y)),(x,y,3.2),(.18,.25,6.4),EDGE,.02)
for idx,y in enumerate([15.,21.,27.,33.],1):
 for yy in [y-2.25,y+2.25]:box('BH_BayLine_'+str((idx,yy)),(-5.6,yy,.020),(10.8,.065,.012),YELLOW,.003)
 box('BH_BayBackLine_'+str(idx),(-11.0,y,.020),(.065,4.5,.012),YELLOW,.003)
 text('BH_BayNumber_'+str(idx),str(idx).zfill(2),(-.45,y-.60,.035),.65,YELLOW,(0,0,pi/2))
for y in range(11,36,4):box('BH_AisleDashedLine_'+str(y),(6,y,.024),(.07,1.65,.014),WHITE,.003)
for y in [18,24,30,35]:
 box('BH_ServiceCabinet_'+str(y),(11.9,y,1.20),(1.10,2.3,2.35),BLUE,.05)
 for z in [.5,1.0,1.5,2.0]:box('BH_ServiceDrawer_'+str((y,z)),(11.31,y,z),(.03,2.05,.045),EDGE,.005)
for y in [6,8,10]:
 box('BH_ControlConsole_'+str(y),(-10.7,y,1.05),(2.1,1.65,1.9),EDGE,.07);box('BH_ControlScreen_'+str(y),(-9.62,y,1.55),(.025,1.0,.58),SCREEN,.02)
children_since(before,ROOT)
# Coherent eroded sandstone shell, hollow below the roof so the vehicles really fit.
CURRENT=ROCK;MODULE='rock';GROUP='rock_static';before=set(bpy.data.objects)
def ridge(x,y):return 7.35+2.4*exp(-((x-6.5)/5.5)**2-((y-5.0)/6.0)**2)+.5*sin(x*.47+y*.13)+.35*sin(y*.41+x*.19)
NX=68;NY=90;v=[];f=[]
for j in range(NY):
 y=.65+j*37.6/(NY-1)
 for i in range(NX):
  x=-13.15+i*27.1/(NX-1);z=ridge(x,y)+.13*sin(x*3.7+y*1.6)+.09*sin(x*8-y*4);v.append((x,y,z))
for j in range(NY-1):
 for i in range(NX-1):
  ids=(j*NX+i,j*NX+i+1,(j+1)*NX+i+1,(j+1)*NX+i);center=sum((Vector(v[k]) for k in ids),Vector())/4
  if (center.x-7)**2+(center.y-6)**2<2.95**2:continue
  f.append(ids)
ob=mesh('BH_SandstoneRoof',v,f,STONE,smooth=True);mod=ob.modifiers.new('RockRoofThickness','SOLIDIFY');mod.thickness=.18
def cliff_wall(name,side):
 vv=[];ff=[];N=100;H=27
 for j in range(H):
  t=j/(H-1)
  for i in range(N):
   q=i/(N-1)
   if side=='front':x=-13.15+q*27.1;y=.65;bottom=6.58
   elif side=='back':x=-13.15+q*27.1;y=38.25;bottom=-.30
   else:x=-13.15 if side=='left' else 13.95;y=.65+q*37.6;bottom=-.30
   z=bottom+(ridge(x,y)-bottom)*t;terrace=.18*sin(t*31)+.20*sin(q*40+sin(t*12));striae=.17*sin(q*130+t*2)+.085*sin(q*310-t*3)
   if side in ['front','back']:y+=(-1 if side=='front' else 1)*(terrace+striae+.16*(1-t))
   else:x+=(-1 if side=='left' else 1)*(terrace+striae+.16*(1-t))
   vv.append((x,y,z))
 for j in range(H-1):ff.extend((j*N+i,j*N+i+1,(j+1)*N+i+1,(j+1)*N+i) for i in range(N-1))
 return mesh(name,vv,ff,STONE,smooth=True)
for side in ['front','back','left','right']:cliff_wall('BH_SandstoneCliff_'+side,side)
# Tall hollow column with terraces, not stacked spheres. The cap is a distinct falling rock.
v=[];f=[];N=128;H=49
for j in range(H):
 t=j/(H-1);z=8.1+t*3.92;base=3.6-1.05*t+.21*sin(t*14)
 for i in range(N):
  a=i*2*pi/N;r=base+.12*sin(a*17+t*3)+.06*sin(a*41-t*6);v.append((7+r*cos(a),6+r*sin(a),z+.08*sin(a*13+t*4)))
for j in range(H-1):f.extend((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i) for i in range(N))
mesh('BH_RockColumnOuter',v,f,STONE,smooth=True)
v=[];f=[]
for r,z in [(2.55,12.02),(2.15,12.02),(2.15,9.1)]:v.extend((7+r*cos(i*2*pi/N),6+r*sin(i*2*pi/N),z+.04*sin(i*13*2*pi/N)) for i in range(N))
for j in range(2):f.extend((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i) for i in range(N))
mesh('BH_RockColumnInnerRim',v,f,STONE,smooth=True);children_since(before,ROOT)
GROUP='cap';cap=empty('BH_FallingBoulder',(7,6,13.22));parent(cap,ROOT);v=[];f=[];rows=[(-1.15,2.42),(-.94,2.62),(-.4,2.57),(.2,2.38),(.7,1.90),(1.10,1.18),(1.30,.02)];N=96
for j,(z,radius) in enumerate(rows):
 for i in range(N):
  a=i*2*pi/N;r=radius*(1+.045*sin(a*9+j*.9)+.025*sin(a*23-j));v.append((7+r*cos(a),6+r*sin(a),13.22+z+.065*sin(a*17+j*2)*sin(pi*j/(len(rows)-1))))
for j in range(len(rows)-1):f.extend((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i) for i in range(N))
f.extend([tuple(reversed(range(N))),tuple(range((len(rows)-1)*N,len(rows)*N))]);parent(mesh('BH_BoulderCapMesh',v,f,STONE,smooth=True),cap)
c,variables=progress('boulder_fall',.57,.79)
def bezier_expr(a,b,c1,d,t):return f'{a}*(1-({t}))**3+3*{b}*(1-({t}))**2*({t})+3*{c1}*(1-({t}))*({t})**2+{d}*({t})**3'
for index,values in [(0,(7,10,23,22)),(1,(6,6,1,1)),(2,(13.22,17.3,8,.85))]:add_driver(cap,'location',index,bezier_expr(*values,c),variables)
add_driver(cap,'rotation_euler',0,'6.28318530718*min(1,max(0,(('+c+')-.40)/.60))',variables);add_driver(cap,'rotation_euler',2,'3.14159265359*('+c+')',variables)
# Gun and chair rise together after the boulder has cleared the column.
CURRENT=TURRET;MODULE='turret';GROUP='turret';turret=empty('BH_TurretLift',(7,6,9.7));parent(turret,ROOT);before=set(bpy.data.objects)
tube('BH_TurretPlatform',(7,6,9.65),(7,6,9.85),1.85,BLACK,N=64);tube('BH_TurretLiftRam',(7,6,8.9),(7,6,9.65),.34,CHROME)
box('BH_TurretSeatBase',(7.70,6.45,10.17),(.78,.86,.23),SEAT,.09);box('BH_TurretSeatBack',(7.70,6.87,10.78),(.82,.19,1.12),SEAT,.10)
for sg in [-1,1]:path('BH_TurretArmrest_'+str(sg),[(7.70+sg*.48,6.75,10.58),(7.70+sg*.48,6.0,10.58)],.055,BLACK)
box('BH_TurretFootplate',(7.70,5.50,9.95),(.86,.66,.10),EDGE,.025);box('BH_TurretConsole',(7.70,5.68,10.55),(.70,.27,.28),EDGE,.05);box('BH_TurretScreen',(7.70,5.52,10.60),(.42,.016,.15),SCREEN,.008)
box('BH_TurretGunReceiver',(6.67,5.86,10.66),(.66,1.15,.54),BLACK,.065)
tube('BH_TurretTrunnion',(6.20,5.98,10.65),(7.20,5.98,10.65),.17,EDGE)
children_since(before,turret)
barrel=empty('BH_TurretBarrelExtension',(6.67,5.35,10.68));parent(barrel,turret);before=set(bpy.data.objects)
tube('BH_TurretBarrel',(6.67,5.35,10.68),(6.67,2.25,10.68),.15,BLACK,N=48,caps=False)
for y in [2.30,2.70,3.4,4.1,4.9]:tube('BH_TurretBarrelBand_'+str(y),(6.67,y-.05,10.68),(6.67,y+.05,10.68),.18,EDGE,N=32)
tube('BH_TurretMuzzleBore',(6.67,2.35,10.68),(6.67,2.24,10.68),.105,DARK,N=32);children_since(before,barrel)
lift,variables=progress('turret_lift',.80,.96);variables+=[('c',ROOT,'boulder_fall')];cap_clear='min(1,max(0,(max(c,min(1,max(0,(b-.57)/.22)))-.72)/.28))';lift=f'min(({lift}),({cap_clear}))';add_driver(turret,'location',2,'9.7+2.4*('+lift+')',variables);add_driver(turret,'rotation_euler',2,'a*0.0174532925199',[('a',ROOT,'turret_yaw')])
extension,variables=progress('turret_extension',.87,1.0);variables+=[('l',ROOT,'turret_lift'),('c',ROOT,'boulder_fall')];clear_lift=f'min(max(l,min(1,max(0,(b-.80)/.16))),({cap_clear}))';add_driver(barrel,'scale',1,f'.23+.77*min(({extension}),min(1,max(0,(({clear_lift})-.85)/.15)))',variables)
# Native path constraints: editable vehicle examples at actual scale, frozen in road configuration.
CURRENT=ROUTES;MODULE='routes';GROUP='route';route_meta={}
def exit_route(bay_y):
 p=[]
 def line(a,b,steps=25):
  a,b=Vector(a),Vector(b);p.extend(tuple(a.lerp(b,i/steps)) for i in range(steps))
 line((-5.6,bay_y,0),(-2,bay_y,0),16)
 for i in range(61):
  a=(pi/2)*i/60;p.append((-2+8*sin(a),bay_y-8+8*cos(a),0))
 line((6,bay_y-8,0),(6,-2,0),40)
 for i in range(46):
  a=(pi/4)*i/45;p.append((15-9*cos(a),-2-9*sin(a),0))
 end=Vector(p[-1]);line(end,end+Vector((1,-1,0)).normalized()*15,45);p.append(tuple(end+Vector((1,-1,0)).normalized()*15))
 lengths=[0.]
 for a,b in zip(p,p[1:]):lengths.append(lengths[-1]+(Vector(b)-Vector(a)).length)
 uniform=[];cursor=0
 for i in range(241):
  distance=lengths[-1]*i/240
  while cursor+1<len(lengths)-1 and lengths[cursor+1]<distance:cursor+=1
  span=max(.000001,lengths[cursor+1]-lengths[cursor]);uniform.append(tuple(Vector(p[cursor]).lerp(Vector(p[cursor+1]),(distance-lengths[cursor])/span)))
 return uniform,lengths[-1]
for label,y,key in [('Thunderhawk',15,'thunderhawk_exit'),('Rhino',33,'rhino_exit')]:
 pts,length=exit_route(y);cu=bpy.data.curves.new('BH_'+label+'_ExitRoute','CURVE');cu.dimensions='3D';cu.path_duration=240;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for point,xyz in zip(sp.points,pts):point.co=(*xyz,1)
 route=bpy.data.objects.new(cu.name,cu);ROUTES.objects.link(route);parent(route,ROOT);route.hide_render=True
 actor=bpy.data.objects['BH_'+label+'_PathRoot'];actor.location=(0,0,0);actor.rotation_euler=(0,0,0);parent(actor,ROOT)
 con=actor.constraints.new('FOLLOW_PATH');con.name='Native exit path';con.target=route;con.use_fixed_location=True;con.use_curve_follow=True;con.forward_axis='FORWARD_X';con.up_axis='UP_Z'
 f=con.driver_add('offset_factor');d=f.driver;v=d.variables.new();v.name='p';v.type='SINGLE_PROP';v.targets[0].id=ROOT;v.targets[0].data_path='["'+key+'"]';d.expression='min(1,max(0,p))'
 route_meta[label]={'bay_y':y,'path_length_m':length,'samples':pts,'control':key,'note':'Kinematic clearance path, not steering or suspension simulation.'}
(A/'exit_routes_v1.json').write_text(json.dumps(route_meta,indent=2))
# Studio-like daylight lets the geological silhouette and gunmetal relationships read clearly.
CURRENT=STUDIO;GROUP='studio';MODULE='studio'
world=bpy.data.worlds.new('BH_DesertWorld');world.use_nodes=True;S.world=world;bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.42,.58,.75,1);bg.inputs[1].default_value=.55
ld=bpy.data.lights.new('BH_DesertSun','SUN');ld.energy=2.8;ld.angle=.14;sun=bpy.data.objects.new(ld.name,ld);STUDIO.objects.link(sun);sun.rotation_euler=(.52,-.42,-.55)
for name,loc,power,size in [('Key',(-16,-20,30),3200,16),('CaveFill',(1,20,5.7),1900,14),('EntranceFill',(7,-5,5.2),600,5)]:
 ld=bpy.data.lights.new('BH_'+name,'AREA');ld.energy=power;ld.shape='DISK';ld.size=size;ob=bpy.data.objects.new(ld.name,ld);STUDIO.objects.link(ob);ob.location=loc;target=Vector((0,8,1)) if 'Fill' in name else Vector((0,0,3));ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler()
cd=bpy.data.cameras.new('Boulder_ReviewCamera');camera=bpy.data.objects.new(cd.name,cd);STUDIO.objects.link(camera);camera.location=(39,-48,32);camera.rotation_euler=(Vector((1,1,5))-camera.location).to_track_quat('-Z','Y').to_euler();cd.lens=47;cd.clip_end=500;S.camera=camera
S.render.engine='CYCLES';S.cycles.samples=24;S.cycles.use_denoising=True
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.get_devices();S.cycles.device='GPU'
except Exception:S.cycles.device='CPU'
S.render.resolution_x=1300;S.render.resolution_y=900;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';S.view_settings.view_transform='AgX';S.render.fps=30;S.frame_start=1;S.frame_end=541
for key,keys in [('battle_mode',[(1,0),(31,0),(181,1),(541,1)]),('gate_open',[(1,0),(181,0),(211,1),(541,1)]),('thunderhawk_exit',[(1,0),(211,0),(331,1),(541,1)]),('rhino_exit',[(1,0),(351,0),(531,1),(541,1)])]:
 for frame,value in keys:ROOT[key]=float(value);ROOT.keyframe_insert(data_path='["'+key+'"]',frame=frame)
if ROOT.animation_data and ROOT.animation_data.action:
 action=ROOT.animation_data.action
 try:curves=list(action.fcurves)
 except Exception:curves=[fc for layer in action.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves]
 for fc in curves:
  for point in fc.keyframe_points:point.interpolation='LINEAR'
for name,frame in [('STATION',1),('TRANSFORMATION',31),('DEFENSE',181),('PORTE OUVERTE',211),('THUNDERHAWK SORT',293),('RHINO SORT',490)]:S.timeline_markers.new(name,frame=frame)
# All static objects belong to the environment controller; demo sources stay independently editable.
for co in [GROUND,SHOP,GARAGE,PUMPS,SIGN,ROCK,TURRET,HANGAR]:
 for ob in co.objects:
  if ob!=ROOT and ob.parent is None:parent(ob,ROOT)
for ob in S.objects:
 if ob.animation_data:
  for fc in ob.animation_data.drivers:fc.driver.expression=fc.driver.expression+' + 0.0';ob.update_tag()
S.frame_set(1);ROOT.update_tag();bpy.context.view_layer.update()
bad=[ob.name+':'+fc.data_path for ob in S.objects if ob.animation_data for fc in ob.animation_data.drivers if not fc.driver.is_valid]
S['BoulderVersion']='V1';S['reference_policy']='Supplied toy photographs and cartoon video seconds1-13 inspected. Hidden mechanisms and enlarged hangar/vehicle paths interpreted.';S['layout']='Four bays 10.8 x 4.5m, 6m centre spacing; clear 6m double gate, 5.43m nominal aperture. Actual vehicle scale retained.'
(A/'build_report_v1.json').write_text(json.dumps({'objects':len(S.objects),'invalid_drivers':bad,'vehicle_measurements':'vehicle_measurements_v1.json','reference_video':'https://www.youtube.com/watch?v=CYgT9k8lJyY','interval_inspected':[1,13],'capacity':4,'bay_dimensions_m':[10.8,4.5],'gate_nominal_width_m':6.0,'gate_nominal_height_m':5.43,'estimated_kinematics':True},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(A/'BoulderHill_V1_Assembly.blend'),compress=True);print('BOULDER_HILL_V1_BUILT',len(S.objects),'invalid drivers',bad)
