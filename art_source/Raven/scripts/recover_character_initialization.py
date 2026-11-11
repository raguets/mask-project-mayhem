import bpy
from pathlib import Path
A=Path('G:/DEV/mask-project-mayhem/art_source/Raven')
assert bpy.data.objects.get('CalhounBurns_Rig')
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Raven_failed_character_initialization.blend'),copy=True,compress=True)
bpy.ops.wm.open_mainfile(filepath=str(A/'Raven_V1_with_character_basis.blend'))
print('BASIS_CHECKPOINT_REOPENED')
