import bpy,math,json
import numpy as np
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Manta';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
R=bpy.data.objects['VanessaWarfield_Rig'];body=bpy.data.objects['VW_ContinuousBodyAndFace'];R['driving_pose']=0.;R['in_vehicle']=0.;R.update_tag();bpy.context.view_layer.update()
# Remove unused first-attempt collections, keeping the actual scene organization explicit.
for c in list(bpy.data.collections):
 if len(c.objects)==0 and c.name in ['CB_Character','Collection','Manta_Vehicle']:bpy.data.collections.remove(c)
bpy.data.collections['Manta_Vehicle.001'].name='Manta_Vehicle'
# Smooth the full weight field over real connected topology to eliminate region seams.
N=len(body.data.vertices);G=len(body.vertex_groups);W=np.zeros((N,G),dtype=np.float64)
for v in body.data.vertices:
 for g in v.groups:W[v.index,g.group]=g.weight
edges=np.array([tuple(e.vertices) for e in body.data.edges]);a=edges[:,0];b=edges[:,1];deg=np.bincount(np.concatenate([a,b]),minlength=N);den=np.maximum(1,deg)[:,None]
for k in range(45):
 avg=np.zeros_like(W);np.add.at(avg,a,W[b]);np.add.at(avg,b,W[a]);W=.50*W+.50*avg/den
W/=np.maximum(1e-12,W.sum(axis=1))[:,None]
for g in body.vertex_groups:g.remove(list(range(N)))
for i,ww in enumerate(W):
 for j in np.flatnonzero(ww>.0001):body.vertex_groups[int(j)].add([i],float(ww[j]),'REPLACE')
body['weight_method']='Regional segment weights with 45 iterations of topology smoothing. One continuous female CC0 mesh; no replacement pose meshes.'
for f in body.data.polygons:
 p=sum((body.data.vertices[i].co for i in f.vertices),Vector())/len(f.vertices)
 idx=3 if p.z>1.44 else (2 if abs(p.y)>.23 and .74<p.z<1.18 else (1 if abs(p.y)>.22 and 1.18<=p.z<1.39 else (2 if p.z<.51 else 0)))
 if p.x>.13 and 1.510<p.z<1.526 and abs(p.y)<.027:idx=5
 f.material_index=idx
# Replace mis-parented eye imports with independent anatomical eyeballs in head space.
for o in list(bpy.data.objects):
 if o.name.startswith(('VW_Eyeball','VW_Iris','VW_Pupil')):bpy.data.objects.remove(o,do_unlink=True)
C=bpy.data.collections['Vanessa_Character'];CURRENT=C;PARENT=None
def bind(o,bone='head'):
 o.vertex_groups.new(name=bone).add(list(range(len(o.data.vertices))),1,'REPLACE');o.parent=R;m=o.modifiers.new('VanessaEditableSkin','ARMATURE');m.object=R;m.use_deform_preserve_volume=True;return o
def visibility(o,mask=False):
 for k in ['hide_render','hide_viewport']:drive(o,k,None,'1-m' if mask else 'm',[('m',R,'mask_on')])
white=bpy.data.materials['VW_EyeWhite'];iris=bpy.data.materials['VW_GreenIris'];black=bpy.data.materials['VW_BlackLeather'];hair=bpy.data.materials['VW_AuburnHair']
for s in [-1,1]:
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=1,location=(0,0,0));o=bpy.context.object;o.name='VW_Eyeball_'+str(s)
 for cc in list(o.users_collection):cc.objects.unlink(o)
 C.objects.link(o)
 for v in o.data.vertices:v.co=Vector((.123,s*.034,1.588))+v.co*.013
 o.data.materials.append(white)
 for f in o.data.polygons:f.use_smooth=True
 bind(o)
 bind(tube('VW_Iris',(.135,s*.034,1.588),(.136,s*.034,1.588),.0055,iris,N=32))
 bind(tube('VW_Pupil',(.1362,s*.034,1.588),(.1367,s*.034,1.588),.0025,black,N=24))
 # Eyebrow strip follows brow bone, no floating dots.
 pts=[(.123,s*(.016+.008*i),1.611+.003*sin(i*pi/4)) for i in range(5)]
 ob=path('VW_AuburnBrow',pts,.0025,hair)
 dg=bpy.context.evaluated_depsgraph_get();me=bpy.data.meshes.new_from_object(ob.evaluated_get(dg),depsgraph=dg);n=bpy.data.objects.new(ob.name+'_Mesh',me);C.objects.link(n);bpy.data.objects.remove(ob,do_unlink=True);bind(n)
