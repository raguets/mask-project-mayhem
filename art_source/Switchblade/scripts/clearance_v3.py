import bpy
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Switchblade'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
root=bpy.data.objects['Switchblade_Control'];R=bpy.data.objects['MilesMayhem_Rig']
for side in [-1,1]:
 yaw=bpy.data.objects['SB_WingSweep_'+str(side)]
 drive(yaw,'location',1,str(side)+'*(0.70+0.48*sin(3.14159265359*t))',[('t',root,'transform')])
 skid=bpy.data.objects['SB_SkidToCannon_'+str(side)]
 drive(skid,'location',2,'1.13+0.24*t',[('t',root,'transform')])
drive(R,'location',0,'0.35*v',[('v',R,'in_vehicle')])
for o in bpy.data.collections['Switchblade_Interior'].all_objects:
 if any(k in o.name for k in ['SeatBase','SeatBack','HeadRest','SeatUpholstery']):o.location.x+=.10
root['kinematic_estimates']='Wing hinges move outward up to0.48m during roll/sweep to clear tail; skid/cannon hinges rise0.24m. Hidden linkage interpretation, not official toy dimensions.'
bpy.context.scene.frame_set(1);root.update_tag();R.update_tag();bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Switchblade_V3_Assembly.blend'),compress=True)
print('CLEARANCE_V3_SAVED')
