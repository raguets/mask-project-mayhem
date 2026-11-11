"""One independently editable Hondo, from inspected toy/illustration references.
Generic CC0 anatomy basis; no real-person likeness. Same body/head/rig in all states.
"""
import bpy,math,random,json
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from math import sin,cos,pi,exp,sqrt
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Hurricane';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
assert bpy.data.objects.get('HondoMacLean_Rig')
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Session_before_Hondo_design_v1.blend'),copy=True,compress=True)
exec(compile((A/'scripts/geometry.py').read_text(),'<geometry>','exec'))
R=bpy.data.objects['HondoMacLean_Rig'];C=bpy.data.collections['HMC_Character'];CURRENT=C;PARENT=None;GROUP='hondo_body'
R['driving_pose']=0.;R['mask_on']=False;R.location=(0,0,0);R.update_tag();S.frame_set(1);bpy.context.view_layer.update()
# Remove replaced clothing, inherited hair, and obsolete mannequin source meshes.
remove=['HMC_Hair_','HMC_ChestArmor','HMC_SmoothShoulder','HMC_Vest','HMC_Suit_Torso','HMC_ContinuousSleeve','HMC_ContinuousTrouser','HMC_DeltoidCloth','HMC_GlovePalm','HMC_GloveFinger','HMC_GloveKnuckle','HMC_GloveThumb']
for o in list(C.all_objects):
    if any(o.name.startswith(p) for p in remove):bpy.data.objects.remove(o,do_unlink=True)
def cloth(name,color):
    m=material(name,color,0,.80);ns=m.node_tree.nodes;ls=m.node_tree.links;n=ns.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=260;b=ns.new('ShaderNodeBump');b.inputs['Distance'].default_value=.00045;b.inputs['Strength'].default_value=.20;ls.new(n.outputs['Fac'],b.inputs['Height']);ls.new(b.outputs['Normal'],next(n for n in ns if n.type=='BSDF_PRINCIPLED').inputs['Normal']);return m
