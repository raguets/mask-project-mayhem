import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Raven';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
assert not (A/'Raven_V2_Assembly.blend').exists()
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(encoding='utf-8'),'<geometry>','exec'))
tau=2*pi;root=bpy.data.objects['Raven_Control'];R=bpy.data.objects['CalhounBurns_Rig'];R.location=(0,0,0)
S.frame_set(1);root['hover_height']=0
PAINT=bpy.data.materials['RV_Obsidian_Clearcoat'];TRIM=bpy.data.materials['RV_BlackRubberTrim'];DARK=bpy.data.materials['RV_Gunmetal'];RED=bpy.data.materials['RV_RedLeather'];ALLOY=bpy.data.materials['RV_BrushedAlloy']
CURRENT=bpy.data.collections['RV_Body'];PARENT=root;GROUP='body'
def width(x):return profile(x,[(-2.225,.77),(-1.93,.88),(-1.24,.915),(-.45,.87),(.40,.85),(1.22,.905),(1.9,.86),(2.225,.76)])
def top(x):return profile(x,[(-2.225,.67),(-1.8,.79),(-1.15,.86),(-.6,.82),(.35,.77),(1.25,.74),(1.8,.66),(2.225,.46)])
# Replace grid-clipped wheel arches with exact, continuous arch boundaries.
for sg,label in [(1,'L'),(-1,'R')]:
    for title,a,b,ax in [('Front',.45,2.215,1.22),('Rear',-2.215,-.68,-1.22)]:
        old=bpy.data.objects['RV_'+title+'Fender_'+label];bpy.data.objects.remove(old,do_unlink=True)
        cuts=sorted(set([a,b,ax-.365,ax+.365]+seq(160,a,b)))
        def lower(x):return .335+math.sqrt(max(0,.365**2-(x-ax)**2)) if abs(x-ax)<.365 else .22
        patch('RV_'+title+'Fender_'+label,cuts,seq(12),lambda x,t,sg=sg:(x,sg*(width(x)-.025*(1-t)),lower(x)+(top(x)-.025-lower(x))*t),PAINT,orient=(0,sg,0),sub=0,thick=.012)
    # Inner wheel-well closures remain inboard of the folding wheels.
    for ax in [-1.22,1.22]:
        patch('RV_WheelWellBulkhead_'+label+str(ax),seq(30,ax-.36,ax+.36),seq(12),lambda x,t,sg=sg,ax=ax:(x,sg*.60,.22+(.335+math.sqrt(max(0,.365**2-(x-ax)**2))-.22)*t),TRIM,orient=(0,sg,0),sub=0,thick=.006)
# Close the front and rear bottom silhouettes without pretending to model an engine.
box('RV_FrontUndertray',(1.29,0,.205),(1.75,1.50,.075),TRIM,.018)
box('RV_RearUndertray',(-1.64,0,.205),(1.10,1.45,.075),TRIM,.018)
box('RV_HoodBayArmoredDeck',(1.28,0,.41),(1.70,1.17,.12),DARK,.025)
for y in [-.42,0,.42]:box('RV_HoodBayStiffener_'+str(y),(1.27,y,.49),(1.54,.036,.035),TRIM,.007)
for x in [.70,1.15,1.65]:box('RV_HoodBayServicePanel_'+str(x),(x,0,.487),(.30,.68,.025),DARK,.008)
# Deepen the rear cover to conceal the thrusters when closed; rigid hinged skirt.
cover=bpy.data.objects['RV_ReactorCover_Hinge']
box('RV_ReactorCover_RearSkirt',(-2.255,0,.741),(.028,1.44,.14),PAINT,.007,root=cover)
for sg in [-1,1]:box('RV_ReactorCover_SideSkirt_'+str(sg),(-2.02,sg*.718,.753),(.48,.022,.125),PAINT,.006,root=cover)
# Lighten glass reflections, keeping actual transmissive glass.
glass=bpy.data.materials['RV_TintedGlass'];p=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(.55,.65,.69,1);p.inputs['Roughness'].default_value=.09
for name in ['RV_Key','RV_Fill','RV_Rim']:
    light=bpy.data.objects[name].data;light.size*=.72;light.energy*=.75
world=next(n for n in S.world.node_tree.nodes if n.type=='BACKGROUND');world.inputs[1].default_value=.40
# The same standing/driving skeleton receives a fitted sports-car driving pose.
def capture():return {b.name:{p:tuple(getattr(b,p)) for p in ['location','rotation_quaternion','scale']} for b in R.pose.bones}
R['driving_pose']=0;R.update_tag();bpy.context.view_layer.update();stand=capture()
R['driving_pose']=1;R.update_tag();bpy.context.view_layer.update();seated=capture()
for f in list(R.animation_data.drivers):
    if f.data_path.startswith('pose.bones['):R.animation_data.drivers.remove(f)
def apply_pose(data):
    for name,channels in data.items():
        b=R.pose.bones[name];b.rotation_mode='QUATERNION'
        for p,v in channels.items():setattr(b,p,v)
    bpy.context.view_layer.update()
