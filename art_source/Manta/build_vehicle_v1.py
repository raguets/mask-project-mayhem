"""Execute only through the installed Blender MCP session. +X forward, metres."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Manta';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
assert not (A/'Manta_V1_Vehicle.blend').exists()
for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
CURRENT=collection('Manta_Vehicle');GROUP='Manta';PARENT=None
purple=material('MA_PlumMetallic',(.23,.012,.30),.52,.29)
edge=material('MA_PurpleTrim',(.10,.008,.15),.40,.32)
black=material('MA_BlackRubber',(.009,.012,.017),.06,.48)
metal=material('MA_WingGunmetal',(.16,.21,.24),.72,.35)
chrome=material('MA_Alloy',(.48,.55,.60),.85,.24)
lime=material('MA_LimeGraphics',(.66,.82,.045),.24,.33)
red=material('MA_WeaponRed',(.68,.015,.025),.3,.31)
amber=material('MA_AmberLamps',(.95,.22,.008),.15,.24)
lamp=material('MA_HeadlightLens',(.59,.72,.80),.28,.19)
tail=material('MA_RedTailLens',(.44,.005,.013),.2,.25)
glass=material('MA_SmokedGlass',(.07,.12,.16),.08,.12)
bs=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Transmission Weight'].default_value=.92;bs.inputs['IOR'].default_value=1.46
seatmat=material('MA_CabinLeather',(.021,.025,.035),0,.66)
root=empty('Manta_Control');PARENT=root
for k,v in {'transform':0.,'door_open':0.,'mask_on':False,'driver_pose':1.}.items():root[k]=v
root.id_properties_ui('transform').update(min=0,max=1)
root.id_properties_ui('door_open').update(min=0,max=1)
root['vehicle_category']='road_airplane';root['flight_rule']='Forward flight required; no stationary hover. Asset intent, not gameplay validation.'
root['reference_basis']='Fiche transformation read first; original Kenner Manta toy photographs are mechanism reference. Supplied Nissan 300ZX Z31 photographs guide full-scale surface proportions.'
root['scale_note']='Estimated 4.40m road length, 1.82m width, 1.30m roof; not official dimensions. Hidden pivots and cabin interpreted.'
root['interpretation_authorized']='General authorization 2026-11-13: realistic characters and unseen cockpits.'
def motion(o,prop,i,expr):return drive(o,prop,i,expr,[('t',root,'transform')])
def prism(name,poly,z,h,mat,parent=None):
 n=len(poly);v=[(x,y,z+q*h/2) for q in [-1,1] for x,y in poly]
 return mesh(name,v,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],mat,parent,bevel=.009)
def loft(name,sections,mat,root=None):
 vv=[]
 for x,w,lo,hi in sections:vv.extend([(x,-w*.87,lo),(x,w*.87,lo),(x,w,lo+.055),(x,w,hi-.045),(x,w*.90,hi),(x,-w*.90,hi),(x,-w,hi-.045),(x,-w,lo+.055)])
 n=len(sections);ff=[tuple(reversed(range(8))),tuple((n-1)*8+i for i in range(8))]+[(j*8+i,j*8+(i+1)%8,(j+1)*8+(i+1)%8,(j+1)*8+i) for j in range(n-1) for i in range(8)]
 return mesh(name,vv,ff,mat,root,bevel=.017)
body=loft('MA_MainBody',[(-2.15,.76,.25,.73),(-1.9,.86,.25,.82),(-1.3,.89,.25,.88),(-.4,.88,.24,.84),(.6,.87,.24,.84),(1.4,.88,.24,.76),(2.13,.79,.28,.64)],purple)
def subtract(o,cut,name):
 m=o.modifiers.new(name,'BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cut
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cut,do_unlink=True)
# True open cabin with floor, rather than a solid block beneath the glass.
subtract(body,box('TempCabin',(-.36,0,1.14),(1.85,1.40,1.38),None,0),'CabinWell')
# Central hood well: moving hood reveals weapons, persistent dark structure below.
subtract(body,box('TempHood',(1.45,0,.94),(1.49,1.29,.75),None,0),'SlidingHoodWell')
for x in [1.24,-1.24]:
 subtract(body,tube('TempArch',(x,-1.1,.32),(x,1.1,.32),.335,None,N=64),'WheelArch')
box('MA_CabinFloor',(-.38,0,.40),(1.91,1.40,.07),black)
box('MA_Underbody',(-.2,0,.29),(3.72,1.29,.10),black)
box('MA_WeaponBayFloor',(1.4,0,.47),(1.55,1.27,.07),black)
box('MA_FrontBumper',(2.15,0,.35),(.13,1.65,.16),purple,.035)
box('MA_FrontIntake',(2.222,0,.37),(.012,.91,.075),black,.006)
for s in [-1,1]:
 box('MA_Rocker_'+str(s),(-.1,s*.85,.29),(2.0,.065,.10),edge,.02)
 # Panel relief around actual arch contour.
 for x in [1.24,-1.24]:
  pts=[(x+.347*math.cos(a),s*.892,.32+.347*math.sin(a)) for a in seq(40,0,pi)]
  path('MA_ArchLip',pts,.016,purple)
 box('MA_DoorBody_'+str(s),(-.15,s*.875,.62),(1.30,.028,.35),purple,.014)
 box('MA_DoorHandle_'+str(s),(-.66,s*.901,.79),(.13,.015,.035),black,.007)
 # Two lime stripes and the crossing Z graphic, on the actual external door skin.
 for zz in [.39,.44]:path('MA_LimeSideStripe',[(-1.04,s*.904,zz),(.78,s*.904,zz)],.009,lime)
 path('MA_ZGraphic',[(-.88,s*.906,.385),(-.43,s*.906,.52),(.02,s*.906,.385),(.49,s*.906,.52),(.73,s*.906,.52)],.011,lime)
 # C pillars and side quarter window, triangular on the reference car.
 pts=[(-.93,s*.70,1.26),(-1.87,s*.79,.86),(-.92,s*.85,.86)]
 o=mesh('MA_QuarterGlass_'+str(s),pts,[(0,1,2)],glass)
 o.modifiers.new('GlassThickness','SOLIDIFY').thickness=.006
 path('MA_QuarterWindowFrame',pts+[pts[0]],.035,purple)
 path('MA_Apillar',[(.69,s*.75,.86),(.02,s*.65,1.29)],.034,purple)
 path('MA_Bpillar',[(-.86,s*.84,.83),(-.86,s*.68,1.29)],.043,purple)
 path('MA_RoofSideRail',[(.02,s*.65,1.29),(-.90,s*.68,1.29),(-1.87,s*.79,.86)],.035,purple)
 # Open side windows as on supplied toy; no fictional fixed glazing sealing access.
 door=empty('MA_DoorHinge_'+str(s),(.56,s*.84,.72),root)
 # door bodies use persistent hinges, currently exact closed position.
 o=bpy.data.objects['MA_DoorBody_'+str(s)];wm=o.matrix_world.copy();o.parent=door;o.matrix_world=wm
 drive(door,'rotation_euler',2,str(-s*1.05)+'*d',[('d',root,'door_open')])
box('MA_TbarRoof',(-.42,0,1.30),(.93,.23,.065),purple,.027)
box('MA_RoofFrontCross',(.015,0,1.285),(.075,1.30,.07),purple,.026)
box('MA_RoofRearCross',(-.89,0,1.285),(.085,1.37,.07),purple,.026)
# Two dark glass T-top panels remain distinct editable parts.
for s in [-1,1]:box('MA_TtopGlass_'+str(s),(-.43,s*.385,1.295),(.79,.48,.014),glass,.025)
wind=[(.69,-.75,.86),(.69,.75,.86),(.02,.65,1.28),(.02,-.65,1.28)]
o=mesh('MA_Windshield',wind,[(0,1,2,3)],glass);o.modifiers.new('LaminatedGlass','SOLIDIFY').thickness=.007
path('MA_WindshieldRubber',wind+[wind[0]],.012,black)
for yy in [-.24,.30]:path('MA_Wiper',[(.69,yy-.10,.876),(.48,yy+.18,1.014)],.007,black)
rear=[(-.94,-.67,1.27),(-.94,.67,1.27),(-1.99,.77,.84),(-1.99,-.77,.84)]
o=mesh('MA_RearHatchGlass',rear,[(0,1,2,3)],glass);o.modifiers.new('GlassThickness','SOLIDIFY').thickness=.006
path('MA_HatchSurround',rear+[rear[0]],.035,purple)
for i in range(13):
 t=i/12;x=-.98-1.0*t;z=1.255-.415*t;w=.66+.105*t
 path('MA_RearLouvre_%02d'%i,[(x,-w,z),(x,w,z)],.014,black)
# Complete front/middle upper hood translates, carrying headlamp faces.
slide=empty('MA_SlidingHood',parent=root);motion(slide,'location',0,'.38*t')
loft('MA_SlidingHoodSkin',[(.74,.63,.68,.835),(1.17,.64,.63,.79),(1.75,.66,.56,.70),(2.12,.65,.53,.63)],purple,slide)
for s in [-1,1]:
 # End lenses, shoulder fairings and recessed cannon barrels.
 mesh('MA_Headlamp_'+str(s),[(2.14,s*.43,.55),(2.14,s*.64,.55),(1.88,s*.64,.68),(1.88,s*.43,.68)],[(0,1,2,3)],lamp,slide,bevel=.008)
 box('MA_HoodRaisedDetail',(1.07,s*.46,.835),(.20,.11,.045),purple,.009,slide)
 gun=empty('MA_HeadlightCannonTravel_'+str(s),parent=root);motion(gun,'location',0,'.58*t')
 tube('MA_RedHeadlightCannon',(1.70,s*.53,.58),(2.10,s*.53,.58),.044,red,root=gun)
 tube('MA_CannonDarkBore',(2.101,s*.53,.58),(2.108,s*.53,.58),.029,black,root=gun)
 for xx in [1.84,1.91,1.98]:tube('MA_CannonRib',(xx,s*.53,.58),(xx+.025,s*.53,.58),.052,red,root=gun)
miss=empty('MA_TripleLauncherLift',parent=root);motion(miss,'location',2,'.27*t')
box('MA_TripleLauncherCassette',(.88,0,.57),(.40,.43,.14),metal,.018,miss)
for yy in [-.135,0,.135]:
 tube('MA_MissileGuide',(.67,yy,.64),(.97,yy,.64),.055,black,root=miss)
 tube('MA_PersistentMissile',(.72,yy,.645),(1.08,yy,.645),.034,metal,root=miss)
 tube('MA_MissileRedTip',(1.08,yy,.645),(1.14,yy,.645),.034,red,r2=.007,root=miss)
# Front wheel rolls into the fender; its underside carries a small gun-wing.
def wheel(name,x,y,z,parent):
 tube(name+'_Tire',(x,y-.105,z),(x,y+.105,z),.296,black,N=64,root=parent)
 for side in [-1,1]:
  tube(name+'_Rim',(x,y+side*.106,z),(x,y+side*.112,z),.213,chrome,N=48,root=parent)
  tube(name+'_DarkRimInset',(x,y+side*.114,z),(x,y+side*.118,z),.168,black,N=48,root=parent)
  tube(name+'_Hub',(x,y+side*.119,z),(x,y+side*.123,z),.057,chrome,N=32,root=parent)
  for i in range(8):
   a=i*2*pi/8;b=a+.15
   mesh(name+'_AlloySpoke',[(x+.05*cos(a),y+side*.124,z+.05*sin(a)),(x+.185*cos(a),y+side*.124,z+.185*sin(a)),(x+.185*cos(b),y+side*.124,z+.185*sin(b)),(x+.05*cos(b+.2),y+side*.124,z+.05*sin(b+.2))],[(0,1,2,3)],chrome,parent)
 for i in range(40):
  a=i*2*pi/40
  path(name+'_Tread',[(x+.297*cos(a),y-.084,z+.297*sin(a)),(x+.298*cos(a+.025),y,z+.298*sin(a+.025)),(x+.297*cos(a),y+.084,z+.297*sin(a))],.003,metal,parent)
for s in [-1,1]:
 flip=empty('MA_FrontWheelFlip_'+str(s),(1.24,s*.80,.34),root);motion(flip,'rotation_euler',0,str(s*pi)+'*t')
 wheel('MA_FrontWheel_'+str(s),1.24,s*.83,.32,flip)
 # Local rigid plate begins inboard of the front wheel; its half-turn exposes it.
 prism('MA_FrontGunWing_'+str(s),[(1.55,s*.66),(.99,s*.66),(.96,s*.49),(1.38,s*.47)],.32,.055,metal,flip)
 tube('MA_FrontWingWeapon',(1.03,s*.57,.29),(1.65,s*.57,.29),.027,metal,root=flip)
 wing=empty('MA_UnderbodyWingPivot_'+str(s),(-1.48,s*.56,.24),root)
 motion(wing,'rotation_euler',2,str(s*pi/2)+'*t')
 # Folded blade points forward under the body; aft pivot swings it laterally.
 poly=[(-1.40,s*.60),(1.70,s*.60),(1.62,s*.82),(-1.20,s*1.02)]
 prism('MA_MainWing_'+str(s),poly,.24,.065,metal,wing)
 for xx in [-.7,.2,1.1]:path('MA_WingPanelLine',[(xx,s*.625,.276),(xx,s*(.91-(xx+.7)*.045),.276)],.003,black,wing)
 path('MA_AileronSeam',[(-1.11,s*.97,.277),(1.49,s*.81,.277)],.004,black,wing)
 # These markings remain on the same wing through its full sweep.
 text('MA_WingVENOM','VENOM',(1.03,s*.70,.28),.105,lime,rot=(0,0,pi/2 if s==1 else -pi/2),root=wing)
 carrier=empty('MA_RearWheelCarrier_'+str(s),(-1.24,s*.83,.32),wing)
 motion(carrier,'rotation_euler',2,str(-s*pi/2)+'*t')
 wheel('MA_RearWheel_'+str(s),-1.24,s*.83,.32,carrier)
 tube('MA_WingTipGun',(1.49,s*.83,.25),(1.88,s*.83,.25),.027,metal,root=wing)
# Rear light-bearing face rises as one rigid spoiler assembly.
tailhinge=empty('MA_RearLightSpoilerHinge',(-2.01,0,.83),root);motion(tailhinge,'rotation_euler',1,'1.40*t')
box('MA_RearLightPanel',(-2.12,0,.67),(.075,1.55,.31),purple,.018,tailhinge)
for s in [-1,1]:
 box('MA_TailRed',(-2.162,s*.53,.71),(.012,.32,.105),tail,.009,tailhinge)
 box('MA_TailAmber',(-2.164,s*.727,.71),(.013,.065,.105),amber,.006,tailhinge)
 box('MA_TailReverse',(-2.165,s*.33,.71),(.013,.07,.105),lamp,.005,tailhinge)
 for z in [.68,.71,.74]:path('MA_LensRibs',[(-2.173,s*.39,z),(-2.173,s*.67,z)],.003,chrome,tailhinge)
box('MA_SpoilerTop',(-2.075,0,.86),(.22,1.71,.055),purple,.018,tailhinge)
engine=empty('MA_TripleReactorTravel',parent=root);motion(engine,'location',0,'-.44*t')
box('MA_ReactorCassette',(-1.80,0,.53),(.51,1.0,.24),black,.025,engine)
for yy in [-.30,0,.30]:
 tube('MA_ReactorBody',(-1.60,yy,.54),(-2.02,yy,.54),.125,metal,root=engine)
 tube('MA_NozzleOuter',(-2.02,yy,.54),(-2.10,yy,.54),.144,chrome,root=engine)
 tube('MA_NozzleInner',(-2.104,yy,.54),(-2.11,yy,.54),.107,black,root=engine)
 for i in range(10):
  a=i*2*pi/10;tube('MA_ReactorRidge',(-1.75,yy+.128*cos(a),.54+.128*sin(a)),(-2.04,yy+.128*cos(a),.54+.128*sin(a)),.009,metal,root=engine)
box('MA_RearBumper',(-2.18,0,.32),(.11,1.62,.13),purple,.025)
text('MA_RearPlate','MANTA',(-2.243,0,.30),.075,lime,rot=(pi/2,0,-pi/2))
# Interpreted interior, two seats, practical contacts in the same coordinate system.
CURRENT=collection('Manta_Interior');PARENT=root
for s in [-1,1]:
 box('MA_SeatBase_'+str(s),(-.48,s*.37,.50),(.53,.49,.13),seatmat,.06)
 o=box('MA_SeatBack_'+str(s),(-.86,s*.37,.78),(.13,.48,.55),seatmat,.05);o.rotation_euler[1]=-.15
 box('MA_Headrest_'+str(s),(-.93,s*.37,1.08),(.12,.27,.18),seatmat,.04)
 for yy in [-.15,0,.15]:path('MA_SeatStitch',[(-.54,s*.37+yy,.568),(-.80,s*.37+yy,.568)],.002,metal)
box('MA_Dashboard',(.40,0,.77),(.32,1.33,.19),seatmat,.035)
box('MA_InstrumentCluster',(.31,-.36,.84),(.06,.39,.13),black,.02)
for yy in [-.46,-.29]:
 tube('MA_InstrumentBezel',(.272,yy,.85),(.260,yy,.85),.055,chrome)
 tube('MA_InstrumentFace',(.259,yy,.85),(.253,yy,.85),.047,black)
path('MA_SteeringColumn',[(.36,-.37,.70),(.06,-.37,.85)],.022,black)
center=Vector((.06,-.37,.85));normal=Vector((-.88,0,.47)).normalized();q=normal.to_track_quat('Z','Y')
pts=[tuple(center+q@Vector((.155*cos(a),.155*sin(a),0))) for a in seq(64,0,2*pi)]
path('MA_SteeringWheel',pts,.014,black)
for a in [0,2*pi/3,4*pi/3]:path('MA_WheelSpoke',[tuple(center),tuple(center+q@Vector((.14*cos(a),.14*sin(a),0)))],.010,chrome)
box('MA_Console',(-.15,0,.55),(.66,.17,.25),seatmat,.03)
path('MA_Shifter',[(-.12,0,.68),(-.08,0,.80)],.014,metal)
for yy in [-.48,-.30]:box('MA_Pedal',(.53,yy,.46),(.10,.09,.025),black,.006)
# Reproducible control timeline: all primary mechanisms share transform.
for f,t in [(1,0),(121,1),(161,1),(281,0)]:root['transform']=t;root.keyframe_insert(data_path='["transform"]',frame=f)
if root.animation_data and root.animation_data.action:
 for fc in root.animation_data.action.fcurves if hasattr(root.animation_data.action,'fcurves') else []:
  for kp in fc.keyframe_points:kp.interpolation='LINEAR'
S.frame_start=1;S.frame_end=281;S.frame_set(1)
CURRENT=collection('Manta_Studio');PARENT=None
floor=box('MA_StudioFloor',(0,0,-.075),(200,200,.10),material('MA_StudioSlate',(.075,.10,.13),.05,.65),0)
for name,pos,power,size in [('Key',(4,-5,7),1800,6),('Fill',(0,5,4),1500,5),('Rim',(-5,-1,6),2200,5)]:
 ld=bpy.data.lights.new('MA_'+name,'AREA');ld.energy=power;ld.shape='DISK';ld.size=size;o=bpy.data.objects.new('MA_'+name,ld);CURRENT.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,.6))-o.location).to_track_quat('-Z','Y').to_euler()
camd=bpy.data.cameras.new('Manta_ReviewCamera');cam=bpy.data.objects.new('Manta_ReviewCamera',camd);CURRENT.objects.link(cam);S.camera=cam;cam.location=(6,-7,4);cam.rotation_euler=(Vector((0,0,.6))-cam.location).to_track_quat('-Z','Y').to_euler();camd.lens=53
S.render.engine='CYCLES';S.cycles.samples=24;S.world.color=(.24,.24,.24)
prefs=bpy.context.preferences.addons['cycles'].preferences
try:
 prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type!='CPU'
 S.cycles.device='GPU'
except Exception:S.cycles.device='CPU'
S.view_settings.view_transform='AgX';S.render.resolution_x=1200;S.render.resolution_y=900;S.render.resolution_percentage=100
for ar in bpy.context.screen.areas:
 if ar.type=='VIEW_3D':ar.spaces.active.shading.type='MATERIAL'
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Manta_V1_Vehicle.blend'))
print('MANTA_V1_VEHICLE_SAVED',len(bpy.data.objects))
