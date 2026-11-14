import bpy
from pathlib import Path
S=bpy.context.scene;A=Path('G:/DEV/mask-project-mayhem/art_source/Manta')
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
for sign in [-1,1]:
 o=bpy.data.objects['MA_RearBoardUpperStage_'+str(sign)];f=o.animation_data.drivers.find('location',index=2);f.driver.expression=f.driver.expression.replace('.47*','.385*')
o=bpy.data.objects['MA_TripleReactorTravel'];o.animation_data.drivers.find('location',index=0).driver.expression='-.02*t-.40*min(1,max(0,(t-.65)/.35))'
S.frame_set(121);S.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Manta_V16_Assembly.blend'),compress=True)
print('V16_REAR_SUPPORT_CLEARANCE_SAVED')
