import bpy
from pathlib import Path
A=Path('G:/DEV/mask-project-mayhem/art_source/Raven')
assert len(bpy.context.scene.objects)<10,'Inspect partial build before recovery'
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Raven_failed_material_initialization.blend'),copy=True,compress=True)
bpy.ops.wm.open_mainfile(filepath=str(A/'Raven_prepared_v1.blend'))
print('PREPARED_SOURCE_REOPENED')
