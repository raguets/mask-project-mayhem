import bpy
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
bpy.ops.wm.open_mainfile(filepath=str(P/'art_source/Manta/Manta_V23_Assembly.blend'))
exec(compile((P/'art_source/Manta/diagnose_character.py').read_text(),'<diagnose-character>','exec'))
