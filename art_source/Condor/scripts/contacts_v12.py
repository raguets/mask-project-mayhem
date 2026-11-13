import bpy,math,json
from pathlib import Path
from mathutils import Vector,Quaternion
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Condor';s=bpy.context.scene;R=bpy.data.objects['BradTurner_Rig'];root=bpy.data.objects['Condor_Control']
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
s.frame_set(1);R['driving_pose']=1.;R.update_tag();bpy.context.view_layer.update();road={b.name:list(b.rotation_quaternion) for b in R.pose.bones}
for f in list(R.animation_data.drivers):
 if f.data_path.startswith('pose.bones'):R.driver_remove(f.data_path,f.array_index)
def orient(name,a,b):
 pb=R.pose.bones[name];rest=R.data.bones[name];q=(rest.tail_local-rest.head_local).rotation_difference(Vector(b)-Vector(a));m=(q.to_matrix()@rest.matrix_local.to_3x3()).to_4x4();m.translation=a;pb.matrix=m;bpy.context.view_layer.update()
def limb(up,low,target,bend):
 a=R.pose.bones[up].head.copy();axis=Vector(target)-a;d=axis.length;axis.normalize();l1=R.data.bones[up].length;l2=R.data.bones[low].length;d=min(d,l1+l2-.001);target=a+axis*d;x=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(max(0,l1*l1-x*x));v=Vector(bend);v=(v-axis*v.dot(axis)).normalized();el=a+axis*x+v*h;orient(up,a,el);orient(low,el,target)
poses=[]
for frame,t in [(1,0),(121,1)]:
 s.frame_set(frame)
 for b in R.pose.bones:b.rotation_quaternion=road[b.name]
 bpy.context.view_layer.update()
 for side,label in [(1,'L'),(-1,'R')]:
  limb('upper_arm.'+label,'forearm.'+label,(.56,side*.2378,1.06+.12*t),(0,side*.3,-1))
  limb('thigh.'+label,'shin.'+label,(.29,side*.30,.45+.12*t),(1,side*.7,0))
  pb=R.pose.bones['foot.'+label];a=pb.head.copy();orient(pb.name,a,a+Vector((.14,0,-.025)))
 poses.append({b.name:list(b.rotation_quaternion) for b in R.pose.bones})
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
for b in R.pose.bones:
 q0=Quaternion(poses[0][b.name]);q1=Quaternion(poses[1][b.name]);q1.make_compatible(q0)
 for i in range(4):drive(b,'rotation_quaternion',i,str((1,0,0,0)[i])+'*(1-p)+p*('+str(q0[i])+'*(1-t)+'+str(q1[i])+'*t)',[('p',R,'driving_pose'),('t',root,'transform')])
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(A/'Condor_V12_Assembly.blend'),compress=True);(A/'poses_v12.json').write_text(json.dumps(poses,indent=2));print('CONTACTS_V12_SAVED')