apply_pose(seated)
hip=R.pose.bones['pelvis'].head.copy();rotation=Matrix.Translation(hip)@Matrix.Rotation(-.18,4,'Y')@Matrix.Translation(-hip)
names=['spine','chest','neck','head','upper_arm.L','forearm.L','hand.L','upper_arm.R','forearm.R','hand.R']
matrices={name:rotation@R.pose.bones[name].matrix for name in names}
for name in names:R.pose.bones[name].matrix=matrices[name];bpy.context.view_layer.update()
def setbone(name,a,b):
    bone=R.data.bones[name];a,b=Vector(a),Vector(b);q=(bone.tail_local-bone.head_local).rotation_difference(b-a)@bone.matrix_local.to_quaternion();R.pose.bones[name].matrix=Matrix.LocRotScale(a,q,Vector((1,(b-a).length/bone.length,1)));bpy.context.view_layer.update()
for sg,side in [(1,'L'),(-1,'R')]:
    shin=R.pose.bones['shin.'+side];a=shin.head.copy();foot=Vector((.40,sg*.115,.40));tip=Vector((.54,sg*.115,.38));setbone('shin.'+side,a,foot);setbone('foot.'+side,foot,tip)
    upper=R.pose.bones['upper_arm.'+side];shoulder=upper.head.copy();elbow=Vector((-.15,sg*.20,.69));wrist=Vector((.10,sg*.143,.85));tip=Vector((.19,sg*.143,.85));setbone('upper_arm.'+side,shoulder,elbow);setbone('forearm.'+side,elbow,wrist);setbone('hand.'+side,wrist,tip)
seated=capture();apply_pose(stand)
for name in stand:
    for prop in ['location','rotation_quaternion','scale']:
        aa=stand[name][prop];dd=list(seated[name][prop])
        if prop=='rotation_quaternion' and sum(x*y for x,y in zip(aa,dd))<0:dd=[-x for x in dd]
        for i,(a,d) in enumerate(zip(aa,dd)):drive(R.pose.bones[name],prop,i,f'{a:.10g}+({d-a:.10g})*d',[('d',R,'driving_pose')])
drive(R,'location',0,'.02*a',[('a',R,'in_vehicle')]);drive(R,'location',1,'.37*a',[('a',R,'in_vehicle')]);drive(R,'location',2,'(-.14+h)*a',[('a',R,'in_vehicle'),('h',root,'hover_height')])
CURRENT=bpy.data.collections['RV_Interior'];PARENT=root;GROUP='interior'
for name in ['RV_DriverSeatPan','RV_PassengerSeatPan','RV_DriverSeatBolster_-1','RV_DriverSeatBolster_1','RV_PassengerSeatBolster_-1','RV_PassengerSeatBolster_1']:
    for v in bpy.data.objects[name].data.vertices:v.co.z-=.10
for v in bpy.data.objects['RV_CabinFloor'].data.vertices:v.co.z-=.11
for name in ['RV_Pedal_0.31','RV_Pedal_0.46']:
    for v in bpy.data.objects[name].data.vertices:v.co.z-=.04
# Replace the open prototype mask with one continuous shell and sealed cheeks.
MASK=bpy.data.collections['CB_Mask']
for o in list(MASK.all_objects):bpy.data.objects.remove(o,do_unlink=True)
CURRENT=MASK;PARENT=None;GROUP='mask'
SHELL=bpy.data.materials['CB_OrangeMaskShell'];VISOR=bpy.data.materials['CB_SmokeVisor'];JOINT=bpy.data.materials['CB_MaskDarkJoint'];CYAN=bpy.data.materials['CB_CyanHarness'];HAIR=bpy.data.materials['CB_ChestnutHair']
def bind(o,bone='head'):
    o.vertex_groups.new(name=bone).add(list(range(len(o.data.vertices))),1,'REPLACE');m=o.modifiers.new('CalhounEditableSkin','ARMATURE');m.object=R;m.use_deform_preserve_volume=True;o.parent=R;return o
def visibility(o,is_mask=True):
    for prop in ['hide_render','hide_viewport']:drive(o,prop,None,'1-m' if is_mask else 'm',[('m',R,'mask_on')])
R['driving_pose']=0;R['in_vehicle']=0;R.update_tag();bpy.context.view_layer.update()
rows=[(1.535,.143,.132),(1.58,.166,.146),(1.64,.180,.151),(1.70,.170,.150),(1.76,.150,.139),(1.81,.117,.114),(1.845,.069,.073),(1.862,.009,.012)]
def rx(z):return profile(z,[(z,x) for z,x,y in rows])
def ry(z):return profile(z,[(z,y) for z,x,y in rows])
vv=[];ff=[];N=96
for z,x,y in rows:
    for i in range(N):a=tau*i/N;vv.append((.005+x*cos(a),y*sin(a),z))
for j in range(len(rows)-1):
    for i in range(N):ff.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
