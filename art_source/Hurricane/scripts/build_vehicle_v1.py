"""Reference-led editable Hurricane. All dimensions and hidden engineering estimated."""
import bpy,json,math,random
from pathlib import Path
from mathutils import Vector
from math import sin,cos,pi,sqrt
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Hurricane';S=bpy.context.scene
assert Path(bpy.data.filepath).name=='Hurricane_prepared_v1.blend'
assert not (A/'Hurricane_V1_Assembly.blend').exists()
exec(compile((A/'scripts/geometry.py').read_text(),'<geometry>','exec'))
BODY=collection('HU_Body');FRAME=collection('HU_RunningGear');CABIN=collection('HU_Interior');WEAPONS=collection('HU_Weapons');STUDIO=collection('HU_Studio');CURRENT=BODY
TEAL=material('HU_TurquoisePaint',(.008,.255,.235),.48,.27);CHROME=material('HU_Chrome',(.66,.72,.74),.95,.19);BRUSH=material('HU_BrushedAlloy',(.37,.43,.45),.82,.33);BLACK=material('HU_ChassisGraphite',(.014,.020,.024),.48,.48);DARK=material('HU_Recess',(.003,.006,.008),.05,.64);RUBBER=material('HU_TireRubber',(.012,.015,.017),0,.76);MAGENTA=material('HU_WeaponBurgundy',(.36,.012,.080),.38,.30);GOLD=material('HU_GoldBadge',(.72,.40,.025),.75,.24);LENS=material('HU_HeadlampGlass',(.72,.82,.84),.05,.12);RED=material('HU_TailLens',(.42,.004,.007),.18,.22);AMBER=material('HU_AmberLens',(.85,.23,.012),.2,.25);GLASS=material('HU_TintedGlass',(.25,.38,.39),.03,.09);LEATHER=material('HU_SeatLeather',(.035,.045,.048),0,.66);CARPET=material('HU_CabinCarpet',(.019,.027,.029),0,.95);WHITE=material('HU_InstrumentMark',(.65,.74,.72),.1,.40)
next(n for n in GLASS.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Transmission Weight'].default_value=1
next(n for n in GLASS.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['IOR'].default_value=1.45
for m,scale,distance in [(TEAL,180,.00018),(RUBBER,140,.0006),(LEATHER,280,.0005)]:
    ns=m.node_tree.nodes;ls=m.node_tree.links;n=ns.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=scale;b=ns.new('ShaderNodeBump');b.inputs['Strength'].default_value=.15;b.inputs['Distance'].default_value=distance;ls.new(n.outputs['Fac'],b.inputs['Height']);ls.new(b.outputs['Normal'],next(n for n in ns if n.type=='BSDF_PRINCIPLED').inputs['Normal'])
for m,c,power in [(LENS,(.7,.85,1,1),.10),(RED,(.8,.005,.002,1),.18),(AMBER,(1,.2,.006,1),.2)]:
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Emission Color'].default_value=c;p.inputs['Emission Strength'].default_value=power
ROOT=empty('Hurricane_Control');ROOT['battle_mode']=0.
for key in ['chassis_lift','roof_open','roof_guns','windshield_cannon','headlight_cannons','lower_cannons','rear_disc','spare_eject']:
    ROOT[key]=0.;ROOT.id_properties_ui(key).update(min=0,max=1,description='0 route / 1 deploye. Commande native editable.')
ROOT['disc_spin']=0.;ROOT.id_properties_ui('disc_spin').update(min=-720,max=720,description='Rotation du disque dente, degres')
ROOT['dimensions_note']='Estimated from supplied 1957 Chevrolet and Hurricane toy photographs; approx 5.25m body, 1.98m width, 2.96m wheelbase. Not official dimensions.'
ROOT['wheel_manifest']='Six persistent road tires: four road wheels and one retractable middle pair; separate rear spare tire and cover, ejected as one assembly.'
def derived(name,expr,vars):ROOT[name]=0.;drive(ROOT,'["'+name+'"]',None,expr,[(n,ROOT,k) for n,k in vars])
def request(key,a,b):return f'max(v,min(1,max(0,(b-{a})/{b-a})))',[('v',key),('b','battle_mode')]
for name,key,a,b in [('_lift','chassis_lift',0,.35),('_roof','roof_open',.22,.57),('_lamps','headlight_cannons',.40,.64),('_wind','windshield_cannon',.52,.78)]:
    e,v=request(key,a,b);derived(name,e,v)
derived('_roofgun','min(max(v,min(1,max(0,(b-.52)/.20))),min(1,max(0,(r-.78)/.22)))',[('v','roof_guns'),('b','battle_mode'),('r','_roof')])
derived('_lower','min(max(v,min(1,max(0,(b-.60)/.25))),min(1,max(0,(l-.80)/.20)))',[('v','lower_cannons'),('b','battle_mode'),('l','_lift')])
derived('_disc','min(max(v,min(1,max(0,(b-.65)/.25))),min(1,max(0,(l-.85)/.15)))',[('v','rear_disc'),('b','battle_mode'),('l','_lift')])
LIFT=empty('HU_UpperChassisLift',parent=ROOT);drive(LIFT,'location',2,'.58*l',[('l',ROOT,'_lift')]);PARENT=LIFT
def width(x):return profile(x,[(-2.62,.88),(-2.38,.97),(-1.40,.97),(0,.98),(1.5,.94),(2.27,.94),(2.55,.85)])
def belt(x):return profile(x,[(-2.62,1.28),(-2.28,1.22),(-1.25,1.12),(.15,1.13),(.85,1.12),(1.8,1.10),(2.55,1.12)])
def bottom(x):
    z=.34
    for cx in [-1.48,1.48]:
        if abs(x-cx)<.445:z=max(z,.38+sqrt(.445**2-(x-cx)**2))
    return z
def side_y(x,z):
    t=max(0,min(1,(z-bottom(x))/max(.05,belt(x)-bottom(x))));return width(x)-.065*(1-t)**2-.025*t*t+.015*sin(pi*t)
GROUP='body'
xs=sorted(set(seq(120,-2.62,2.55)+[-1.925,-1.48,-1.035,1.035,1.48,1.925]))
for sg,label in [(1,'L'),(-1,'R')]:
    patch('HU_SculptedSide_'+label,xs,seq(14),lambda x,t,sg=sg:(x,sg*side_y(x,bottom(x)+(belt(x)-bottom(x))*t),bottom(x)+(belt(x)-bottom(x))*t),TEAL,orient=(0,sg,0),sub=1)
    # Wheel arch folded lips and black inner tubs follow the same real openings.
    for cx,ax in [(-1.48,'Rear'),(1.48,'Front')]:
        pts=[]
        for a in seq(64,0,pi):
            x=cx+.445*cos(a);z=.38+.445*sin(a);pts.append((x,sg*(side_y(x,z)+.006),z))
        path('HU_ArchChrome_'+label+'_'+ax,pts,.012,CHROME)
        patch('HU_WheelWell_'+label+'_'+ax,seq(48,0,pi),[.69,.87,.93],lambda a,y,cx=cx,sg=sg:(cx+.454*cos(a),sg*y,.38+.454*sin(a)),BLACK,sub=0,thick=.006,orient=(0,0,-1))
    # Rounded upper fender crown; hood remains visibly lower than the lamp eyebrows.
    patch('HU_FrontFenderCrown_'+label,seq(48,.80,2.48),seq(16),lambda x,t,sg=sg:(x,sg*(.64+(width(x)-.64)*t),belt(x)+.048*sin(pi*t)+.015*(1-t)),TEAL,orient=(0,0,1))
    # Tail fins, with a sharp rear peak and a broad 1957-style chrome insert.
    patch('HU_TailFinCrown_'+label,seq(42,-2.61,-.92),seq(9),lambda x,t,sg=sg:(x,sg*(.76+(width(x)-.76)*t),belt(x)+.10*sin(pi*t)*max(0,(-x-.92)/1.69)),TEAL,orient=(0,0,1))
    poly=[(-2.55,1.235),(-.93,1.075),(-2.55,.91)]
    mesh('HU_BelAirSideInsert_'+label,[(x,sg*(side_y(x,z)+.009),z) for x,z in poly],[(0,1,2)],BRUSH,smooth=False,orient=(0,sg,0))
    for i in range(1,22):
        z=.916+i*.014;xend=-2.55+(1.62)*(z-.91)/(.165) if z<1.075 else -2.55+(1.62)*(1.235-z)/(.160)
        if xend>-2.52:path('HU_InsertStrake_'+str((label,i)),[(x,sg*(side_y(x,z)+.012),z) for x in seq(12,-2.53,min(-.95,xend))],.0025,CHROME)
    path('HU_BelAirLongChrome_'+label,[(x,sg*(side_y(x,profile(x,[(-2.55,1.235),(-.93,1.075),(2.37,.90)]))+.012),profile(x,[(-2.55,1.235),(-.93,1.075),(2.37,.90)])) for x in seq(100,-2.55,2.37)],.009,CHROME)
    outline=[(-.76,.39),(.87,.39),(.87,1.12),(-.76,1.12),(-.76,.39)]
    path('HU_DoorShutLine_'+label,[(x,sg*(side_y(x,z)+.002),z) for x,z in outline],.004,DARK)
    path('HU_DoorHandle_'+label,[(-.63,sg*1.003,1.06),(-.63,sg*1.021,1.08),(-.43,sg*1.021,1.08),(-.43,sg*1.003,1.06)],.009,CHROME)
    for k in range(3):path('HU_FrontFenderVent_'+str((label,k)),[(1.84-k*.085,sg*.969,1.005),(1.80-k*.085,sg*.969,.934)],.009,CHROME)
    tube('HU_SidePipe_'+label,(-1.18,sg*1.002,.31),(.94,sg*1.002,.31),.035,CHROME)
    for x in [-.95,.75]:tube('HU_SidePipeMount_'+str((label,x)),(x,sg*.91,.40),(x,sg*1.0,.32),.018,BRUSH)
# Crowned hood, boot and sculpted central nose.
patch('HU_CurvedHood',seq(55,.89,2.37),seq(36,-.68,.68),lambda x,y:(x,y,profile(x,[(.89,1.145),(1.45,1.13),(2.37,1.045)])+.055*(1-(y/.68)**2)),TEAL,orient=(0,0,1))
path('HU_HoodShutLine',[(x,y,z+.003) for x,y,z in [(x,sg*.69,profile(x,[(.89,1.145),(1.45,1.13),(2.37,1.045)])) for sg in [-1,1] for x in seq(35,.89,2.37)]],.003,DARK)
patch('HU_CurvedTrunk',seq(40,-2.49,-1.11),seq(26,-.77,.77),lambda x,y:(x,y,1.06+.045*(1-(y/.77)**2)),TEAL,orient=(0,0,1))
patch('HU_NosePanel',seq(30,-.64,.64),seq(15,.72,1.04),lambda y,z:(2.41+.09*(1-(y/.70)**2),y,z),TEAL,orient=(1,0,0))
path('HU_HoodVBadge',[(2.22,.17,1.11),(2.35,0,1.105),(2.22,-.17,1.11)],.011,GOLD)
for sg in [-1,1]:tube('HU_HoodJetOrnament_'+str(sg),(1.62,sg*.49,1.18),(1.91,sg*.49,1.16),.015,CHROME,r2=.007)
# Front grille bowl and flowing chrome bumper.
box('HU_GrilleRecess',(2.465,0,.625),(.045,1.72,.27),DARK,.055)
for z in [.515,.548,.581,.614,.647,.680,.713,.746]:
    path('HU_GrilleHorizontal_'+str(z),[(2.51+.025*(1-(y/.84)**2),y,z) for y in seq(30,-.84,.84)],.006,CHROME)
for y in seq(76,-.83,.83):tube('HU_GrilleMeshTooth_'+str(y),(2.525,y,.52),(2.525,y,.74),.0032,BRUSH,N=8)
for z in [.49,.76]:path('HU_GrilleSurround_'+str(z),[(2.53+.03*(1-(y/.86)**2),y,z) for y in seq(40,-.86,.86)],.024,CHROME)
path('HU_FrontBumper',[(2.37,-.99,.48),(2.51,-.96,.46),(2.64,-.75,.45),(2.66,0,.445),(2.64,.75,.45),(2.51,.96,.46),(2.37,.99,.48)],.050,CHROME)
for sg in [-1,1]:
    tube('HU_BumperBullet_'+str(sg),(2.53,sg*.73,.50),(2.72,sg*.73,.50),.065,CHROME,r2=.035)
    tube('HU_Indicator_'+str(sg),(2.52,sg*.67,.79),(2.54,sg*.67,.79),.042,AMBER,N=32)
# Wrap-around glass and fixed perimeter, with a physical aperture for the left gun.
GROUP='glass'
def wind(y,t):return (1.015-.35*t-.055*(y/.80)**2,y,1.15+.49*t)
ys=sorted(set(seq(36,-.80,.80)+[.34,.72]));ts=sorted(set(seq(14)+[.16,.78]))
patch('HU_WraparoundWindshield',ys,ts,wind,GLASS,sub=0,thick=.004,orient=(1,0,.7),skip=lambda y,t:.34<y<.72 and .16<t<.78)
for t in [0,1]:path('HU_WindshieldChrome_'+str(t),[wind(y,t) for y in seq(64,-.80,.80)],.014,CHROME)
for sg in [-1,1]:path('HU_A_Pillar_'+str(sg),[wind(sg*.80,t) for t in seq(20)],.029,TEAL)
for sg,label in [(1,'L'),(-1,'R')]:
    def sidewindow(u,t,sg=sg):
        lo=-1.18+.31*t;hi=1.015-.35*t;x=lo+(hi-lo)*u;return(x,sg*(.825-.16*t),1.15+.49*t+.012*sin(pi*u))
    patch('HU_SideWindow_'+label,seq(48),seq(12),sidewindow,GLASS,sub=0,thick=.004,orient=(0,sg,0))
    for t in [0,1]:path('HU_SideWindowChrome_'+str((label,t)),[sidewindow(u,t) for u in seq(50)],.012,CHROME)
    for u in [0,1]:path('HU_SideWindowEnd_'+str((label,u)),[sidewindow(u,t) for t in seq(20)],.016,CHROME)
    path('HU_QuarterWindowDivision_'+label,[sidewindow(.31,t) for t in seq(15)],.010,CHROME)
    tube('HU_MirrorStem_'+label,(.78,sg*.86,1.12),(.76,sg*1.04,1.25),.012,CHROME)
    tube('HU_MirrorBack_'+label,(.76,sg*1.04,1.25),(.73,sg*1.04,1.25),.063,CHROME,N=36)
    tube('HU_MirrorGlass_'+label,(.726,sg*1.04,1.25),(.724,sg*1.04,1.25),.054,BRUSH,N=36)
patch('HU_RearWrapGlass',seq(36,-.73,.73),seq(12),lambda y,t:(-1.18+.31*t+.05*(y/.73)**2,y,1.15+.49*t),GLASS,sub=0,thick=.004,orient=(-1,0,.6))
for t in [0,1]:path('HU_RearWindowChrome_'+str(t),[(-1.18+.31*t+.05*(y/.73)**2,y,1.15+.49*t) for y in seq(50,-.73,.73)],.014,CHROME)
GROUP='body'
for sg in [-1,1]:path('HU_RoofSideRail_'+str(sg),[(-.90,sg*.67,1.65),(-.45,sg*.67,1.68),(.60,sg*.67,1.66)],.032,TEAL)
patch('HU_RearRoofArch',seq(18,-.90,-.45),seq(18,-.66,.66),lambda x,y:(x,y,1.66+.025*(1-(y/.66)**2)),TEAL,orient=(0,0,1))
ROOF=empty('HU_RoofHinge',(.60,0,1.66),LIFT);drive(ROOF,'rotation_euler',1,'1.57079632679*r',[('r',ROOT,'_roof')]);GROUP='roof'
patch('HU_OpeningRoofPanel',seq(35,-.45,.60),seq(24,-.64,.64),lambda x,y:(x,y,1.66+.024*(1-(y/.64)**2)),TEAL,root=ROOF,thick=.014,orient=(0,0,1))
box('HU_RoofInnerArmor',(.075,0,1.635),(1.02,1.23,.025),BLACK,.012,ROOF)
for y in [-.50,.50]:tube('HU_RoofHingePin_'+str(y),(.60,y-.065,1.66),(.60,y+.065,1.66),.022,CHROME,root=LIFT)
# Rear closure and lights; no open trunk seen through the glazing.
GROUP='body'
box('HU_RearFascia',(-2.55,0,.80),(.11,1.76,.57),TEAL,.045)
path('HU_RearBumper',[(-2.49,-.98,.47),(-2.64,-.86,.45),(-2.68,-.42,.44),(-2.79,0,.34),(-2.68,.42,.44),(-2.64,.86,.45),(-2.49,.98,.47)],.047,CHROME)
for sg in [-1,1]:
    for j,z in enumerate([.83,1.035]):
        tube('HU_TailChrome_'+str((sg,j)),(-2.58,sg*.85,z),(-2.625,sg*.85,z),.067,CHROME,N=36)
        tube('HU_TailLens_'+str((sg,j)),(-2.626,sg*.85,z),(-2.632,sg*.85,z),.049,RED,N=36)
# Interior separated from mechanical side pockets, including rear shelf and firewall.
CURRENT=CABIN;PARENT=LIFT;GROUP='interior'
box('HU_CabinFloor',(-.18,0,.49),(2.10,1.31,.06),BLACK,.02)
box('HU_FloorCarpet',(-.20,0,.525),(1.95,1.27,.012),CARPET,.015)
box('HU_RearBulkhead',(-1.22,0,.82),(.06,1.50,.62),BLACK,.012)
box('HU_ParcelShelf',(-1.38,0,1.02),(.42,1.46,.08),LEATHER,.02)
box('HU_Firewall',(.88,0,.86),(.08,1.44,.60),BLACK,.015)
box('HU_Dashboard',(.73,0,1.075),(.32,1.46,.22),LEATHER,.04)
for sg in [-1,1]:
    box('HU_DoorInnerTrim_'+str(sg),(-.10,sg*.75,.91),(1.59,.045,.37),LEATHER,.025)
    path('HU_DoorPull_'+str(sg),[(-.30,sg*.714,.95),(-.30,sg*.69,.93),(-.05,sg*.69,.93),(-.05,sg*.714,.95)],.012,CHROME)
for label,y in [('Driver',.40),('Passenger',-.40)]:
    box('HU_'+label+'SeatPan',(-.53,y,.735),(.65,.39,.18),LEATHER,.065)
    ob=box('HU_'+label+'SeatBack',(-.82,y,1.00),(.16,.41,.58),LEATHER,.06)
    for yy in [y-.13,y,y+.13]:path('HU_'+label+'SeatStitch_'+str(yy),[(-.78,yy,.81),(-.75,yy,1.16)],.002,BRUSH)
    for x in [-.73,-.30]:tube('HU_'+label+'SeatLeg_'+str(x),(x,y,.53),(x,y,.66),.022,BLACK)
for y in [.28,.40,.52]:
    tube('HU_DialRim_'+str(y),(.55,y,1.09),(.535,y,1.09),.052,CHROME,N=32)
    tube('HU_DialFace_'+str(y),(.532,y,1.09),(.528,y,1.09),.043,DARK,N=32)
    path('HU_DialNeedle_'+str(y),[(.526,y,1.09),(.526,y+.018,1.112)],.0018,WHITE)
text('HU_DashRadio','HURRICANE',(.532,-.20,1.11),.040,WHITE,(pi/2,0,-pi/2))
box('HU_RiserPocket',(.04,0,.55),(.58,.36,.08),BLACK,.018)
PLATFORM=empty('HU_GunnerFootPlatform',(.04,0,.58),LIFT);drive(PLATFORM,'location',2,'.58+.47*p',[('p',ROOT,'_roofgun')]);box('HU_GunnerPlatformTop',(.04,0,.59),(.56,.36,.035),BRUSH,.018,PLATFORM)
for y in [-.12,0,.12]:path('HU_PlatformGrip_'+str(y),[(-.20,y,.613),(.28,y,.613)],.008,RUBBER,PLATFORM)
# Running gear: actual persistent six tires, with retracted central wheel pockets outside the cabin floor.
CURRENT=FRAME;PARENT=ROOT;GROUP='lower_chassis'
for y in [-.48,.48]:box('HU_LowerFrameRail_'+str(y),(0,y,.42),(4.20,.11,.15),BLACK,.012)
for x in [-1.48,0,1.48]:tube('HU_Axle_'+str(x),(x,-.83,.38),(x,.83,.38),.045,BLACK)
box('HU_Transmission',(0,0,.36),(.80,.62,.27),BLACK,.04)
CENTRE=empty('HU_CentreAxleRetract',(0,0,.81),ROOT);drive(CENTRE,'location',2,'.81-.43*l',[('l',ROOT,'_lift')])
def wheel(name,x,y,z,root):
    N=80;v=[];f=[];w=.23
    profile=[(-w/2,.22),(-w/2,.31),(-w*.43,.367),(-w*.28,.38),(w*.28,.38),(w*.43,.367),(w/2,.31),(w/2,.22)]
    for yy,r in profile:v.extend((x+r*cos(i*2*pi/N),y+yy,z+r*sin(i*2*pi/N)) for i in range(N))
    for j in range(len(profile)):f.extend((j*N+i,j*N+(i+1)%N,((j+1)%len(profile))*N+(i+1)%N,((j+1)%len(profile))*N+i) for i in range(N))
    mesh(name+'_Tire',v,f,RUBBER,root,True);sg=1 if y>0 else -1;outer=y+sg*(w/2+.006)
    tube(name+'_RimBarrel',(x,y-w/2,z),(x,y+w/2,z),.245,BRUSH,root=root)
    tube(name+'_RimLip',(x,outer-sg*.008,z),(x,outer+sg*.008,z),.252,CHROME,root=root)
    tube(name+'_RimRecess',(x,outer+sg*.009,z),(x,outer+sg*.011,z),.217,DARK,root=root)
    for j in range(5):
        a=j*2*pi/5;path(name+'_Spoke_'+str(j),[(x+.055*cos(a),outer+sg*.018,z+.055*sin(a)),(x+.20*cos(a+.17),outer+sg*.018,z+.20*sin(a+.17))],.025,CHROME,root)
    tube(name+'_Hub',(x,outer,z),(x,outer+sg*.036,z),.070,CHROME,root=root)
    vv=[];ff=[]
    for row in range(3):
        for i in range(52):
            a=2*pi*(i+(row%2)*.5)/52;off=len(vv)
            for da,dy,dr in [(-.044,-.027,-.006),(-.044,-.027,.010),(-.044,.027,-.006),(-.044,.027,.010),(.044,-.027,-.006),(.044,-.027,.010),(.044,.027,-.006),(.044,.027,.010)]:vv.append((x+(.38+dr)*cos(a+da),y+(row-1)*.065+dy,z+(.38+dr)*sin(a+da)))
            ff.extend(tuple(off+k for k in face) for face in [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)])
    mesh(name+'_Tread',vv,ff,RUBBER,root,False)
for ax,x in [('Front',1.48),('Rear',-1.48),('Centre',0)]:
    for sg,side in [(1,'L'),(-1,'R')]:
        GROUP='wheel_'+ax+'_'+side;wheel('HU_'+ax+'Wheel_'+side,x,sg*.82,.81 if ax=='Centre' else .38,CENTRE if ax=='Centre' else ROOT)
for x in [-1.48,1.48]:
    for sg in [-1,1]:
        GROUP='suspension';tube('HU_ShockOuter_'+str((x,sg)),(x,sg*.62,.39),(x,sg*.62,.56),.048,BLACK)
        rod=empty('HU_ShockExtension_'+str((x,sg)),(x,sg*.62,.52),ROOT);drive(rod,'scale',2,'1+2.9*l',[('l',ROOT,'_lift')]);tube('HU_ShockChrome_'+str((x,sg)),(x,sg*.62,.52),(x,sg*.62,.72),.025,CHROME,root=rod)
# Roof-mounted twin gun, counter-rotated to remain horizontal as the roof rises.
CURRENT=WEAPONS;PARENT=LIFT;GROUP='roof_gun'
GUNLEVEL=empty('HU_RoofGunLevel',(-.40,0,1.61),ROOF);drive(GUNLEVEL,'rotation_euler',1,'-1.57079632679*r',[('r',ROOT,'_roof')])
box('HU_RoofGunReceiver',(-.39,0,1.61),(.24,.39,.14),MAGENTA,.025,GUNLEVEL)
BARRELS=empty('HU_RoofTwinBarrels',(-.32,0,1.61),GUNLEVEL);drive(BARRELS,'scale',0,'.30+.70*p',[('p',ROOT,'_roofgun')])
for sg in [-1,1]:
    y=sg*.14;tube('HU_RoofCannon_'+str(sg),(-.31,y,1.61),(.27,y,1.61),.044,MAGENTA,root=BARRELS,caps=False)
    for x in [-.23,-.14,-.05,.04,.13,.22]:tube('HU_RoofBarrelBand_'+str((sg,x)),(x-.012,y,1.61),(x+.012,y,1.61),.052,MAGENTA,root=BARRELS,N=24)
    box('HU_RoofMuzzle_'+str(sg),(.29,y,1.61),(.13,.125,.11),MAGENTA,.014,BARRELS)
    tube('HU_RoofMuzzleBore_'+str(sg),(.357,y,1.61),(.36,y,1.61),.033,DARK,root=BARRELS)
    path('HU_RoofGunGrip_'+str(sg),[(-.53,sg*.16,1.61),(-.56,sg*.16,1.55),(-.56,sg*.16,1.46)],.014,BLACK,GUNLEVEL)
# Left windshield hatch, kept as a real moving part rather than hiding the glass.
GROUP='windshield_hatch';base=wind(.34,.16);HATCH=empty('HU_WindshieldHatchHinge',base,LIFT);drive(HATCH,'rotation_euler',2,'-1.65*min(1,w/.45)',[('w',ROOT,'_wind')])
patch('HU_WindshieldCannonCover',[.34,.72],[.16,.78],wind,BLACK,root=HATCH,sub=0,thick=.012,orient=(1,0,.7))
GROUP='windshield_gun';WINDGUN=empty('HU_WindshieldGunSlide',(.15,.53,1.31),LIFT);drive(WINDGUN,'location',0,'.15+.85*min(1,max(0,(w-.42)/.58))',[('w',ROOT,'_wind')])
tube('HU_LeftWindshieldBarrel',(.10,.53,1.31),(.74,.53,1.31),.043,MAGENTA,root=WINDGUN,caps=False)
for x in seq(8,.22,.64):tube('HU_WindshieldBarrelRib_'+str(x),(x-.014,.53,1.31),(x+.014,.53,1.31),.050,MAGENTA,root=WINDGUN,N=24)
tube('HU_WindshieldGunMuzzle',(.72,.53,1.31),(.80,.53,1.31),.057,BLACK,root=WINDGUN,caps=False)
# Headlights telescope as cannons. Lens retracts into a fender pocket before barrels move.
for sg,label in [(1,'L'),(-1,'R')]:
    y=sg*.79;GROUP='body';tube('HU_HeadlightBucket_'+label,(2.22,y,1.00),(2.49,y,1.00),.182,DARK,root=LIFT,caps=False)
    path('HU_HeadlightEyebrow_'+label,[(2.48,y+.189*cos(a),1+.189*sin(a)) for a in seq(48,-.12,pi+.12)],.027,CHROME,LIFT)
    GROUP='lamp_lens';lens=empty('HU_HeadlightLensRetract_'+label,(2.49,y,1.00),LIFT);drive(lens,'location',2,'1-.35*min(1,p/.55)',[('p',ROOT,'_lamps')]);drive(lens,'location',0,'2.49-.16*min(1,p/.55)',[('p',ROOT,'_lamps')]);tube('HU_HeadlightLens_'+label,(2.49,y,1.),(2.495,y,1.),.143,LENS,root=lens)
    GROUP='headlight_gun';gun=empty('HU_HeadlightCannonSlide_'+label,(2.05,y,1.00),LIFT);drive(gun,'location',0,'2.05+.55*min(1,max(0,(p-.55)/.45))',[('p',ROOT,'_lamps')])
    tube('HU_ChromeHeadlightCannon_'+label,(2.04,y,1.),(2.42,y,1.),.126,CHROME,root=gun,caps=False)
    for x in [2.10,2.25,2.40]:tube('HU_HeadlightCannonCollar_'+str((label,x)),(x-.018,y,1),(x+.018,y,1),.143,CHROME,root=gun)
    tube('HU_HeadlightCannonBore_'+label,(2.423,y,1),(2.427,y,1),.092,DARK,root=gun)
# Lower front weapon rack stays on the lower chassis, cleared by the body lift.
GROUP='lower_guns';LOW=empty('HU_LowerFrontGunRack',(1.72,0,.47),ROOT);drive(LOW,'location',0,'1.72+.85*p',[('p',ROOT,'_lower')])
box('HU_LowerGunReceiver',(1.70,0,.47),(.32,1.17,.16),MAGENTA,.025,LOW)
for j,y in enumerate([-.48,0,.48]):
    z=.47 if j!=1 else .39;tube('HU_LowerFrontCannon_'+str(j),(1.73,y,z),(2.20,y,z),.048,MAGENTA,root=LOW,caps=False);box('HU_LowerGunMuzzle_'+str(j),(2.24,y,z),(.14,.15,.12),MAGENTA,.015,LOW);tube('HU_LowerGunBore_'+str(j),(2.313,y,z),(2.317,y,z),.031,DARK,root=LOW)
# Distinct rear horizontal saw disc and spring-launched covered spare.
GROUP='rear_disc';DISC=empty('HU_RearSawSlide',(-2.10,0,.26),ROOT);drive(DISC,'location',0,'-2.10-.86*d',[('d',ROOT,'_disc')]);drive(DISC,'rotation_euler',2,'a*.01745329252',[('a',ROOT,'disc_spin')])
N=96;vv=[]
for z in [.23,.29]:
    for i in range(N):
        a=i*2*pi/N;r=.36 if i%4 in [0,1] else .305;vv.append((-2.10+r*cos(a),r*sin(a),z))
ff=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,N+(i+1)%N,N+i) for i in range(N)];mesh('HU_RearToothedDisc',vv,ff,MAGENTA,DISC,False,bevel=.003)
tube('HU_SawHub',(-2.10,0,.225),(-2.10,0,.30),.10,CHROME,root=DISC)
GROUP='spare';SPARE=empty('HU_SpareEjection',(-2.72,0,.96),LIFT);drive(SPARE,'location',0,'-2.72-4.8*e',[('e',ROOT,'spare_eject')]);drive(SPARE,'location',2,'.96+e-1.56*e*e-.58*l*e',[('e',ROOT,'spare_eject'),('l',ROOT,'_lift')]);drive(SPARE,'rotation_euler',0,'12.5663706144*e',[('e',ROOT,'spare_eject')])
tube('HU_SpareTire',(-2.67,0,.96),(-2.82,0,.96),.355,RUBBER,root=SPARE)
tube('HU_SpareCover',(-2.82,0,.96),(-2.86,0,.96),.382,TEAL,r2=.361,N=80,root=SPARE)
path('HU_SpareChromeRing',[(-2.866,.356*cos(a),.96+.356*sin(a)) for a in seq(96,0,2*pi)],.009,CHROME,SPARE)
path('HU_SpareCoverV',[(-2.87,-.17,1.03),(-2.87,0,.93),(-2.87,.17,1.03)],.012,TEAL,SPARE)
GROUP='body';tube('HU_SpareSocket',(-2.56,0,.96),(-2.69,0,.96),.105,BLACK,root=LIFT)
# Clearly lit studio, with readable tinted glass rather than white opaque panes.
CURRENT=STUDIO;PARENT=None;GROUP='studio';FLOOR=material('HU_StudioFloor',(.105,.12,.13),0,.73)
box('HU_ReviewFloor',(0,0,-.08),(200,200,.10),FLOOR,.005)
world=bpy.data.worlds.new('HU_Daylight');world.use_nodes=True;S.world=world;bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.48,.55,.62,1);bg.inputs[1].default_value=.75
ld=bpy.data.lights.new('HU_Sun','SUN');ld.energy=2.8;ld.angle=.18;o=bpy.data.objects.new(ld.name,ld);STUDIO.objects.link(o);o.rotation_euler=(.45,-.55,-.6)
for name,pos,power,size,target in [('Key',(3,-4,7),1100,4,(0,0,1)),('SoftFill',(0,5,5),950,5,(0,0,1)),('Rim',(-4,-1,5),1100,3,(0,0,1))]:
    ld=bpy.data.lights.new('HU_'+name,'AREA');ld.energy=power;ld.shape='DISK';ld.size=size;o=bpy.data.objects.new(ld.name,ld);STUDIO.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
