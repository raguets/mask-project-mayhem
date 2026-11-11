"""V10 additive character and sequenced reactors; preserves V9 and live input."""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem/art_source/Thunderhawk')
s=bpy.context.scene
s.frame_set(1)
if not (P/'Thunderhawk_V10_before_work.blend').exists():
    bpy.ops.wm.save_as_mainfile(filepath=str(P/'Thunderhawk_V10_before_work.blend'),copy=True,compress=True)
old=bpy.data.collections.get('MT10_Character')
if old:
 for ob in list(old.objects):bpy.data.objects.remove(ob,do_unlink=True)
 bpy.data.collections.remove(old)
c=bpy.data.collections.new('MT10_Character');s.collection.children.link(c)
root=bpy.data.objects.new('MT_Root_Seated',None);c.objects.link(root)
root['reference']='Eight supplied images inspected: illustration 2012, replicas, toy editions, cartoon portrait. Geometry and seated proportions estimated.'
root['status']='Editable posed character study; not a production animation rig'
def mat(n,col,metal=0,rough=.4):
 m=bpy.data.materials.new(n);m.diffuse_color=(*col,1);m.use_nodes=True
 p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 return m
suit=mat('MT_GreyFlightSuit',(.31,.36,.40));red=mat('MT_RedGlovesTrim',(.55,.012,.019),.08,.3)
strap=mat('MT_CharcoalHarness',(.027,.023,.022),0,.65);silver=mat('Spectrum_SilverShell',(.45,.51,.55),.7,.26)
black=mat('Spectrum_Recess',(.006,.012,.02),.2,.23);blue=mat('Spectrum_BlueVisor',(.012,.12,.32),.65,.16)
boot=mat('MT_BootSole',(.018,.021,.024),0,.6)
def own(o,n,m,parent=root):
 o.name=n
 for co in list(o.users_collection):co.objects.unlink(o)
 c.objects.link(o);o.data.materials.append(m)
 if parent:o.parent=parent
 return o
def ell(n,p,r,m,parent=root):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20,location=p)
 o=own(bpy.context.object,n,m,parent);o.scale=r
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for f in o.data.polygons:f.use_smooth=True
 return o
def box(n,p,d,m,b=.01,parent=root):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=own(bpy.context.object,n,m,parent);o.dimensions=d
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if b:
  mod=o.modifiers.new('SoftManufacturedEdges','BEVEL');mod.width=b;mod.segments=3
  o.modifiers.new('WeightedNormals','WEIGHTED_NORMAL')
 return o
def limb(n,a,b,r1,r2,m):
 a=Vector(a);b=Vector(b);v=b-a
 # Rounded tapered garment section, quad rings, elliptical cross-section.
 q=v.to_track_quat('Z','Y');verts=[];N=24
 for t,k in [(0,.65),(.06,.95),(.20,1),(.78,1),(.94,.95),(1,.65)]:
  r=r1*(1-t)+r2*t
  for i in range(N):verts.append(tuple(a+v*t+q@Vector((r*k*math.cos(i*2*math.pi/N),r*k*.85*math.sin(i*2*math.pi/N),0))))
 faces=[tuple(reversed(range(N)))]
 for j in range(5):
  faces.extend((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i) for i in range(N))
 faces.append(tuple(range(5*N,6*N)))
 me=bpy.data.meshes.new(n);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(n,me);c.objects.link(o);o.parent=root;me.materials.append(m)
 for f in me.polygons:f.use_smooth=len(f.vertices)==4
 return o
def line(n,pts,r,m,parent=root):
 cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=3
 sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,co in zip(sp.points,pts):p.co=(*co,1)
 o=bpy.data.objects.new(n,cu);c.objects.link(o);o.parent=parent;cu.materials.append(m);return o
# Driver seated on left (+Y), +X forward. Cabin envelope roof 1.30m.
y=.40
ell('MT_Pelvis',(-.36,y,.57),(.15,.155,.10),suit)
ell('MT_Torso',(-.39,y,.775),(.115,.185,.225),suit)
for sg,side in [(1,'L'),(-1,'R')]:
 hip=(-.33,y+sg*.09,.57);knee=(.02,y+sg*.115,.54);ankle=(.29,y+sg*.115,.415)
 limb('MT_Thigh_'+side,hip,knee,.09,.072,suit);ell('MT_Knee_'+side,knee,(.073,.072,.067),suit)
 limb('MT_Shin_'+side,knee,ankle,.068,.047,suit)
 box('MT_KneePad_'+side,(.058,y+sg*.115,.565),(.025,.10,.085),red,.016)
 ell('MT_Boot_'+side,(.34,y+sg*.115,.407),(.105,.058,.046),strap)
 box('MT_BootSole_'+side,(.34,y+sg*.115,.377),(.18,.115,.018),boot,.006)
 shoulder=(-.35,y+sg*.175,.90);elbow=(-.09,y+sg*.205,.755);wrist=(.145,y+sg*.145,.81)
 ell('MT_Shoulder_'+side,shoulder,(.085,.09,.09),suit)
 limb('MT_UpperArm_'+side,shoulder,elbow,.074,.060,suit)
 limb('MT_ArmBand_'+side,Vector(shoulder).lerp(Vector(elbow),.47),Vector(shoulder).lerp(Vector(elbow),.68),.075,.07,red)
 ell('MT_Elbow_'+side,elbow,(.063,.060,.06),suit)
 limb('MT_Forearm_'+side,elbow,wrist,.061,.041,suit)
 limb('MT_GloveCuff_'+side,Vector(elbow).lerp(Vector(wrist),.79),wrist,.048,.045,red)
 ell('MT_GlovePalm_'+side,(.16,y+sg*.145,.82),(.048,.043,.036),red)
 for j in range(4):
  yy=y+sg*(.118+j*.017)
  line('MT_GrippingFinger_'+side+str(j),[(.175,yy,.844),(.194,yy,.83),(.192,yy,.807),(.175,yy,.802)],.009,red)
 ell('MT_Thumb_'+side,(.143,y+sg*.114,.818),(.027,.012,.018),red)
 # Broad harness webbing follows torso front rather than floating straight.
 line('MT_Harness_'+side,[(-.335,y+sg*.135,.967),(-.276,y+sg*.11,.88),(-.272,y+sg*.055,.775),(-.272,y+sg*.12,.66)],.014,strap)
 line('MT_TrouserSeam_'+side,[(-.28,y+sg*.17,.59),(-.08,y+sg*.177,.566),(.015,y+sg*.17,.548)],.0025,strap)
