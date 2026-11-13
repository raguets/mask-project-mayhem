"""Condor, inspected original toy references. Executed inside Blender MCP only."""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
from math import pi,sin,cos
P=Path('G:/DEV/mask-project-mayhem'); A=P/'art_source/Condor'; A.mkdir(parents=True,exist_ok=True)
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Session_before_Condor.blend'),copy=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
C=collection('Condor_Vehicle');CURRENT=C;PARENT=None;GROUP='condor'
green=material('Condor_LimePaint',(.30,.72,.009),.27,.28)
black=material('Condor_Charcoal',(.012,.017,.020),.35,.34)
rubber=material('Condor_TireRubber',(.009,.012,.014),0,.72)
chrome=material('Condor_WheelAlloy',(.44,.49,.52),.85,.22)
glass=material('Condor_SmokeWindshield',(.038,.065,.057),.05,.16)
bs=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Transmission Weight'].default_value=.72;bs.inputs['IOR'].default_value=1.47
yellow=material('Condor_Headlamp',(.75,.75,.38),.25,.22)
root=empty('Condor_Control');PARENT=root
for k,v in {'transform':0.,'rotor_angle':0.,'forward_flight':0.,'hover_height':0.}.items():
 root[k]=v;root.id_properties_ui(k).update(min=0,max=1 if k in ['transform','forward_flight'] else 100)
root['vehicle_category']='road_helicopter';root['flight_braking']='Maximum braking permits stationary hover';root['scale_note']='Estimated adult scale, 2.8m body, not official dimensions'
drive(root,'rotation_euler',1,'0.105*f*t',[('f',root,'forward_flight'),('t',root,'transform')])
drive(root,'location',2,'h',[('h',root,'hover_height')])
def pivot(n,p):return empty(n,p,root)
def torus(n,p,R,r,mat,par):
 vv=[];ff=[];N=72;M=16
 for i in range(N):
  a=2*pi*i/N
  for j in range(M):
   b=2*pi*j/M;vv.append((p[0]+(R+r*cos(b))*sin(a),p[1]+r*sin(b),p[2]+(R+r*cos(b))*cos(a)))
 for i in range(N):
  for j in range(M):ff.append((i*M+j,((i+1)%N)*M+j,((i+1)%N)*M+(j+1)%M,i*M+(j+1)%M))
 return mesh(n,vv,ff,mat,par,True)
front=pivot('Condor_FrontWheel',(1.00,0,.355));rear=pivot('Condor_RearWheelPivot',(-1.04,0,.64))
drive(rear,'rotation_euler',1,'1.83*t',[('t',root,'transform')])
for name,p,par in [('Front',(1,0,.355),front),('Rear',(-.99,0,.355),rear)]:
 torus('Condor_'+name+'_PersistentTire',p,.286,.067,rubber,par)
 for side in [-1,1]:
  torus('Condor_'+name+'_Rim', (p[0],side*.052,p[2]),.235,.016,chrome,par)
  for i in range(3):
   a=2*pi*i/3;tube('Condor_'+name+'_ThreeSpoke', (p[0]+.07*sin(a),side*.058,p[2]+.07*cos(a)),(p[0]+.232*sin(a),side*.058,p[2]+.232*cos(a)),.037,chrome,root=par)
 tube('Condor_'+name+'_Hub',(p[0],-.10,p[2]),(p[0],.10,p[2]),.069,black,root=par)
 for i in range(40):
  a=2*pi*i/40
  for side in [-1,1]:
   tube('Condor_'+name+'_Tread',(p[0]+.346*sin(a-.023),side*.035,p[2]+.346*cos(a-.023)),(p[0]+.346*sin(a+.023),side*.055,p[2]+.346*cos(a+.023)),.008,rubber,root=par,N=8)
for side in [-1,1]:
 tube('Condor_Fork',(1,side*.112,.355),(.80,side*.112,.91),.037,green)
 tube('Condor_ForkPiston',(1,side*.112,.355),(.92,side*.112,.58),.025,chrome)
 tube('Condor_RearSwingArm',(-.54,side*.12,.40),(-.99,side*.12,.355),.039,black,root=rear)
 path('Condor_ChassisRail',[(.85,side*.21,.70),(.54,side*.235,.24),(-.40,side*.235,.24),(-1.28,side*.22,.59)],.047,green)
 box('Condor_Footrest',(.18,side*.27,.28),(.46,.15,.055),black,.015)