ff.append(tuple((len(rows)-1)*N+i for i in range(N)))
shell=bind(mesh('CB_ClosedHelmetShell',vv,ff,SHELL,smooth=True));shell.modifiers.new('ShellWall','SOLIDIFY').thickness=.004
vis=patch('CB_ContinuousWrapVisor',seq(56,-1,1),seq(12),lambda u,t:(.005+(rx(1.658+.095*t-.009*abs(u))+.006)*cos(u*1.34),(ry(1.658+.095*t-.009*abs(u))+.006)*sin(u*1.34),1.658+.095*t-.009*abs(u)),VISOR,sub=0,thick=.003,orient=(1,0,0));bind(vis)
guard=patch('CB_TaperedSealedRespirator',seq(28,-1,1),seq(18),lambda u,t:(profile(t,[(0,.178),(.5,.215),(1,.203)])-.012*u*u,profile(t,[(0,.042),(.5,.065),(1,.076)])*u,1.545+.12*t),SHELL,sub=1,thick=.022,orient=(1,0,0));bind(guard)
for z in [1.563,1.584,1.605,1.626,1.647]:
    t=(z-1.545)/.12;x=profile(t,[(0,.178),(.5,.215),(1,.203)])+.002;width=profile(t,[(0,.06),(.5,.11),(1,.13)])
    bind(box('CB_DarkRecessedVent_'+str(z),(x,0,z),(.004,width,.0035),JOINT,.0008))
bind(box('CB_RespiratorCentralSpine',(.218,0,1.611),(.008,.008,.085),SHELL,.002))
for sg,label in [(1,'L'),(-1,'R')]:
    bind(box('CB_LateralFilter_'+label,(-.008,sg*.153,1.695),(.125,.029,.147),SHELL,.013))
    bind(box('CB_FilterSlot_'+label,(.05,sg*.169,1.695),(.010,.004,.105),JOINT,.002))
    bind(box('CB_FittedNeckSeal_'+label,(-.005,sg*.115,1.537),(.18,.035,.025),CYAN,.008))
# Low molded crown ribs projected onto the actual shell, with no floating tubes.
shelltree=BVHTree.FromPolygons([v.co for v in shell.data.vertices],[list(f.vertices) for f in shell.data.polygons])
for y in [-.048,0,.048]:
    points=[]
    for x in seq(40,-.12,.125):
        hit=shelltree.ray_cast(Vector((x,y,2)),Vector((0,0,-1)),.5)
        if hit[0]:points.append(tuple(hit[0]+hit[1]*.001))
    curve=path('CB_MoldedCrownRib_'+str(y),points,.0035,SHELL)
    dg=bpy.context.evaluated_depsgraph_get();me=bpy.data.meshes.new_from_object(curve.evaluated_get(dg),depsgraph=dg);o=bpy.data.objects.new(curve.name+'_Mesh',me);MASK.objects.link(o);bpy.data.objects.remove(curve,do_unlink=True);bind(o)
for o in MASK.all_objects:visibility(o)
# Replace the irregular cropped scalp edge with a continuous ray-fitted hair cap.
CURRENT=bpy.data.collections['CB_Character'];HEAD=bpy.data.objects['CB_Head_AnatomicalSurface'];PARENT=None;GROUP='calhoun'
for o in list(CURRENT.all_objects):
    if 'SweptBackScalp' in o.name or 'SweptHairStrand_' in o.name:bpy.data.objects.remove(o,do_unlink=True)
headtree=BVHTree.FromPolygons([v.co for v in HEAD.data.vertices],[list(f.vertices) for f in HEAD.data.polygons]);center=Vector((-.008,0,1.70));vv=[];ff=[];N=96;H=24
for j in range(H):
    for i in range(N):
        a=tau*i/N;maxphi=1.45-.27*cos(a);phi=.015+(maxphi-.015)*j/(H-1);direction=Vector((sin(phi)*cos(a),sin(phi)*sin(a),cos(phi)))
        hit=headtree.ray_cast(center,direction,.35)
        point,normal=hit[:2];q=point+normal*.004;q.z+=.016*(1-j/(H-1))**2;vv.append(tuple(q))
for j in range(H-1):
    for i in range(N):ff.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
hair=bind(mesh('CB_ContinuousSweptHairCap',vv,ff,HAIR,smooth=True));visibility(hair,False)
hp=next(n for n in HAIR.node_tree.nodes if n.type=='BSDF_PRINCIPLED');hp.inputs['Base Color'].default_value=(.032,.009,.0035,1);hp.inputs['Roughness'].default_value=.62
ns=HAIR.node_tree.nodes;ls=HAIR.node_tree.links;noise=ns.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=220;bump=ns.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.25;bump.inputs['Distance'].default_value=.0006;ls.new(noise.outputs['Fac'],bump.inputs['Height']);ls.new(bump.outputs['Normal'],hp.inputs['Normal'])
# All four states use exactly the same meshes and rig.
R['driving_pose']=1.;R['in_vehicle']=1.;R['mask_on']=False;R['asset_version']='Calhoun Burns V2';R.update_tag();S.frame_set(1);bpy.context.view_layer.update()
(A/'calhoun_pose_basis_v2.json').write_text(json.dumps({'standing':stand,'driving':seated},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Raven_V2_Assembly.blend'),compress=True)
print('RAVEN_AND_CALHOUN_V2_SAVED')
