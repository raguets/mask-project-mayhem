import bpy,json
from pathlib import Path
R=bpy.data.objects['MilesMayhem_Rig'];root=bpy.data.objects['Switchblade_Control']
print('FILE',bpy.data.filepath,'FRAME',bpy.context.scene.frame_current)
for p in [0.,1.]:
 R['driving_pose']=p;R.update_tag();bpy.context.view_layer.update()
 print('POSE',p,[(b.name,list(b.head),list(b.tail),b.length) for b in R.pose.bones if b.name in ['spine','neck','head','thigh.L','shin.L','hand.L','foot.L','upper_arm.L','forearm.L']])
R['driving_pose']=1.;R.update_tag();bpy.context.view_layer.update()
