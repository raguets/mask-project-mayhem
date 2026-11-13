import bpy
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Switchblade'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
# The floor belongs to Vehicle, not Interior: set its final height explicitly.
o=bpy.data.objects['SB_CockpitFloor'];o.location.z=.94-max(v.co.z for v in o.data.vertices)
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Switchblade_V22_Assembly.blend'),compress=True)
print('FLOOR_TOP_EXPLICITLY_94CM',o.location.z)
