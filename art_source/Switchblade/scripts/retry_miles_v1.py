import bpy
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Switchblade'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Session_partial_Miles_V1.blend'),copy=True)
bpy.ops.wm.open_mainfile(filepath=str(A/'Switchblade_V2_Vehicle.blend'))
exec(compile((A/'scripts/build_miles_v1.py').read_text(),'<miles>','exec'))
