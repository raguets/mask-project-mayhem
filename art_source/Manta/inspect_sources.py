import bpy,json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
bpy.ops.wm.save_as_mainfile(filepath=str(P/'art_source/Manta/session_before_manta.blend'))
with bpy.data.libraries.load(str(P/'art_source/AnatomyBase/bundle/human_base_meshes_bundle.blend')) as (s,d):
 print('FEMALE SOURCES', [n for n in s.objects if 'female' in n.lower()])
 d.objects=[n for n in s.objects if 'female' in n.lower() and 'realistic' in n.lower()]
for o in d.objects:
 if not o:continue
 print(o.name, o.type, len(o.data.vertices) if o.type=='MESH' else 0, [list(v) for v in o.bound_box],list(o.location), list(o.rotation_euler))
with bpy.data.libraries.load(str(P/'art_source/Calhoun_Burns/CalhounBurns_V2.blend')) as (s,d):
 d.collections=['CB_Character']
C=d.collections[0];bpy.context.scene.collection.children.link(C)
for o in C.all_objects:
 if o.type=='ARMATURE': print('RIG',o.name,[(b.name,list(b.head_local),list(b.tail_local)) for b in o.data.bones])
 elif o.type=='MESH':print('MESH',o.name,len(o.data.vertices),list(o.dimensions))
