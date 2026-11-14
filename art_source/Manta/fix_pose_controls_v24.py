import bpy,json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Manta'
R=bpy.data.objects['VanessaWarfield_Rig'];S=bpy.context.scene
if R.animation_data and R.animation_data.action:
 R.animation_data.action.use_fake_user=True
 R.animation_data.action=None
R['pose_controls_note']='Manual driving_pose/in_vehicle/mask_on; old presentation action preserved as fake-user but detached to prevent frame overrides.'
rows=[]
for pose,mask in [(0,False),(0,True),(1,False),(1,True)]:
 R['driving_pose']=float(pose);R['in_vehicle']=float(pose);R['mask_on']=mask
 for o in S.objects:o.update_tag(refresh={'OBJECT','DATA','TIME'})
 S.frame_set(2);S.frame_set(1);bpy.context.view_layer.update()
 angle=R.pose.bones['thigh.L'].rotation_quaternion.angle
 rows.append({'pose':pose,'mask':mask,'props_retained':R['driving_pose']==pose and R['mask_on']==mask,'pose_angle':angle,'mask_visible':not bpy.data.objects['WH_ContinuousFaceShell'].hide_render})
 assert R['driving_pose']==pose and R['mask_on']==mask and ((angle>.5)==bool(pose)) and ((not bpy.data.objects['WH_ContinuousFaceShell'].hide_render)==mask)
R['driving_pose']=1.;R['in_vehicle']=1.;R['mask_on']=False;R.update_tag();S.frame_set(2);S.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Manta_V24_Assembly.blend'),compress=True)
(A/'pose_controls_v24.json').write_text(json.dumps({'passed':True,'states':rows},indent=2))