box('Condor_Engine',(.05,0,.40),(.58,.30,.25),black,.045)
for i in range(7):box('Condor_CoolingFin',(.03,0,.325+i*.027),(.48,.35,.009),chrome,.003)
# Tail cowl: rounded cross sections, wider at saddle, pointed rear.
def loft(n,sections,mat):
 vv=[];ff=[];N=20
 for x,w,z,h in sections:
  for i in range(N):
   a=2*pi*i/N;vv.append((x,w*sin(a),z+h*cos(a)))
 for j in range(len(sections)-1):
  for i in range(N):ff.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
 ff.extend([tuple(reversed(range(N))),tuple((len(sections)-1)*N+i for i in range(N))]);return mesh(n,vv,ff,mat,smooth=True,bevel=.006)
loft('Condor_RearCowl',[(-1.40,.10,.66,.08),(-1.32,.19,.70,.15),(-.83,.25,.70,.20),(-.48,.255,.70,.19),(-.38,.22,.66,.12)],green)
seat=pivot('Condor_SeatCarriage',(-.17,0,.69));drive(seat,'location',2,'0.69-0.10*t',[('t',root,'transform')])
box('Condor_Saddle',(-.17,0,.715),(.52,.36,.10),black,.047,seat)
for i in range(9):box('Condor_SaddleRib',(-.39+i*.054,0,.767),(.019,.335,.012),rubber,.005,seat)
for side in [-1,1]:
 for i in range(3):box('Condor_TailVent',(-.63-i*.18,side*.249,.73),(.115,.008,.037),black,.01)
 for i in range(2):tube('Condor_TailRoundVent',(-.48,side*.246,.72+i*.10),(-.48,side*.255,.72+i*.10),.026,black)
 text('Condor_Brand','M.A.S.K.',(-.91,side*.253,.59),.072,chrome,(pi/2,0,0) if side==-1 else (pi/2,0,pi))
# Front fairing: true bilateral swept surfaces, open rider recess behind.
for side in [-1,1]:
 sections=[(1.38,.16,.72,.10),(1.28,.27,.82,.14),(1.00,.35,.88,.19),(.70,.36,.89,.19),(.48,.30,.78,.17)]
 vv=[];ff=[];N=9
 for x,w,z,h in sections:
  for i in range(N):
   a=-pi/2+pi*i/(N-1);vv.append((x,side*w*cos(a),z+h*sin(a)))
 for j in range(len(sections)-1):
  for i in range(N-1):ff.append((j*N+i,(j+1)*N+i,(j+1)*N+i+1,j*N+i+1))
 o=mesh('Condor_Fairing_'+str(side),vv,ff,green,smooth=True);m=o.modifiers.new('FairingThickness','SOLIDIFY');m.thickness=.018
 mesh('Condor_BlackSideInset',[(1.30,side*.23,.76),(1.00,side*.347,.80),(.55,side*.32,.79),(.60,side*.318,.70),(1.12,side*.29,.72)],[(0,1,2,3,4)],black,bevel=.009)
 box('Condor_MirrorPod',(.71,side*.36,1.02),(.14,.09,.14),green,.035)
# Windshield rises aft; curved in plan with rounded trapezoidal perimeter.
o=patch('Condor_Windshield',seq(20),seq(24,-1,1),lambda u,v:(1.19-.60*u-.10*(1-v*v),v*(.205+.055*u),.94+.46*u-.025*v*v),glass,thick=.006,sub=1)
path('Condor_WindshieldTop',[ (.59-.10*(1-v*v),v*.26,1.40-.025*v*v) for v in seq(40,-1,1)],.009,black)
box('Condor_HeadlightRecess',(1.379,0,.79),(.025,.22,.115),black,.016)
for side in [-1,1]:box('Condor_Headlight',(1.399,side*.071,.79),(.022,.060,.075),yellow,.009)
gun=pivot('Condor_HeadlampCannon',(1.30,0,.79));drive(gun,'location',0,'1.30+0.23*t',[('t',root,'transform')])
tube('Condor_CannonBarrel',(1.27,0,.79),(1.37,0,.79),.026,black,root=gun)
tube('Condor_CannonMuzzle',(1.367,0,.79),(1.373,0,.79),.018,rubber,root=gun)
box('Condor_InstrumentPanel',(.61,0,.99),(.10,.40,.11),black,.022)
for i in range(3):box('Condor_Display',(.548,-.12+i*.12,1.01),(.004,.085,.049),material('Condor_Display_'+str(i),(.025,.26,.14),.2,.3),.004)
for side in [-1,1]:
 path('Condor_Handlebar',[(.55,side*.10,.95),(.46,side*.24,.97),(.35,side*.29,.96)],.018,chrome)
 tube('Condor_Grip',(.34,side*.29,.96),(.44,side*.29,.96),.025,rubber)
