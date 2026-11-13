"""Run in the installed Blender MCP session. Reference-led Switchblade V1."""
import bpy, math, json
from pathlib import Path
from mathutils import Vector, Matrix
P=Path('G:/DEV/mask-project-mayhem'); A=P/'art_source/Switchblade'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
assert not (A/'Switchblade_V1_Vehicle.blend').exists(), 'Preserve existing V1'
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Session_before_Switchblade.blend'),copy=True)
for o in list(bpy.data.objects): bpy.data.objects.remove(o,do_unlink=True)
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
CURRENT=collection('Switchblade_Vehicle'); PARENT=None; GROUP='Switchblade'
navy=material('SB_DeepNavyPaint',(.016,.043,.095),.48,.29)
edge=material('SB_EdgeBlue',(.032,.085,.16),.42,.30)
black=material('SB_BlackMechanism',(.009,.014,.023),.45,.35)
silver=material('SB_Chrome',(.46,.54,.60),.86,.22)
orange=material('SB_OrangeMarkings',(.90,.115,.008),.20,.34)
red=material('SB_RedMarkings',(.48,.009,.035),.25,.34)
glass=material('SB_MagentaCanopy',(.34,.008,.10),.04,.11)
bs=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Transmission Weight'].default_value=.88;bs.inputs['IOR'].default_value=1.46
seatmat=material('SB_OrangeSeat',(.57,.065,.009),0,.60)
root=empty('Switchblade_Control');PARENT=root
for k,v in {'transform':0.,'rotor_angle':0.,'canopy_open':0.,'hover_height':0.}.items():
 root[k]=v;root.id_properties_ui(k).update(min=0,max=1 if k in ['transform','canopy_open'] else 100)
root['vehicle_category']='helicopter_airplane'
root['mode_0']='Helicopter: stationary hover and ground landing permitted'
root['mode_1']='Airplane: sustained forward flight required, NO stationary hover'
root['reference_basis']='Supplied original-type toy photographs; modern reissue and cartoon compared separately. Fiche read first.'
root['scale_note']='Estimated adult scale: 7.15m fuselage; not official dimensions. Hidden pivots/cockpit details interpreted.'
root['interpretation_authorized']='2026-11-13: general realistic character and cockpit interpretation authorized by user.'
drive(root,'location',2,'h',[('h',root,'hover_height')])

def polyprism(name,pts,z,thick,mat,parent=None):
 v=[(x,y,z+dz) for dz in [-thick/2,thick/2] for x,y in pts];N=len(pts)
 f=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
 return mesh(name,v,f,mat,parent,bevel=.012)

def loft(name,sections,mat):
 # octagonal/chamfered sections: planar toy-derived skin rather than tubular tail
 vv=[];ff=[]
 for x,w,lo,hi in sections:
  vv += [(x,-w*.72,lo),(x,w*.72,lo),(x,w,lo+.12),(x,w,hi-.10),(x,w*.72,hi),(x,-w*.72,hi),(x,-w,hi-.10),(x,-w,lo+.12)]
 for j in range(len(sections)-1):
  for i in range(8):ff.append((j*8+i,j*8+(i+1)%8,(j+1)*8+(i+1)%8,(j+1)*8+i))
 ff += [tuple(reversed(range(8))),tuple((len(sections)-1)*8+i for i in range(8))]
 return mesh(name,vv,ff,mat,bevel=.035)

