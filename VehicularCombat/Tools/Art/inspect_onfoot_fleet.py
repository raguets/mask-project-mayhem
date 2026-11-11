"""Read-only rig and FBX contracts through Blender MCP."""
import bpy,json
from pathlib import Path
from io_scene_fbx import parse_fbx
root=Path('G:/DEV/mask-project-mayhem/VehicularCombat')
jobs=[('Matt','Thunderhawk_GameReady.blend','Thunderhawk/Matt_Body.fbx'),('Alex','Rhino/Rhino_GameReady_v3.blend','Rhino/AlexBody.fbx'),('Bruce','Rhino/Rhino_GameReady_v3.blend','Rhino/BruceBody.fbx'),('Hondo','Hurricane/Hurricane_GameReady.blend','Hurricane/HondoBody.fbx')]
result=[]
for name,file,fbx in jobs:
    bpy.ops.wm.open_mainfile(filepath=str(root/'SourceArt/MASK/Editable'/file))
    rigs=[o for o in bpy.context.scene.objects if o.type=='ARMATURE' and 'pelvis' in o.data.bones and name.lower() in o.name.lower()]
    rig=min(rigs,key=lambda o:abs(o.data.bones['head'].head_local.z-1.6))
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH' and any(m.type=='ARMATURE' and m.object==rig for m in o.modifiers)]
    data={'name':name,'file':file,'rig':rig.name,'unit_scale':bpy.context.scene.unit_settings.scale_length,'scale':list(rig.scale),'meshes':[o.name for o in meshes],'height':rig.data.bones['head'].tail_local.z,'bones':list(rig.pose.bones.keys()),'actions':[a.name for a in bpy.data.actions if name.lower() in a.name.lower()]}
    path=root/'SourceArt/MASK'/fbx
    if path.exists():
        tree,version=parse_fbx.parse(str(path));objects=next(e for e in tree.elems if e.id==b'Objects')
        data['fbx_models']=[{'name':e.props[1].split(b'\x00')[0].decode(),'type':e.props[2].decode(),'properties':str([(c.id,c.props) for ch in e.elems if ch.id==b'Properties70' for c in ch.elems if c.props and c.props[0] in (b'Lcl Scaling',b'Lcl Translation')])} for e in objects.elems if e.id==b'Model'][:4]
    result.append(data)
(root/'Saved/Art/onfoot/fleet-rigs.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