# Pair of side arms pivot together from low seat-rear mount.
mast=pivot('Condor_RotorSupport',(-.46,0,.30));drive(mast,'rotation_euler',1,'1.570796*t',[('t',root,'transform')])
for side in [-1,1]:
 box('Condor_MastArm',(-1.20,side*.30,.32),(1.48,.062,.072),black,.018,mast)
 tube('Condor_MastPivot',(-.46,side*.27,.30),(-.46,side*.35,.30),.093,black,root=mast)
hub=empty('Condor_MainRotorHub',(-1.94,0,.32),mast)
# rotor plane horizontal when mast rises: local YZ plane.
drive(hub,'rotation_euler',0,'a*t',[('a',root,'rotor_angle'),('t',root,'transform')])
tube('Condor_MainRotorSpindle',(-1.98,0,.32),(-1.90,0,.32),.075,chrome,root=hub)
for side in [-1,1]:
 blade=empty('Condor_BladeHinge_'+str(side),(-1.94,0,.32),hub)
 drive(blade,'rotation_euler',0,str(side)+'*1.570796*(1-t)',[('t',root,'transform')])
 mesh('Condor_MainBlade_'+str(side),[(-1.96,-.03,.32),(-1.96,side*1.45,.32),(-1.96,side*1.49,.40),(-1.96,side*.13,.47)],[(0,1,2,3)],black,blade,bevel=.008)
 m=bpy.data.objects['Condor_MainBlade_'+str(side)].modifiers.new('BladeThickness','SOLIDIFY');m.thickness=.016
# Skids extend down and out; saddle lowers simultaneously.
for side in [-1,1]:
 skid=pivot('Condor_SkidCarriage_'+str(side),(-.15,side*.15,.29))
 drive(skid,'location',2,'0.29-0.16*t',[('t',root,'transform')]);drive(skid,'location',1,str(side)+'*(0.15+0.28*t)',[('t',root,'transform')])
 path('Condor_LandingSkid_'+str(side),[(.43,side*.15,.30),(.38,side*.15,.25),(.28,side*.15,.24),(-.63,side*.15,.24),(-.71,side*.15,.27)],.025,black,skid)
 for x in [.22,-.49]:tube('Condor_SkidStrut',(x,side*.15,.25),(x,side*.15,.37),.020,black,root=skid)
# Studio, stored with the independent asset.
CURRENT=collection('Condor_Studio');PARENT=None
floor=box('Review_Floor',(0,0,-.055),(200,200,.10),material('Condor_StudioFloor',(.16,.19,.21),0,.83),0)
world=bpy.context.scene.world or bpy.data.worlds.new('Condor_World');bpy.context.scene.world=world;world.use_nodes=True;next(n for n in world.node_tree.nodes if n.type=='BACKGROUND').inputs[0].default_value=(.42,.48,.55,1);next(n for n in world.node_tree.nodes if n.type=='BACKGROUND').inputs[1].default_value=.6
for name,pos,power,size in [('Key',(3,-4,6),1600,5),('Fill',(0,4,4),1300,4),('Rim',(-4,-1,5),1800,3)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);CURRENT.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,.7))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('Condor_ReviewCamera');cam=bpy.data.objects.new('Condor_ReviewCamera',d);CURRENT.objects.link(cam);cam.location=(4,-5,3);cam.rotation_euler=(Vector((0,0,.8))-cam.location).to_track_quat('-Z','Y').to_euler();d.lens=52
s=bpy.context.scene;s.camera=cam;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=1100;s.render.resolution_y=900;s.render.resolution_percentage=100
prefs=bpy.context.preferences.addons['cycles'].preferences
try:
 prefs.compute_device_type='OPTIX';prefs.get_devices()
 for dev in prefs.devices:dev.use=dev.type!='CPU'
 s.cycles.device='GPU'
except Exception:s.cycles.device='CPU'
s.view_settings.view_transform='AgX';s.frame_end=121
for frame,value in [(1,0.),(121,1.)]:root['transform']=value;root.keyframe_insert(data_path='["transform"]',frame=frame)
root['transform']=0.;s.frame_set(1)
bpy.ops.object.select_all(action='DESELECT');root.select_set(True);bpy.context.view_layer.objects.active=root
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Condor_V1_Vehicle.blend'),compress=True)
print('CONDOR_V1_BUILT',len(C.all_objects))