loft('SB_FuselageLower',[(-4.05,.10,1.72,1.99),(-3.65,.22,1.60,2.03),(-1.25,.59,.95,2.12),(-.35,.67,.95,2.16),(.10,.71,.95,1.62),(1.65,.62,1.06,1.47),(2.65,.36,1.30,1.49),(3.1,.10,1.40,1.48)],navy)
# Remove the covered cockpit from the upper body: lower skin has an open well.
# A separate rim/floor closes the cabin without placing a solid block in the pilot.
body=bpy.data.objects['SB_FuselageLower']
cut=box('SB_TemporaryCockpitCut',(1.02,0,1.74),(2.12,1.04,1.12),None,.0,root)
mod=body.modifiers.new('CockpitWell','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut
bpy.context.view_layer.objects.active=body
bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
box('SB_CockpitFloor',(1.05,0,1.20),(2.08,1.02,.08),black,.025)
box('SB_CockpitRearBulkhead',(-.035,0,1.81),(.08,1.03,1.15),navy,.025)

# Faceted canopy, same perimeter as the supplied open-cockpit photograph.
canopy=empty('SB_CanopyHinge',(-.08,0,2.35),root)
drive(canopy,'rotation_euler',1,'-1.4*c',[('c',root,'canopy_open')])
sections=[(2.50,.32,1.51,1.60),(2.12,.48,1.53,1.94),(.65,.59,1.58,2.56),(.08,.51,1.62,2.64)]
vv=[];ff=[]
for x,w,z,top in sections:vv += [(x,-w,z),(x,-w*.64,top-.035),(x,w*.64,top-.035),(x,w,z)]
for j in range(3):
 for k in range(3):ff.append((j*4+k,(j+1)*4+k,(j+1)*4+k+1,j*4+k+1))
ff += [(0,1,2,3),(12,13,14,15)]
o=mesh('SB_MagentaFacetedGlazing',vv,ff,glass,canopy,bevel=.014);o.modifiers.new('GlazingThickness','SOLIDIFY').thickness=.008
for k in [0,3]:path('SB_CanopySill',[(x,(-1 if k==0 else 1)*w,z) for x,w,z,top in sections],.018,edge,canopy)
path('SB_CanopyRearFrame',[vv[12],vv[13],vv[14],vv[15]],.022,navy,canopy)
path('SB_CanopyCenterSeam',[(x,0,top-.03) for x,w,z,top in sections],.007,edge,canopy)

for s in [-1,1]:
 polyprism('SB_FixedCockpitChine_'+str(s),[(2.60,s*.28),(2.00,s*.68),(.05,s*.98),(-.25,s*.66)],1.49,.065,navy)
 polyprism('SB_ChineFlash_'+str(s),[(.20,s*.83),(.68,s*.76),(.49,s*.86)],1.527,.005,orange)
 tube('SB_FrontChromePort',(2.03,s*.61,1.44),(2.27,s*.48,1.44),.055,silver,r2=.027)
 # square shoulder recess and retracting gun, slight forward/outward deployment
 box('SB_GunHousing_'+str(s),(.14,s*.74,1.95),(.53,.21,.28),navy,.025)
 gun=empty('SB_SideGunSlide_'+str(s),(.10,s*.75,1.95),root)
 drive(gun,'location',1,str(s)+'*(0.75+0.20*t)',[('t',root,'transform')])
 drive(gun,'location',0,'0.10+0.44*t',[('t',root,'transform')])
 tube('SB_CockpitCannon_'+str(s),(-.02,s*.75,1.95),(.32,s*.75,1.95),.063,silver,root=gun)
 tube('SB_CockpitCannonBore_'+str(s),(.321,s*.75,1.95),(.331,s*.75,1.95),.039,black,root=gun)
 for i in range(5):box('SB_GunCoolingRib',(.0+i*.045,s*.75,1.95),(.018,.16,.17),edge,.003,gun)

# Folding wings: yaw forward AND roll down from their vertical storage against tail sides.
for s in [-1,1]:
 yaw=empty('SB_WingSweep_'+str(s),(-.55,s*.70,1.45),root)
 roll=empty('SB_WingFold_'+str(s),(-.55,s*.70,1.45),yaw)
 # Geometry is built at the final position; local matrices are normalized after parenting.
 for obj in [yaw,roll]:obj.rotation_mode='XYZ'
 wingpts=[(.22,s*.73),(.10,s*1.35),(-.82,s*3.30),(-1.16,s*3.33),(-1.45,s*.74)]
 polyprism('SB_MainWing_'+str(s),wingpts,1.45,.075,navy,roll)
 polyprism('SB_WingOrangeFlash_'+str(s),[(.00,s*1.04),(-.16,s*1.70),(-.75,s*2.56),(-.39,s*1.39)],1.492,.005,orange,roll)
 polyprism('SB_WingRedFlash_'+str(s),[(-.19,s*1.25),(-.53,s*1.78),(-.81,s*2.45),(-.57,s*1.63)],1.499,.005,red,roll)
 path('SB_WingPanelLine_'+str(s),[(-.10,s*1.02,1.496),(-.89,s*3.12,1.496),(-1.04,s*3.13,1.496)],.008,edge,roll)
 # Convert roll empty to local origin of yaw (helpers preserve global placement).
 drive(yaw,'rotation_euler',2,str(s)+'*1.57079632679*(1-t)',[('t',root,'transform')])
 drive(roll,'rotation_euler',1,'-1.57079632679*(1-t)',[('t',root,'transform')])
 tube('SB_WingRootBearing',(-.55,s*.66,1.45),(-.55,s*.76,1.45),.16,black)
 # Patins stay persistent; the whole shaped strut pivots up into a wing-mounted cannon.
 skid=empty('SB_SkidToCannon_'+str(s),(-.20,s*.68,1.13),root)
 drive(skid,'rotation_euler',0,str(s)+'*1.57079632679*t',[('t',root,'transform')])
 # solid bent broad strut, no floating supports
 sidepoly=[(.40,s*.70,1.14),(-.32,s*.70,1.14),(-.65,s*.98,.22),(-.43,s*.98,.16),(.55,s*.98,.16),(.27,s*.95,.30),(-.02,s*.76,1.0)]
 o=mesh('SB_BentSkidStrut_'+str(s),sidepoly,[tuple(range(7))],black,skid,bevel=.03);o.modifiers.new('StrutThickness','SOLIDIFY').thickness=.11
 rail=polyprism('SB_LandingSkidCannon_'+str(s),[(-1.25,s*.88),(1.34,s*.88),(1.61,s*.96),(1.38,s*1.08),(-1.32,s*1.08)],.13,.12,black,skid)
 tube('SB_SkidCannonBarrel_'+str(s),(-.92,s*.98,.19),(1.46,s*.98,.19),.052,edge,root=skid)
 tube('SB_SkidCannonSilverTip_'+str(s),(1.45,s*.98,.19),(1.66,s*.98,.19),.065,silver,r2=.05,root=skid)
 tube('SB_SkidCannonBore_'+str(s),(1.662,s*.98,.19),(1.670,s*.98,.19),.031,black,root=skid)
 for i in range(9):box('SB_SkidRailRib',(-.97+i*.24,s*.98,.205),(.025,.14,.022),edge,.004,skid)

# Tail stabilizers, jet nozzle, tail rotor/fin assembly turning UP as a single piece.
for s in [-1,1]:
 polyprism('SB_Tailplane_'+str(s),[(-3.53,s*.13),(-3.76,s*.87),(-4.08,s*.85),(-3.95,s*.11)],1.99,.055,navy)
 polyprism('SB_TailStripe_'+str(s),[(-3.77,s*.35),(-3.90,s*.70),(-3.98,s*.69),(-3.86,s*.34)],2.021,.004,red)
 box('SB_TailVentStrip',(-2.90,s*.30,1.91),(1.05,.025,.085),edge,.005)
 for i in range(12):box('SB_TailVentSlat',(-3.36+i*.082,s*.315,1.91),(.025,.02,.074),black,.002)
tailfin=empty('SB_TailRotorToFin',(-3.73,0,1.97),root)
drive(tailfin,'rotation_euler',0,'3.14159265359*t',[('t',root,'transform')])
v=[(-3.60,-.04,1.94),(-3.88,-.04,1.93),(-3.87,-.04,.72),(-3.53,-.04,.91),(-3.23,-.04,1.93)]
o=mesh('SB_VentralTailRotorFin',v,[(0,1,2,3,4)],navy,tailfin,bevel=.025);o.modifiers.new('TailFinThickness','SOLIDIFY').thickness=.095
path('SB_TailFinOutline',v+[v[0]],.014,edge,tailfin)
tube('SB_TailRotorHousing',(-3.60,-.10,1.74),(-3.60,.10,1.74),.14,black,root=tailfin)
for i in range(5):
 a=i*2*pi/5
 path('SB_TailRotorGrille',[(-3.60+.11*math.cos(a),-.111,1.74+.11*math.sin(a)),(-3.60+.04*math.cos(a),-.111,1.74+.04*math.sin(a))],.011,silver,tailfin)
tube('SB_JetNozzle',(-3.90,0,1.75),(-4.16,0,1.75),.11,black,r2=.145)
tube('SB_JetNozzleLip',(-4.14,0,1.75),(-4.18,0,1.75),.148,edge)

# Two real persistent blades; folding is separate from continuous helicopter rotation.
mast=empty('SB_MainRotorMast',(-.43,0,2.85),root)
drive(mast,'location',2,'2.85-0.38*t',[('t',root,'transform')])
tube('SB_RotorMastSpindle',(-.43,0,2.26),(-.43,0,2.84),.095,black,root=mast)
hub=empty('SB_MainRotorSpin',(-.43,0,2.85),mast)
drive(hub,'rotation_euler',2,'a*(1-t)',[('a',root,'rotor_angle'),('t',root,'transform')])
box('SB_RotorHub',(-.43,0,2.85),(.41,.24,.11),black,.028,hub)
for s in [-1,1]:
 hinge=empty('SB_BladeFold_'+str(s),(-.43,0,2.85+s*.022),hub)
 drive(hinge,'rotation_euler',2,str(s)+'*1.57079632679*(1-t)',[('t',root,'transform')])
 polyprism('SB_MainRotorBlade_'+str(s),[(-.49,-.092),(-3.57,-.09),(-3.64,.042),(-.72,.10)],2.85+s*.022,.027,black,hinge)
 polyprism('SB_BladeTipMark_'+str(s),[(-3.41,-.082),(-3.55,-.082),(-3.59,.035),(-3.45,.04)],2.867+s*.022,.003,edge,hinge)
 tube('SB_BladeRootBolt',(-.43,0,2.82+s*.022),(-.43,0,2.93+s*.022),.047,silver,root=hinge)
for s in [-1,1]:
 polyprism('SB_MastShoulderFin_'+str(s),[(-.04,s*.38),(-.65,s*.60),(-1.25,s*.58),(-.46,s*.34)],2.26,.04,silver)

# Referenced orange cockpit, with restrained interpreted flight controls.
CURRENT=collection('Switchblade_Interior');PARENT=root
box('SB_SeatBase',(.40,0,1.50),(.64,.57,.16),seatmat,.07)
o=box('SB_SeatBack',(.08,0,1.85),(.15,.57,.75),seatmat,.065);o.rotation_euler.y=-.08
box('SB_HeadRest',(.04,0,2.23),(.18,.38,.20),seatmat,.055)
for y in [-.18,-.09,0,.09,.18]:box('SB_SeatUpholsteryRib',(.17,y,1.88),(.025,.023,.56),orange,.009)
box('SB_InstrumentConsole',(1.59,0,1.65),(.30,.86,.32),black,.035)
screen=material('SB_InstrumentGlass',(.015,.12,.11),.35,.21)
for y in [-.26,0,.26]:
 box('SB_InstrumentScreen',(1.427,y,1.72),(.01,.19,.12),screen,.009)
 for i in range(3):tube('SB_ConsoleSwitch',(1.421,y-.06+i*.06,1.61),(1.399,y-.06+i*.06,1.61),.009,silver,N=12)
path('SB_ControlColumn',[(.95,0,1.28),(.97,0,1.61),(1.02,0,1.84)],.024,black)
path('SB_FlightYoke',[(1.02,-.24,1.91),(1.02,-.24,1.83),(1.02,.24,1.83),(1.02,.24,1.91)],.023,black)
for s in [-1,1]:box('SB_RudderPedal',(1.43,s*.19,1.30),(.20,.14,.045),silver,.015)

# Presentation
CURRENT=collection('Switchblade_Studio');PARENT=None
box('Review_Floor',(0,0,-.06),(200,200,.10),material('SB_StudioFloor',(.15,.18,.22),0,.8),0)
s=bpy.context.scene;w=s.world or bpy.data.worlds.new('SB_World');s.world=w;w.use_nodes=True
bg=next(n for n in w.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.50,.57,.68,1);bg.inputs[1].default_value=.6
for n,p,e,sz in [('Key',(5,-6,9),2300,7),('Fill',(0,5,7),2200,6),('Rim',(-6,-1,7),2600,5)]:
 d=bpy.data.lights.new('SB_'+n,'AREA');d.energy=e;d.shape='DISK';d.size=sz;o=bpy.data.objects.new('SB_'+n,d);CURRENT.objects.link(o);o.location=p;o.rotation_euler=(Vector((0,0,1.5))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('SB_ReviewCamera');cam=bpy.data.objects.new('SB_ReviewCamera',d);CURRENT.objects.link(cam);cam.location=(10,-12,7);cam.rotation_euler=(Vector((-.4,0,1.5))-cam.location).to_track_quat('-Z','Y').to_euler();d.lens=55;s.camera=cam
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100
prefs=bpy.context.preferences.addons['cycles'].preferences
try:
 prefs.compute_device_type='OPTIX';prefs.get_devices()
 for dev in prefs.devices:dev.use=dev.type!='CPU'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
s.view_settings.view_transform='AgX';s.frame_end=121
for frame,value in [(1,0.),(121,1.)]:root['transform']=value;root.keyframe_insert(data_path='["transform"]',frame=frame)
s.frame_set(1);root['transform']=0.;root.update_tag();bpy.context.view_layer.update()
bpy.ops.object.select_all(action='DESELECT');root.select_set(True);bpy.context.view_layer.objects.active=root
for screen in bpy.data.screens:
 for ar in screen.areas:
  if ar.type=='VIEW_3D':ar.spaces.active.region_3d.view_distance=11;ar.spaces.active.region_3d.view_location=(0,0,1.4)
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Switchblade_V1_Vehicle.blend'),compress=True)
print('SWITCHBLADE_V1_VEHICLE_SAVED',len(bpy.data.objects))
