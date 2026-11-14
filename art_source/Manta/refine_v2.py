import bpy,math,json
from pathlib import Path
from mathutils import Vector,Quaternion
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Manta';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
R=bpy.data.objects['VanessaWarfield_Rig'];body=bpy.data.objects['VW_ContinuousBodyAndFace']
R['driving_pose']=0.;R['in_vehicle']=0.;R.update_tag();bpy.context.view_layer.update()
for b in R.pose.bones:
 for i in range(4):
  try:R.driver_remove('pose.bones["'+b.name+'"].rotation_quaternion',i)
  except:pass
 b.rotation_quaternion=(1,0,0,0)
def segdist(p,b):
 a=b.head_local;v=b.tail_local-a;t=max(0,min(1,(p-a).dot(v)/v.length_squared));return (p-a-v*t).length
for v in body.data.vertices:
 p=v.co;side='L' if p.y>0 else 'R'
 if p.z>1.42:names=['neck','head','chest']
 elif abs(p.y)>.205 and p.z>.77:names=['chest','upper_arm.'+side,'forearm.'+side,'hand.'+side]
 elif p.z<.92:names=['pelvis','thigh.'+side,'shin.'+side,'foot.'+side]
 else:names=['pelvis','spine','chest','neck']
 ranked=sorted([(segdist(p,R.data.bones[n]),n) for n in names])[:2]
 vals=[1/(d+.015)**5 for d,n in ranked];total=sum(vals)
 for (d,n),w in zip(ranked,vals):body.vertex_groups[n].add([v.index],w/total,'REPLACE')
body['weight_method']='Regional continuous distance weights, nearest two adjacent bones, power 5; replaces failed bone heat. Pose renders required.'
# Torso/neck remain neutral; solve bent limbs against reachable pedal and wheel contacts.
def orient(name,start,end):
 b=R.pose.bones[name];rest=R.data.bones[name];q=(rest.tail_local-rest.head_local).rotation_difference(Vector(end)-Vector(start));mat=(q.to_matrix()@rest.matrix_local.to_3x3()).to_4x4();mat.translation=start;b.matrix=mat;bpy.context.view_layer.update()
def limb(upper,lower,target,bend):
 a=R.pose.bones[upper].head.copy();axis=(Vector(target)-a).normalized();d=min((Vector(target)-a).length,R.data.bones[upper].length+R.data.bones[lower].length-.001);target=a+axis*d;l1=R.data.bones[upper].length;l2=R.data.bones[lower].length;x=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(max(0,l1*l1-x*x));v=Vector(bend);v=(v-axis*v.dot(axis)).normalized();el=a+axis*x+v*h;orient(upper,a,el);orient(lower,el,target)
bpy.context.view_layer.update()
for s,l in [(1,'L'),(-1,'R')]:
 limb('thigh.'+l,'shin.'+l,(.73,s*.105,.74),(0,0,1))
 limb('upper_arm.'+l,'forearm.'+l,(.45,s*.13,1.13),(0,s*.3,-1))
 b=R.pose.bones['foot.'+l];p=b.head.copy();orient(b.name,p,p+Vector((.15,0,-.02)))
 b=R.pose.bones['hand.'+l];p=b.head.copy();orient(b.name,p,p+Vector((.035,-s*.045,.015)))
pose={b.name:list(b.rotation_quaternion) for b in R.pose.bones}
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
for b in R.pose.bones:
 q=pose[b.name];b.rotation_quaternion=(1,0,0,0)
 for i,v in enumerate(q):drive(b,'rotation_quaternion',i,str((1,0,0,0)[i])+'*(1-p)+'+str(v)+'*p',[('p',R,'driving_pose')])
R.animation_data.drivers.find('location',index=0).driver.expression='-0.40*v'
for o in bpy.data.objects:
 if o.name.startswith('MA_Pedal'):
  for v in o.data.vertices:v.co.x-=.18
# Lower reflection strength and relocate the broad key reflection away from windshield.
glass=bpy.data.materials.get('MA_SmokedGlass');bs=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['IOR'].default_value=1.32;bs.inputs['Roughness'].default_value=.065
bpy.data.objects['MA_Key'].location=(1,-4,7)
# Darker plum and less metallic glare for the large painted surfaces.
mat=bpy.data.materials.get('MA_PlumMetallic');bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.13,.006,.19,1);mat.diffuse_color=(.13,.006,.19,1);bs.inputs['Metallic'].default_value=.32
R['driving_pose']=1.;R['in_vehicle']=1.;R.update_tag();S.frame_set(1);bpy.context.view_layer.update()
(A/'vanessa_driving_pose_v2.json').write_text(json.dumps(pose,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Manta_V2_Assembly.blend'),compress=True)
print('WEIGHTED',sum(bool(v.groups) for v in body.data.vertices),'OF',len(body.data.vertices))
