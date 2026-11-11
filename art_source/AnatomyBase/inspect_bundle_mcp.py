import bpy,json
from pathlib import Path
path=Path('G:/DEV/mask-project-mayhem/art_source/AnatomyBase/bundle/human_base_meshes_bundle.blend')
with bpy.data.libraries.load(str(path),link=False) as (src,dst):
    report={'objects':list(src.objects),'collections':list(src.collections),'meshes':list(src.meshes)}
print(json.dumps(report))
