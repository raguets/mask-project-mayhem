"""Run through Blender MCP. Preserve the open session; inspect existing game rigs."""
import bpy, json
from pathlib import Path
root=Path('G:/DEV/mask-project-mayhem/VehicularCombat')
out=root/'Saved/Art/onfoot';out.mkdir(parents=True,exist_ok=True)
if not (out/'session-before.blend').exists():
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'session-before.blend'),copy=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'SourceArt/MASK/Editable/Thunderhawk_GameReady.blend'))
report={'file':bpy.data.filepath,'rigs':[],'actions':[]}
for o in bpy.context.scene.objects:
    if o.type!='ARMATURE':continue
    report['rigs'].append({'name':o.name,'scale':list(o.scale),'location':list(o.location),
        'bones':[{'name':b.name,'head':list(b.head_local),'tail':list(b.tail_local),'parent':b.parent.name if b.parent else None} for b in o.data.bones],
        'action':o.animation_data.action.name if o.animation_data and o.animation_data.action else None})
report['actions']=[{'name':a.name,'range':list(a.frame_range)} for a in bpy.data.actions]
(out/'rigs.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
