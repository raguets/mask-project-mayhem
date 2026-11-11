import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
from math import pi,sqrt,cos,sin,exp
P=Path('G:/DEV/mask-project-mayhem');T=P/'art_source/Thunderhawk';s=bpy.context.scene;r=bpy.data.objects['MattTrakker_Rig'];char=bpy.data.collections['MT11_Character']
source=(P/'art_source/Matt_Trakker/final_review_corrections_v4.py').read_text()
exec(compile(source[source.index('# Restore a stable rest-space'):],'final_review_corrections_v4.py','exec'))