cd=bpy.data.cameras.new('HU_ReviewCamera');camera=bpy.data.objects.new(cd.name,cd);STUDIO.objects.link(camera);camera.location=(8.3,-8,4.8);camera.rotation_euler=(Vector((0,0,1.0))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=52;S.camera=camera
S.render.engine='CYCLES';S.cycles.samples=24;S.cycles.use_denoising=True;S.cycles.device='GPU';S.render.resolution_x=1300;S.render.resolution_y=900;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';S.view_settings.view_transform='AgX';S.view_settings.exposure=.15;S.render.fps=30;S.frame_start=1;S.frame_end=241
for key,keys in [('battle_mode',[(1,0),(31,0),(151,1),(241,1)]),('spare_eject',[(1,0),(171,0),(211,1),(241,1)])]:
    for frame,value in keys:ROOT[key]=float(value);ROOT.keyframe_insert(data_path='["'+key+'"]',frame=frame)
action=ROOT.animation_data.action
try:curves=list(action.fcurves)
except Exception:curves=[f for layer in action.layers for strip in layer.strips if hasattr(strip,'channelbags') for bag in strip.channelbags for f in bag.fcurves]
for f in curves:
    for p in f.keyframe_points:p.interpolation='LINEAR'
for name,frame in [('ROUTE',1),('LEVAGE',45),('TOIT OUVERT',100),('DEFENSE',151),('ROUE EJECTEE',211)]:S.timeline_markers.new(name,frame=frame)
for o in S.objects:
    if o.animation_data:
        for f in o.animation_data.drivers:f.driver.expression+=' + 0.0'
    o.update_tag()
S.frame_set(151);S.frame_set(1);bpy.context.view_layer.update()
bad=[o.name+':'+f.data_path for o in S.objects if o.animation_data for f in o.animation_data.drivers if not f.driver.is_valid]
(A/'vehicle_build_v1.json').write_text(json.dumps({'objects':len(S.objects),'invalid_drivers':bad,'reference_review':'docs/art/Hurricane_reference_review_v1.md','estimated_dimensions':True,'phase':'Vehicle surfacing and mechanisms; paint graphics and Hondo to follow visual silhouette inspection.'},indent=2))
assert not bad,bad
S['asset']='Hurricane V1';S['interpretation']='Supplied photographs and toy transformation video inspected. Dimensions and hidden engineering estimated.'
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Hurricane_V1_Assembly.blend'),compress=True);print('HURRICANE_V1_VEHICLE_BUILT',len(S.objects))
