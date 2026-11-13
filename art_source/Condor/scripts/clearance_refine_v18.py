import bpy
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Condor'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
root=bpy.data.objects['Condor_Control'];rear=bpy.data.objects['Condor_RearWheelPivot'];f=rear.animation_data.drivers[0];f.driver.variables[0].targets[0].data_path='["transform"]';f.driver.variables[0].name='t';f.driver.expression='2.2*max(0,min(1,(t-0.36)/0.64))**2*(3-2*max(0,min(1,(t-0.36)/0.64)))'
cut=bpy.data.objects['Condor_RearWheelWell_Cutter']
for v in cut.data.vertices:
 v.co.y=.12 if v.co.y>0 else -.12
 v.co.x=-1.05+(v.co.x+1.05)*(.385/.377);v.co.z=.355+(v.co.z-.355)*(.385/.377)
bpy.context.scene.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Condor_V18_Assembly.blend'),compress=True);print('V18_WHEEL_RECESS_CLEARANCE_SAVED')