box('MT_HarnessBuckle',(-.261,y,.765),(.018,.047,.047),silver,.005)
box('MT_Belt',(-.34,y,.635),(.22,.31,.037),strap,.01)
# Spectrum remains a separately parented removable assembly.
mask=bpy.data.objects.new('Spectrum_Mask_Attach',None);c.objects.link(mask);mask.parent=root
mask['variant']='Illustrated compact Spectrum; replica and toy shapes distinguished in notes'
ell('Spectrum_HelmetShell',(-.37,y,1.09),(.116,.123,.146),silver,mask)
ell('Spectrum_VisorRecess',(-.269,y,1.105),(.048,.111,.073),black,mask)
ell('Spectrum_BlueVisor',(-.242,y,1.11),(.022,.097,.052),blue,mask)
# Heavy red brow and side ear sections, silver crown remains visible.
box('Spectrum_RedBrow',(-.257,y,1.183),(.075,.244,.050),red,.018,mask)
for sg,side in [(1,'L'),(-1,'R')]:
 o=box('Spectrum_Temple_'+side,(-.29,y+sg*.109,1.113),(.067,.036,.125),red,.013,mask);o.rotation_euler[1]=-.22
 ell('Spectrum_Ear_'+side,(-.37,y+sg*.117,1.09),(.055,.022,.075),red,mask)
# Faceted respirator has a high central bridge and flared lower cheek shield.
verts=[(-.218,y,1.105),(-.248,y-.077,1.025),(-.248,y+.077,1.025),(-.239,y-.063,.995),(-.239,y+.063,.995),(-.190,y,1.045),(-.197,y,1.005)]
faces=[(0,1,5),(0,5,2),(1,3,6,5),(5,6,4,2),(3,4,6),(0,2,4,3,1)]
me=bpy.data.meshes.new('Spectrum_Respirator');me.from_pydata(verts,[],faces);me.materials.append(silver)
o=bpy.data.objects.new('Spectrum_Respirator',me);c.objects.link(o);o.parent=mask
mod=o.modifiers.new('RespiratorEdgeRadius','BEVEL');mod.width=.003;mod.segments=2
for i in range(6):box('Spectrum_BreathingSlot_'+str(i),(-.188-i*.0015,y,1.012+i*.006),(.005,.059-i*.005,.0025),black,.001,mask)
for z in [.968,.988]:
 pts=[(-.37+.123*math.cos(i*2*math.pi/64),y+.136*math.sin(i*2*math.pi/64),z) for i in range(65)]
 line('Spectrum_RedCollar_'+str(z),pts,.013,red,mask)
# Parent moving nozzle, throat, vanes and socket together; housings remain fixed.
travel=.085
for side in ['L','R']:
 deploy=bpy.data.objects.new('THK_Reactor_Deploy_'+side,None);bpy.data.collections['THK9_Exterior'].objects.link(deploy);deploy.parent=bpy.data.objects['THK_Root']
 for ob in list(s.objects):
  if ob.name in ['THK_Reactor_'+side,'THK_ReactorThroat_'+side,'SOCKET_Reactor_'+side] or ob.name.startswith('THK_ReactorVane_'+side):
   mw=ob.matrix_world.copy();ob.parent=deploy;ob.matrix_world=mw
 for fr,x in [(1,0),(85,0),(97,-travel),(121,-travel),(133,0),(193,0)]:
  deploy.location.x=x;deploy.keyframe_insert(data_path='location',frame=fr)
 deploy['travel_m_estimated']=travel;deploy['sequence']='Panel fully raised at 85; reactors extend 85-97, retract 121-133'
# Hold raised rear cover until both reactors have retracted.
panel=bpy.data.objects['THK_RearPanel_Lift'];panel.animation_data_clear()
for fr,z in [(1,0),(45,0),(85,.215),(133,.215),(173,0),(193,0)]:
 panel.location=(0,0,z);panel.keyframe_insert(data_path='location',frame=fr)
s.frame_set(97);s.name='THK_V10_Matt_Spectrum';s['THK_Version']='V10';s['THK10_InteriorPendingReference']=True
for screen in bpy.data.screens:
 for ar in screen.areas:
  if ar.type=='VIEW_3D':
   ar.spaces.active.region_3d.view_location=(-.05,.1,.8);ar.spaces.active.region_3d.view_distance=4.8
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Thunderhawk_V10.blend'),compress=True)
print(json.dumps({'file':bpy.data.filepath,'character_objects':len(c.objects),'reactor_travel_m':travel,'interior':'pending references or authorization for interpreted design'}))

