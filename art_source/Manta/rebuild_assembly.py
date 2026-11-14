import bpy
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Manta'
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Manta_V1_Assembly_debug.blend'),compress=True)
bpy.ops.wm.open_mainfile(filepath=str(A/'Manta_V1_Vehicle.blend'))
exec(compile((A/'build_vanessa_v1.py').read_text(),'<vanessa>','exec'))
exec(compile((A/'fix_drivers_v2.py').read_text(),'<fix>','exec'))