PURPLE=cloth('HMC_DeepPurpleFabric',(.20,.012,.092));YELLOW=material('HMC_GoldenArmor',(.80,.39,.012),.13,.39);YELLOWLEATHER=material('HMC_YellowBootLeather',(.66,.30,.008),.04,.54);BLUE=material('HMC_DeepBlueEquipment',(.008,.075,.205),.22,.43);GOLD=material('HMC_GoldFasteners',(.70,.38,.025),.75,.24);BLACK=material('HMC_Recess',(.003,.006,.008),.05,.62);SKIN=material('HMC_BrownSkin',(.19,.075,.041),0,.49);LIPS=material('HMC_LipTint',(.105,.026,.018),0,.48);HAIR=material('HMC_ShortBlackHair',(.006,.004,.003),0,.86)
p=next(n for n in SKIN.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Subsurface Weight'].default_value=.08;p.inputs['Subsurface Scale'].default_value=.025
ns=SKIN.node_tree.nodes;ls=SKIN.node_tree.links;n=ns.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=380;b=ns.new('ShaderNodeBump');b.inputs['Strength'].default_value=.12;b.inputs['Distance'].default_value=.00020;ls.new(n.outputs['Fac'],b.inputs['Height']);ls.new(b.outputs['Normal'],p.inputs['Normal'])
suit=bpy.data.objects['HMC_ContinuousFlightSuit'];head=bpy.data.objects['HMC_Head_AnatomicalSurface'];suit.data.materials.clear();suit.data.materials.append(PURPLE)
for f in suit.data.polygons:f.material_index=0
def headmorph(p):
    p=p.copy();t=max(0,min(1,(1.76-p.z)/.19));p.y*=1+.11*t
    nose=exp(-((p.z-1.652)/.027)**2)*max(0,min(1,(p.x-.070)/.055));p.y*=1+.14*nose
    mouth=exp(-((p.z-1.607)/.020)**2-(p.y/.045)**2);p.x+=.003*mouth
    return p
for o in C.all_objects:
    if o.type=='MESH' and any(k in o.name for k in ['Head_','Eyeball','Iris_','Brow_']):
        for v in o.data.vertices:v.co=headmorph(v.co)
        o.data.update()
head.data.materials.clear();head.data.materials.append(SKIN);head.data.materials.append(LIPS)
for f in head.data.polygons:
    p=f.center;f.material_index=int(p.x>.077 and abs(p.y)<.034 and 1.600<p.z<1.623)
for o in C.all_objects:
    if o.type!='MESH':continue
    if any(k in o.name for k in ['GloveSkin']):
        o.data.materials.clear();o.data.materials.append(SKIN)
        for f in o.data.polygons:f.material_index=0
    elif any(k in o.name for k in ['OrangeGaiter','BootUpper','BootWelt','Cuff','KneePatch']):
        for i in range(len(o.data.materials)):o.data.materials[i]=YELLOWLEATHER if 'Boot' in o.name else YELLOW
    elif any(k in o.name for k in ['ArmBand','FabricCollar']):
        for i in range(len(o.data.materials)):o.data.materials[i]=PURPLE
    elif o.name=='HMC_Belt':
        for i in range(len(o.data.materials)):o.data.materials[i]=BLUE
    elif o.name=='HMC_BeltBuckle':
        for i in range(len(o.data.materials)):o.data.materials[i]=GOLD
    if 'Brow_' in o.name:
        for i in range(len(o.data.materials)):o.data.materials[i]=HAIR
        for attribute in o.data.color_attributes:
            for p in attribute.data:p.color=(.006,.004,.003,1)
    if 'Iris_' in o.name:
        attribute=o.data.color_attributes.get('IrisColor')
        if attribute:
            for p in attribute.data:p.color=(.045,.019,.008,1)
def bind(o,bone='head',weights=None):
    if weights:
        for i,ww in enumerate(weights):
            total=sum(ww.values()) or 1
            for name,w in ww.items():
                vg=o.vertex_groups.get(name) or o.vertex_groups.new(name=name);vg.add([i],w/total,'REPLACE')
    else:o.vertex_groups.new(name=bone).add(list(range(len(o.data.vertices))),1,'REPLACE')
    mod=o.modifiers.new('EditableHondoSkin','ARMATURE');mod.object=R;mod.use_deform_preserve_volume=True;o.parent=R;return o
def visible(o,mask=False):
    for prop in ['hide_render','hide_viewport']:drive(o,prop,None,'1-m' if mask else 'm',[('m',R,'mask_on')])
# Fitted plates use the actual weighted garment surface, with regular boundaries.
sv=suit.data.vertices;sf=suit.data.polygons;tree=BVHTree.FromPolygons([v.co for v in sv],[list(f.vertices) for f in sf])
def project_panel(name,ys,zs,mat,offset=.009,keep=None):
    vv=[];ww=[];ff=[];N=len(zs)
    for y in ys:
        for z in zs:
            hit=tree.ray_cast(Vector((.38,y,z)),Vector((-1,0,0)),.70)
            if not hit[0]:hit=tree.find_nearest(Vector((.12,y,z)))
            point,normal,index,dist=hit;point=Vector((point.x+offset,y,z));vv.append(tuple(point));face=sf[index];nearest=min((sv[k] for k in face.vertices),key=lambda v:(v.co-point).length_squared);ww.append({suit.vertex_groups[g.group].name:g.weight for g in nearest.groups})
    for i in range(len(ys)-1):
        for j in range(N-1):
            if keep and not keep((ys[i]+ys[i+1])/2,(zs[j]+zs[j+1])/2):continue
            ff.append((i*N+j,(i+1)*N+j,(i+1)*N+j+1,i*N+j+1))
    o=bind(mesh(name,vv,ff,mat,smooth=True),weights=ww);solid=o.modifiers.new('PlateThickness','SOLIDIFY');solid.thickness=.0035;return o
for sg,label in [(1,'L'),(-1,'R')]:
    project_panel('HMC_UpperChestArmor_'+label,[sg*y for y in seq(18,.018,.238)],seq(18,1.33,1.465),YELLOW,.010,lambda y,z:abs(y)>(1.465-z)*.25+.018 and z>1.33+.18*max(0,.1-abs(y)))
project_panel('HMC_BlueChestPanel',seq(20,-.073,.073),seq(28,1.105,1.385),BLUE,.017)
for i,y in enumerate([-.035,0,.035]):bind(box('HMC_ChestIndicator_'+str(i),(.134,y,1.285),(.012,.016,.026),YELLOW,.004),bone='chest')
bind(tube('HMC_ChestMedallion',(.126,0,1.17),(.143,0,1.17),.029,GOLD,N=40),bone='chest')
bind(box('HMC_RightHipHolster',(.01,-.188,.90),(.13,.075,.22),BLUE,.025),bone='thigh.R')
for sg,label in [(1,'L'),(-1,'R')]:
    # Smooth fitted shoulder coverage, no separate spherical shoulder joint.
    vv=[];ff=[];ww=[];mapping={}
    for face in sf:
        p=face.center
        if not(sg*p.y>.145 and 1.34<p.z<1.465):continue
        weights={suit.vertex_groups[g.group].name:g.weight for k in face.vertices for g in sv[k].groups}
        if weights.get('upper_arm.'+label,0)+weights.get('clavicle.'+label,0)<.1:continue
        ids=[]
        for k in face.vertices:
            if k not in mapping:
                v=sv[k];mapping[k]=len(vv);vv.append(tuple(v.co+v.normal*.009));ww.append({suit.vertex_groups[g.group].name:g.weight for g in v.groups})
            ids.append(mapping[k])
        ff.append(ids)
    if ff:
        o=bind(mesh('HMC_FittedShoulder_'+label,vv,ff,YELLOW,smooth=True),weights=ww);m=o.modifiers.new('ShoulderShellThickness','SOLIDIFY');m.thickness=.003
# Short close-cropped hair on the actual skull, plus fine curved fibers.
mapping={};vv=[];ff=[]
for face in head.data.polygons:
    p=face.center
    if not(p.z>1.724+(max(0,p.x)*.15) or (p.x<-.015 and p.z>1.673)):continue
    ids=[]
    for k in face.vertices:
        if k not in mapping:
            v=head.data.vertices[k];mapping[k]=len(vv);vv.append(tuple(v.co+v.normal*.002))
        ids.append(mapping[k])
    ff.append(ids)
hair=bind(mesh('HMC_CloseCropScalp',vv,ff,HAIR,smooth=True));visible(hair)
rng=random.Random(57);hv=[];hf=[]
for face in rng.sample(list(hair.data.polygons),min(1200,len(hair.data.polygons))):
    c=face.center;n=face.normal.normalized();axis=n.cross(Vector((1,0,0)))
    if axis.length<.1:axis=n.cross(Vector((0,1,0)))
    axis.normalize();side=n.cross(axis).normalized();off=len(hv)
    for j in range(7):
        t=j/6;a=t*1.4*pi;center=c+n*(.0008+.0034*sin(pi*t))+axis*(.0014*cos(a))+side*(.0014*sin(a))
        for k in range(4):hv.append(tuple(center+axis*(.00034*cos(k*pi/2))+side*(.00034*sin(k*pi/2))))
    for j in range(6):hf.extend((off+j*4+k,off+j*4+(k+1)%4,off+(j+1)*4+(k+1)%4,off+(j+1)*4+k) for k in range(4))
hair=bind(mesh('HMC_ShortCurlGroom',hv,hf,HAIR,smooth=True));visible(hair)
# Three poses on the same rig, preserving the repaired neck and continuous garments.
def capture():return {pb.name:{p:tuple(getattr(pb,p)) for p in ['location','rotation_quaternion','scale']} for pb in R.pose.bones}
R['driving_pose']=0;R.update_tag();bpy.context.view_layer.update();stand=capture();R['driving_pose']=1;R.update_tag();bpy.context.view_layer.update();driving=capture()
for f in list(R.animation_data.drivers):
    if f.data_path.startswith('pose.bones['):R.animation_data.drivers.remove(f)
def apply_pose(data):
    for name,channels in data.items():
        pb=R.pose.bones[name];pb.rotation_mode='QUATERNION'
        for prop,value in channels.items():setattr(pb,prop,value)
    bpy.context.view_layer.update()
def setbone(name,a,b):
    bone=R.data.bones[name];a,b=Vector(a),Vector(b);q=(bone.tail_local-bone.head_local).rotation_difference(b-a)@bone.matrix_local.to_quaternion();R.pose.bones[name].matrix=Matrix.LocRotScale(a,q,Vector((1,(b-a).length/bone.length,1)));bpy.context.view_layer.update()
apply_pose(driving)
for side in ['L','R']:
    shin=R.pose.bones['shin.'+side];foot=R.pose.bones['foot.'+side];a=shin.head.copy();b=foot.head.copy()+Vector((.07,0,.065));tail=foot.tail.copy()+Vector((.07,0,.065));setbone('shin.'+side,a,b);setbone('foot.'+side,b,tail)
driving=capture();apply_pose(stand)
for sg,label in [(1,'L'),(-1,'R')]:
    shoulder=R.data.bones['upper_arm.'+label].head_local.copy();elbow=Vector((.24,sg*.22,1.28));wrist=Vector((.37,sg*.16,1.49));tip=Vector((.46,sg*.16,1.49));setbone('upper_arm.'+label,shoulder,elbow);setbone('forearm.'+label,elbow,wrist);setbone('hand.'+label,wrist,tip)
gunner=capture();apply_pose(stand)
R['gunner_pose']=0.;R['in_vehicle']=1.;R['vehicle_lift']=0.
for key in ['driving_pose','gunner_pose','in_vehicle']:R.id_properties_ui(key).update(min=0,max=1)
R.id_properties_ui('gunner_pose').update(description='Pose debout de tir du meme personnage ; 0 repos/conduite, 1 double canon')
for name in stand:
    for prop in ['location','rotation_quaternion','scale']:
        aa=stand[name][prop];dd=list(driving[name][prop]);gg=list(gunner[name][prop])
        if prop=='rotation_quaternion':
            if sum(x*y for x,y in zip(aa,dd))<0:dd=[-x for x in dd]
            if sum(x*y for x,y in zip(aa,gg))<0:gg=[-x for x in gg]
        for i,(s,d,g) in enumerate(zip(aa,dd,gg)):drive(R.pose.bones[name],prop,i,f'{s:.10g}+({d-s:.10g})*d*(1-g)+({g-s:.10g})*g',[('d',R,'driving_pose'),('g',R,'gunner_pose')])
MASTER=bpy.data.objects['Hurricane_Control'];drive(R,'["gunner_pose"]',None,'p',[('p',MASTER,'_roofgun')]);drive(R,'["vehicle_lift"]',None,'l',[('l',MASTER,'_lift')])
drive(R,'location',0,'a*(-.10+.15*g)',[('a',R,'in_vehicle'),('g',R,'gunner_pose')]);drive(R,'location',1,'a*.37*(1-g)',[('a',R,'in_vehicle'),('g',R,'gunner_pose')]);drive(R,'location',2,'a*(.36+.71*g+.58*l)',[('a',R,'in_vehicle'),('g',R,'gunner_pose'),('l',R,'vehicle_lift')]);R['driving_pose']=1.
for o in C.all_objects:
    if o.type=='MESH' and o.data.shape_keys and o.data.shape_keys.key_blocks.get('DrivingGrip'):
        key=o.data.shape_keys.key_blocks['DrivingGrip'];drive(key,'value',None,'max(d,g)*.85',[('d',R,'driving_pose'),('g',R,'gunner_pose')])
# Fitted helmet: domed crown, angular brow, open cheek cage and flared rear apron.
MASK=collection('HMC_Mask');CURRENT=MASK;GROUP='hondo_mask';PARENT=None
CYAN=material('HMC_MaskTurquoise',(.01,.29,.34),.28,.30);MRED=material('HMC_MaskRed',(.48,.012,.027),.24,.33);VISOR=material('HMC_BlackVisor',(.003,.014,.017),.45,.13)
N=80;vv=[];ff=[]
for j in range(21):
    theta=.005+1.54*j/20
    for i in range(N):
        a=i*2*pi/N;vv.append((-.015+.139*sin(theta)*cos(a),.130*sin(theta)*sin(a),1.735+.120*cos(theta)))
for j in range(20):ff.extend((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i) for i in range(N))
o=bind(mesh('HMC_MaskDomedCrown',vv,ff,CYAN,smooth=True));m=o.modifiers.new('CrownWall','SOLIDIFY');m.thickness=.004
poly=[(-.119,1.758),(-.055,1.773),(0,1.801),(.055,1.773),(.119,1.758),(.116,1.736),(.043,1.752),(0,1.775),(-.043,1.752),(-.116,1.736)]
bind(mesh('HMC_MaskRedBrow',[(.125+.028*(1-(y/.13)**2),y,z) for y,z in poly],[tuple(range(len(poly)))],MRED,smooth=False))
bind(box('HMC_MaskBrowLedge',(.145,0,1.709),(.035,.259,.027),CYAN,.008))
patcho=patch('HMC_NarrowEyeVisor',seq(32,-.111,.111),[1.668,1.695],lambda y,z:(.149+.015*(1-(y/.12)**2),y,z),VISOR,thick=.003,sub=0,orient=(1,0,0));bind(patcho)
bind(mesh('HMC_MaskNoseBridge',[(.177,-.026,1.677),(.177,.026,1.677),(.194,.020,1.630),(.194,-.020,1.630)],[(0,1,2,3)],CYAN,bevel=.002))
for sg in [-1,1]:
    bind(path('HMC_MaskEyeFrame_'+str(sg),[(.145,sg*.121,1.716),(.158,sg*.116,1.665),(.188,sg*.095,1.620),(.181,sg*.090,1.575)],.012,CYAN).to_mesh() if False else mesh('HMC_MaskSideCheekBar_'+str(sg),[(.145,sg*.13,1.716),(.168,sg*.114,1.65),(.193,sg*.10,1.58),(.171,sg*.075,1.57),(.145,sg*.091,1.65),(.126,sg*.107,1.716)],[(0,1,4,5),(1,2,3,4)],CYAN,smooth=False))
    for j,x in enumerate([-.066,-.017,.032]):bind(tube('HMC_RedCheekCartridge_'+str((sg,j)),(x,sg*.139,1.60),(x,sg*.139,1.671),.019,MRED,r2=.017,N=28))
    bind(tube('HMC_CheekCartridgeRail_'+str(sg),(-.090,sg*.14,1.60),(.055,sg*.14,1.60),.010,CYAN))
bind(box('HMC_MaskMouthBar',(.182,0,1.625),(.023,.167,.018),CYAN,.005));bind(box('HMC_MaskLowerMouthBar',(.179,0,1.579),(.025,.175,.018),CYAN,.005))
bind(mesh('HMC_MaskChinGuard',[(.180,-.090,1.585),(.180,.090,1.585),(.149,.065,1.539),(.149,-.065,1.539)],[(0,1,2,3)],CYAN,smooth=False))
# Rear skirt covers only the back/sides, leaving the face cage open.
rows=[(1.492,.165,.190),(1.54,.153,.174),(1.62,.134,.146),(1.705,.131,.131)];N=64;vv=[];ff=[]
for z,rx,ry in rows:
    for i in range(N):
        a=pi/2+pi*i/(N-1);vv.append((-.015+rx*cos(a),ry*sin(a),z))
for j in range(len(rows)-1):
    for i in range(N-1):
        a=pi/2+pi*(i+.5)/(N-1)
        if j==0 and abs(a-pi)<.70:continue
        ff.append((j*N+i,j*N+i+1,(j+1)*N+i+1,(j+1)*N+i))
o=bind(mesh('HMC_FlaredRearHelmetApron',vv,ff,CYAN,smooth=True));m=o.modifiers.new('ApronWall','SOLIDIFY');m.thickness=.004
for z in [1.507,1.548]:bind(path('HMC_RearVentFrame_'+str(z),[(-.015+(.162 if z<1.53 else .15)*cos(a),(.185 if z<1.53 else .17)*sin(a),z) for a in seq(40,pi/2,3*pi/2)],.010,CYAN)) if False else None
# A closed lower rim around the rear vent is a mesh, with rigid head weights.
for z in [1.501,1.545]:
    for sg in [-1,1]:bind(tube('HMC_RearVentEdge_'+str((z,sg)),(-.15,sg*.0,z),(-.115,sg*.145,z),.008,CYAN))
for j,x in enumerate([-.110,-.058,-.006,.046]):
    z=1.735+.12*sqrt(max(0,1-((x+.015)/.139)**2))+.008;bind(box('HMC_RedCrestSegment_'+str(j),(x,0,z),(.042,.041,.025),MRED,.008))
for o in MASK.all_objects:
    visible(o,True);o['reference']='Supplied Hondo Hurricane mask toy close-ups; unseen shell thickness interpreted.'
# Architecture corrections for a real-scale seated human rather than stretching his neck.
for name,delta in [('HU_CabinFloor',-.13),('HU_FloorCarpet',-.12)]:
    for v in bpy.data.objects[name].data.vertices:v.co.z+=delta
for name in ['HU_DriverSeatPan','HU_PassengerSeatPan']:
    for v in bpy.data.objects[name].data.vertices:v.co.z-=.025
for o in S.objects:
    if o.name.startswith('HU_LowerFrameRail_'):
        for v in o.data.vertices:v.co.z-=.15
CURRENT=bpy.data.collections['HU_Interior'];PARENT=bpy.data.objects['HU_UpperChassisLift'];GROUP='interior'
box('HU_TransmissionConsoleEnclosure',(.02,0,.47),(.78,.37,.17),bpy.data.materials['HU_ChassisGraphite'],.022)
# Enclose the inside webs of both tail fins.
CURRENT=bpy.data.collections['HU_Body'];GROUP='body'
def belt(x):return profile(x,[(-2.62,1.28),(-2.28,1.22),(-1.25,1.12),(.15,1.13),(.85,1.12),(1.8,1.10),(2.55,1.12)])
for sg in [-1,1]:patch('HU_TailFinInnerWeb_'+str(sg),seq(40,-2.60,-1.11),seq(8),lambda x,t,sg=sg:(x,sg*.76,1.062+(belt(x)-1.062)*t),bpy.data.materials['HU_TurquoisePaint'],orient=(0,-sg,0))
for o in S.objects:
    if o.animation_data:
        for f in o.animation_data.drivers:f.driver.expression=f.driver.expression.replace(' + 0.0','')+' + 0.0'
    o.update_tag()
S.frame_set(1);bpy.context.view_layer.update();S.frame_set(151);bpy.context.view_layer.update();S.frame_set(1)
bad=[o.name+':'+f.data_path for o in S.objects if o.animation_data for f in o.animation_data.drivers if not f.driver.is_valid]
assert not bad,bad
R['asset_version']='Hondo MacLean V1';R['reference_note']='Generic anatomical interpretation of supplied Hondo toy photographs and illustrated portrait. Hurricane purple/yellow outfit; not the red/green variant. Same head/body/rig in standing, driving and gunner poses.';R['anatomy_provenance']='Blender Human Base Meshes CC0, inherited editable anatomy via Bruce Sato source; copied into independent Hondo meshes, materials and skeleton, reshaped facial proportions and close-cropped hair.'
(A/'hondo_pose_basis_v1.json').write_text(json.dumps({'standing':stand,'driving':driving,'gunner':gunner},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Hurricane_V2_Assembly.blend'),compress=True);print('HONDO_AND_MASK_V1_BUILT',len(C.all_objects),len(MASK.all_objects))
