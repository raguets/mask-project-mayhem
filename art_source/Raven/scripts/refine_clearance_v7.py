"""Continuous overlapping mechanisms, with a reserved swept volume for the hood."""
import bpy,math
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Raven';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
assert not (A/'Raven_V7_Assembly.blend').exists()
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(encoding='utf-8'),'<geometry>','exec'))
root=bpy.data.objects['Raven_Control'];hood=bpy.data.objects['RV_Hood_LongitudinalPivot'];S.frame_set(1)
h='min(1,t*2)';w='(0.15*t if t<0.5 else 0.075+0.925*(2*t-1))'
drive(hood,'rotation_euler',0,f'3.141592653589793*{h}',[('t',root,'transform')])
drive(hood,'location',2,f'.71+.50*sin(3.141592653589793*{h})',[('t',root,'transform')])
hood['mechanism_estimate']='Hood and wheels start together; hood finishes its flip halfway through the shared interval. Estimated0.50m cam lift reserves swept clearance. Rates and hidden linkage are interpretations, not measured toy kinematics.'
for sg,side in [(1,'L'),(-1,'R')]:
    wheel=bpy.data.objects['RV_FrontWheelFold_'+side]
    drive(wheel,'rotation_euler',0,f'{sg*pi/2}*{w}',[('t',root,'transform')])
    drive(wheel,'location',2,f'.4125+.35*sin(3.141592653589793*{w})',[('t',root,'transform')])
    wheel['mechanism_estimate']='Continuous fold with estimated0.35m temporary carrier lift; same wheel persists. Begins with other mechanisms, no replacement meshes.'
root['hover_height']=0.;R=bpy.data.objects['CalhounBurns_Rig'];R['in_vehicle']=1.;R['driving_pose']=1.;R['mask_on']=False;R.update_tag();S.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Raven_V7_Assembly.blend'),compress=True)
print('RAVEN_V7_CONTINUOUS_CLEARANCE_STUDY_SAVED')
