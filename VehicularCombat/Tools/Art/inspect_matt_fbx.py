from pathlib import Path
from io_scene_fbx import parse_fbx
import json
file=Path('G:/DEV/mask-project-mayhem/VehicularCombat/SourceArt/MASK/Thunderhawk/MattBody.fbx')
tree,version=parse_fbx.parse(str(file));objects=next(e for e in tree.elems if e.id==b'Objects')
result=[]
for e in objects.elems:
    if e.id==b'Model':
        result.append({'name':e.props[1].split(b'\x00')[0].decode(),'type':e.props[2].decode(),'properties':str([(c.id,c.props) for ch in e.elems if ch.id==b'Properties70' for c in ch.elems if c.props and c.props[0] in (b'Lcl Scaling',b'Lcl Translation')])})
Path('G:/DEV/mask-project-mayhem/VehicularCombat/Saved/Art/onfoot/matt-fbx.json').write_text(json.dumps(result[:4],indent=2),encoding='utf-8')
print(json.dumps(result[:4]))