# Fuller hairline, swept crown, broad asymmetric locks rather than a bare forehead strip.
for o in list(C.objects):
 if o.name.startswith(('VW_AuburnScalp','VW_Forelock')):bpy.data.objects.remove(o,do_unlink=True)
ob=patch('VW_ContinuousHairCap',seq(80,-pi,pi),seq(24,.01,1),lambda a,t:(-.008+.145*sin(t*(1.20+1.25*(1-cos(a))/2))*cos(a),.112*sin(t*(1.20+1.25*(1-cos(a))/2))*sin(a),1.586+.157*cos(t*(1.20+1.25*(1-cos(a))/2))),hair,sub=1,thick=.006);bind(ob);visibility(ob)
for j in range(7):
 yy=-.082+j*.023
 ob=patch('VW_SweptFringe',seq(6,-1,1),seq(16),lambda u,t,yy=yy:(.015+.125*sin(t*1.32),yy+.013*u+.025*t,1.748-.115*t+.008*sin(t*pi)),hair,sub=1,thick=.004);bind(ob);visibility(ob)
# Keep the nose beneath Whip and close the crown opening.
M=bpy.data.collections['Whip_Mask'];CURRENT=M
for o in M.objects:
 if o.type=='MESH' and o.name.startswith(('WH_ContinuousFaceShell','WH_FrontOnlyVisor','WH_GoldBreathingPort','WH_PortGrille')):
  for v in o.data.vertices:v.co.x+=.025
old=bpy.data.objects['WH_RedCrown'];bpy.data.objects.remove(old,do_unlink=True)
ob=patch('WH_ClosedRedCrown',seq(72,-pi,pi),seq(24,.01,1),lambda a,t:(-.020+.148*sin(t*(1.20+.95*(1-cos(a))/2))*cos(a),.127*sin(t*(1.20+.95*(1-cos(a))/2))*sin(a),1.60+.18*cos(t*(1.20+.95*(1-cos(a))/2))),bpy.data.materials['WH_RedHelmet'],sub=1,thick=.008);bind(ob);visibility(ob,True)
# Finish the material/lighting correction from V2 using the actual assigned materials.
glass=bpy.data.objects['MA_Windshield'].data.materials[0];bs=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['IOR'].default_value=1.32;bs.inputs['Roughness'].default_value=.065
bpy.data.objects['MA_Key'].location=(1,-4,7)
mat=bpy.data.objects['MA_MainBody'].data.materials[0];bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.13,.006,.19,1);mat.diffuse_color=(.13,.006,.19,1);bs.inputs['Metallic'].default_value=.32
# Store the main wings wholly below the floor; retain wheel hierarchy.
for s in [-1,1]:
 wing=bpy.data.objects['MA_UnderbodyWingPivot_'+str(s)]
 for o in wing.children:
  if o.name.startswith('MA_RearWheelCarrier'):continue
  if o.type=='MESH':
   for v in o.data.vertices:v.co.z-=.065
  elif o.type=='CURVE':
   o.location.z-=.065
 # A more aft hidden pivot gives the rear wheel genuine outward travel on the wing.
 newx=-1.80;delta=newx-wing.location.x;wing.location.x=newx
 for o in wing.children:o.matrix_parent_inverse.translation.x-=delta
# Save coherent default state, retain all prior iterations.
R['driving_pose']=1.;R['in_vehicle']=1.;R['mask_on']=False;R.update_tag();S.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Manta_V3_Assembly.blend'),compress=True)
print('V3_SAVED',len(bpy.data.objects))
