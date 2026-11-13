import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Condor';s=bpy.context.scene;R=bpy.data.objects['BradTurner_Rig'];root=bpy.data.objects['Condor_Control']
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
code=(A/'scripts/fit_and_validate_v3.py').read_text();code=code[code.index('# Geometry checks'):].replace('validation_v3.json','validation_v7.json').replace('Condor_V3_Assembly.blend','Condor_V7_Assembly.blend').replace("['Fairing','RearCowl','Windshield','Saddle']","['Fairing','RearMonobloc','FrontCowl','Windshield','Saddle']")
exec(compile(code,'<validate_v7>','exec'))
