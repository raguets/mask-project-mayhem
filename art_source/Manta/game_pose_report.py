import bpy,json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');F=P/'art_source/GameReady/Manta/Manta_GameReady.blend'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
bpy.ops.wm.open_mainfile(filepath=str(F));R=bpy.data.objects['Vanessa_GameRig'];S=bpy.context.scene;rows=[]
for label in ['Standing','Driving','Transform']:
 R.data.pose_position='POSE';R.animation_data.action=bpy.data.actions['Vanessa_'+label];S.frame_set(2);S.frame_set(1);bpy.context.view_layer.update()
 rows.append({'clip':label,'thigh_angle':R.pose.bones['thigh.L'].rotation_quaternion.angle,'hand':list(R.pose.bones['hand.L'].head)})
r={'passed':rows[0]['thigh_angle']<.01 and rows[1]['thigh_angle']>.5,'clips':rows}
(P/'art_source/Manta/game_pose_report.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
bpy.ops.wm.open_mainfile(filepath=str(P/'art_source/Manta/Manta_V24_Assembly.blend'))
