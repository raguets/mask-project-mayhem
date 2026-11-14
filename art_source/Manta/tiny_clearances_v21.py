import bpy
from pathlib import Path
A=Path('G:/DEV/mask-project-mayhem/art_source/Manta');S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
for sign in [-1,1]:bpy.data.objects['MA_FrontWheelFlip_'+str(sign)].animation_data.drivers.find('location',index=2).driver.expression='.34-.012*sin(3.141592653589793*t)'
# The slider underside is flat across its width. Match its actual lower envelope,
# rather than the cambered upper skin, to keep the fixed lower nose out of its way.
o=bpy.data.objects['MA_IntegratedRoundedNose']
flat_z=.540-.035*(.54/.70)**2-.027-.0015
for v in o.data.vertices:
 if v.co.z>.30 and abs(v.co.y)<=.5401:v.co.z=flat_z
o.data.update();o.update_tag();S.frame_set(121);S.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Manta_V21_Assembly.blend'),compress=True)
print('V21_SMALL_CLEARANCES_SAVED',flat_z)
