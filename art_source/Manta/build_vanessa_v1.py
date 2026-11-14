"""CC0 female anatomy, one articulated body/head; standalone removable Whip."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Manta';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
CURRENT=collection('Vanessa_Character');C=CURRENT;PARENT=None;GROUP='Vanessa'
navy=material('VW_RoyalBlueSuit',(.018,.055,.26),.08,.54)
cyan=material('VW_CyanSleeve',(.09,.45,.55),.06,.51)
red=material('VW_RedLeather',(.48,.009,.019),.08,.40)
skin=material('VW_InterpretedSkin',(.61,.35,.23),0,.47)
bs=next(n for n in skin.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Subsurface Weight'].default_value=.10
hair=material('VW_AuburnHair',(.20,.012,.009),.08,.43)
hairlight=material('VW_CopperHairGlints',(.34,.025,.013),.1,.40)
black=material('VW_BlackLeather',(.009,.013,.02),.06,.48)
silver=material('VW_SilverBuckle',(.48,.54,.59),.8,.25)
white=material('VW_EyeWhite',(.72,.76,.72),0,.30)
iris=material('VW_GreenIris',(.035,.10,.068),.0,.33)
lip=material('VW_LipTint',(.40,.045,.047),0,.41)
with bpy.data.libraries.load(str(P/'art_source/AnatomyBase/bundle/human_base_meshes_bundle.blend'),link=False) as (src,dst):
 dst.objects=['GEO-body_female_realistic','GEO-body_female_realistic.eye.L','GEO-body_female_realistic.eye.R']
source_body=dst.objects[0];source_origin=source_body.location.copy();scale=1.035
Q=Matrix.Rotation(pi/2,4,'Z')
def anatomypoint(p):return (Q.to_3x3()@p)*scale
body=source_body;C.objects.link(body);body.name='VW_ContinuousBodyAndFace';body.data=body.data.copy();bpy.context.view_layer.update()
wm=body.matrix_world.copy()
for v in body.data.vertices:v.co=anatomypoint(wm@v.co-source_origin)
body.matrix_world=Matrix.Identity(4);body.data.materials.clear()
for m in [navy,cyan,red,skin,black,lip]:body.data.materials.append(m)
for f in body.data.polygons:
 p=sum((body.data.vertices[i].co for i in f.vertices),Vector())/len(f.vertices)
 if p.z>1.44:idx=3
 elif abs(p.y)>.235 and p.z>.89:idx=2 if p.z<1.18 else 1
 elif p.z<.51:idx=2
 else:idx=0
 if p.x>.075 and 1.525<p.z<1.548 and abs(p.y)<.035:idx=5
 f.material_index=idx;f.use_smooth=True
body['provenance']='CC0 Blender Human Base Meshes v1.2.0 GEO-body_female_realistic; project archive preserved. Realistic interpretation authorized 2026-11-13, no intended real-person likeness.'
# Editable tailored clothing thickness, same continuous anatomical mesh beneath all states.
body.modifiers.clear();sub=body.modifiers.new('AnatomicalRefinement','SUBSURF');sub.levels=2;sub.render_levels=2
# Build skeleton to match inspected generic female anatomy; fingers remain continuous gloves.
ad=bpy.data.armatures.new('Vanessa_EditableSkeleton');R=bpy.data.objects.new('VanessaWarfield_Rig',ad);C.objects.link(R)
bpy.context.view_layer.update()
bpy.context.view_layer.objects.active=R;R.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
spec=[('pelvis',(0,0,.90),(0,0,1.04),None),('spine',(0,0,1.04),(-.012,0,1.25),'pelvis'),('chest',(-.012,0,1.25),(-.013,0,1.42),'spine'),('neck',(-.013,0,1.42),(-.012,0,1.51),'chest'),('head',(-.012,0,1.51),(-.012,0,1.70),'neck')]
for s,l in [(1,'L'),(-1,'R')]:
 spec.extend([('upper_arm.'+l,(-.012,s*.175,1.405),(-.005,s*.285,1.15),'chest'),('forearm.'+l,(-.005,s*.285,1.15),(.015,s*.383,.94),'upper_arm.'+l),('hand.'+l,(.015,s*.383,.94),(.035,s*.418,.83),'forearm.'+l),('thigh.'+l,(0,s*.10,.91),(.014,s*.108,.50),'pelvis'),('shin.'+l,(.014,s*.108,.50),(0,s*.105,.095),'thigh.'+l),('foot.'+l,(0,s*.105,.095),(.15,s*.105,.045),'shin.'+l)])
for n,a,b,parent in spec:
 e=ad.edit_bones.new(n);e.head=a;e.tail=b
 if parent:e.parent=ad.edit_bones[parent]
bpy.ops.object.mode_set(mode='OBJECT');R['driving_pose']=0.;R['mask_on']=False;R['in_vehicle']=0.
for k in ['driving_pose','in_vehicle']:R.id_properties_ui(k).update(min=0,max=1)
R['identity_note']='One body, one face, one armature in standing/driving and masked/unmasked states.'
# Bone heat weights are generated against the actual continuous body.
bpy.ops.object.select_all(action='DESELECT');body.select_set(True);R.select_set(True);bpy.context.view_layer.objects.active=R
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
assert len(body.vertex_groups)>=15,'Bone heat failed; inspect anatomy before retry'
for m in body.modifiers:
 if m.type=='ARMATURE':m.use_deform_preserve_volume=True
def bind(o,bone='head',weights=None):
 if weights:
  for i,ww in enumerate(weights):
   for n,w in ww.items():(o.vertex_groups.get(n) or o.vertex_groups.new(name=n)).add([i],w,'REPLACE')
 else:o.vertex_groups.new(name=bone).add(list(range(len(o.data.vertices))),1,'REPLACE')
 o.parent=R;m=o.modifiers.new('VanessaEditableSkin','ARMATURE');m.object=R;m.use_deform_preserve_volume=True;return o
def visibility(o,mask=False):
 for k in ['hide_render','hide_viewport']:drive(o,k,None,'1-m' if mask else 'm',[('m',R,'mask_on')])
def convert(o,bone='head'):
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();me=bpy.data.meshes.new_from_object(o.evaluated_get(dg),depsgraph=dg);n=bpy.data.objects.new(o.name+'_Mesh',me);CURRENT.objects.link(n);n.matrix_world=o.matrix_world.copy();bpy.data.objects.remove(o,do_unlink=True);return bind(n,bone)
for i,o in enumerate(dst.objects[1:]):
 C.objects.link(o);bpy.context.view_layer.update();ow=o.matrix_world.copy();o.data=o.data.copy()
 for v in o.data.vertices:v.co=anatomypoint(ow@v.co-source_origin)
 o.matrix_world=Matrix.Identity(4);o.name='VW_Eyeball_'+str(i);o.modifiers.clear();o.data.materials.clear();o.data.materials.append(white);bind(o)
 center=sum((v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
 tubeob=tube('VW_Iris',tuple(center+Vector((.013,0,0))),tuple(center+Vector((.014,0,0))),.006,iris,N=32);bind(tubeob)
 bind(tube('VW_Pupil',tuple(center+Vector((.0142,0,0))),tuple(center+Vector((.0147,0,0))),.0025,black,N=24))
# Belt and fitted equipment; no disconnected limb primitives.
o=patch('VW_Belt',seq(64,0,2*pi),seq(2,.99,1.025),lambda a,z:(.117*cos(a),.151*sin(a),z),black,sub=0,thick=.006);bind(o,'pelvis')
bind(box('VW_SilverBuckle',(.121,0,1.005),(.013,.065,.033),silver,.005),'pelvis')
for s,l in [(1,'L'),(-1,'R')]:
 bind(box('VW_ShoulderBadge',(.015,s*.176,1.397),(.11,.07,.018),navy,.009),'upper_arm.'+l)
bind(box('VW_ChestClasp',(.143,0,1.35),(.013,.10,.032),silver,.005),'chest')
for s in [-1,1]:
 convert(path('VW_CyanCollar',[(.06,s*.06,1.44),(.115,s*.09,1.40),(.14,0,1.355)],.012,cyan),'chest')
bind(box('VW_ThighHolster',(.01,.177,.80),(.095,.05,.19),black,.02),'thigh.L')
# Continuous scalp and broad swept locks. Their hidden portions are suppressed by mask_on.
cap=patch('VW_AuburnScalp',seq(80,-pi,pi),seq(20,.01,1),lambda a,t:(-.012+.115*sin(t*(1.28+1.35*(1-cos(a))/2))*cos(a),.100*sin(t*(1.28+1.35*(1-cos(a))/2))*sin(a),1.585+.155*cos(t*(1.28+1.35*(1-cos(a))/2))),hair,sub=1,thick=.007)
bind(cap);visibility(cap)
for j in range(18):
 a=.68+(2*pi-1.36)*j/17
 def lock(u,t,a=a,j=j):
  ang=a+u*.17+.08*sin(t*5+j*.8);r=.101+.025*t+.009*sin(t*7+j)
  return (-.028+r*cos(ang),r*sin(ang),1.64-.32*t+.012*cos(t*9+j))
 ob=patch('VW_SweptLock_%02d'%j,seq(5,-1,1),seq(18),lock,hair if j%3 else hairlight,sub=1,thick=.005);bind(ob);visibility(ob)
# Short side-swept fringe, preserving the face and eye opening.
for j in range(8):
 y=-.075+j*.018
 ob=patch('VW_Forelock',seq(4,-1,1),seq(10),lambda u,t,y=y:(.025+.09*sin(t*1.5),y+.01*u+.027*t,1.738-.12*t),hair,sub=1,thick=.005);bind(ob);visibility(ob)
# Whip: squared blue front, red posterior helmet, front-only visor and twin gold ports.
M=collection('Whip_Mask');CURRENT=M;PARENT=None;GROUP='Whip'
teal=material('WH_BlueGreyShell',(.065,.20,.25),.35,.35)
helmetred=material('WH_RedHelmet',(.39,.018,.018),.30,.35)
visor=material('WH_DarkBlueVisor',(.005,.035,.09),.46,.16)
gold=material('WH_GoldPorts',(.70,.38,.035),.72,.29)
# Back helmet covers crown with a flatter square front boundary.
back=patch('WH_RedCrown',seq(56,.58,2*pi-.58),seq(20,.03,2.05),lambda a,t:(-.027+.134*sin(t)*cos(a),.117*sin(t)*sin(a),1.60+.169*cos(t)),helmetred,sub=1,thick=.008);bind(back);visibility(back,True)
# Front face is a rigid chamfered shell, not a cylindrical mask.
verts=[(.149,-.106,1.68),(.149,.106,1.68),(.166,.112,1.62),(.168,.102,1.46),(.172,.028,1.445),(.172,-.028,1.445),(.168,-.102,1.46),(.166,-.112,1.62)]
face=mesh('WH_ContinuousFaceShell',verts,[tuple(range(8))],teal,bevel=.012)
face.modifiers.new('RigidShell','SOLIDIFY').thickness=.013;bind(face);visibility(face,True)
v=[(.183,-.094,1.625),(.183,.094,1.625),(.185,.085,1.582),(.185,-.085,1.582)]
ob=mesh('WH_FrontOnlyVisor',v,[(0,1,2,3)],visor,bevel=.007);ob.modifiers.new('VisorDepth','SOLIDIFY').thickness=.004;bind(ob);visibility(ob,True)
for s in [-1,1]:
 ob=tube('WH_GoldBreathingPort',(.178,s*.047,1.515),(.199,s*.047,1.515),.018,gold,r2=.013,N=32);bind(ob);visibility(ob,True)
 for z in [1.493,1.506,1.519]:
  ob=box('WH_PortGrille',(.201,s*.047,z),(.005,.019,.0025),black,.001);bind(ob);visibility(ob,True)
 # Faceted side transition joins front shell to red cap.
 v=[(.15,s*.107,1.67),(-.055,s*.116,1.68),(-.09,s*.119,1.49),(.165,s*.102,1.46)]
 ob=mesh('WH_SideCheek',v,[(0,1,2,3)],teal,bevel=.009);ob.modifiers.new('ShellThickness','SOLIDIFY').thickness=.007;bind(ob);visibility(ob,True)
# Flared neck guard: head above, chest/shoulder weights below, same connected mesh.
def collarfn(a,t):
 r=.081+.106*t*t
 return (-.014+r*cos(a),r*1.16*sin(a),1.47-.15*t+.014*cos(a))
ob=patch('WH_ConnectedFlaredCollar',seq(64,-pi,pi),seq(12),collarfn,teal,sub=1,thick=.007)
weights=[]
for v in ob.data.vertices:
 t=max(0,min(1,(1.455-v.co.z)/.13));weights.append({'head':1-t,'chest':t})
bind(ob,weights=weights);visibility(ob,True)
for i in range(3):
 z=1.35+i*.035
 ob=convert(path('WH_CollarSegment',[(.10,-.11,z),(.13,0,z-.008),(.10,.11,z)],.003,black),'chest');visibility(ob,True)
for s in [-1,1]:
 ob=convert(path('WH_DarkHose',[(.16,s*.095,1.475),(.19,s*.15,1.36),(.16,s*.12,1.285),(.15,s*.05,1.29)],.007,black),'chest');visibility(ob,True)
ob=bind(box('WH_GoldNeckClasp',(.155,0,1.29),(.015,.085,.02),gold,.005),'chest');visibility(ob,True)
R['mask_fit_note']='Rigid head shell plus interpreted flexible collar with head/chest weights; reference cartoon geometry, not a photographed wearable.'
# Solve driving pose with fixed bone lengths, and retain a single editable pose control.
CURRENT=C;R.update_tag();bpy.context.view_layer.update()
def orient(name,start,end):
 b=R.pose.bones[name];rest=R.data.bones[name];q=(rest.tail_local-rest.head_local).rotation_difference(Vector(end)-Vector(start));mat=(q.to_matrix()@rest.matrix_local.to_3x3()).to_4x4();mat.translation=start;b.matrix=mat;bpy.context.view_layer.update()
def limb(upper,lower,target,bend):
 a=R.pose.bones[upper].head.copy();axis=(Vector(target)-a).normalized();d=min((Vector(target)-a).length,R.data.bones[upper].length+R.data.bones[lower].length-.001);target=a+axis*d
 l1=R.data.bones[upper].length;l2=R.data.bones[lower].length;x=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(max(0,l1*l1-x*x));v=Vector(bend);v=(v-axis*v.dot(axis)).normalized();el=a+axis*x+v*h;orient(upper,a,el);orient(lower,el,target)
for b in R.pose.bones:b.rotation_mode='QUATERNION'
# Seat hip world (-.49,-.37,.62); shift rest pelvis by (-.49,-.37,-.28).
for s,l in [(1,'L'),(-1,'R')]:
 limb('thigh.'+l,'shin.'+l,(.94,s*.11,.73),(1,0,.25))
 limb('upper_arm.'+l,'forearm.'+l,(.55,s*.12,1.11),(0,s*.3,-1))
 b=R.pose.bones['foot.'+l];p=b.head.copy();orient(b.name,p,p+Vector((.15,0,-.02)))
 b=R.pose.bones['hand.'+l];p=b.head.copy();orient(b.name,p,p+Vector((.06,0,.02)))
pose={b.name:list(b.rotation_quaternion) for b in R.pose.bones}
for b in R.pose.bones:
 q=pose[b.name];b.rotation_quaternion=(1,0,0,0)
 for i,val in enumerate(q):drive(b,'rotation_quaternion',i,str((1,0,0,0)[i])+'*(1-p)+'+str(val)+'*p',[('p',R,'driving_pose')])
for i,e in [(0,'-.49*v'),(1,'-.37*v'),(2,'-.28*v')]:drive(R,'location',i,e,[('v',R,'in_vehicle')])
R.parent=bpy.data.objects['Manta_Control'];R.matrix_parent_inverse=Matrix.Identity(4)
R['driving_pose']=1.;R['in_vehicle']=1.;R['mask_on']=False;R.update_tag();S.frame_set(1);bpy.context.view_layer.update()
(A/'vanessa_driving_pose_v1.json').write_text(json.dumps(pose,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Manta_V1_Assembly.blend'),compress=True)
print('VANESSA_V1_SAVED',len(C.all_objects),len(M.all_objects))
