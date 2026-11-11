"""Read-only inventory of the Rhino source opened through Blender MCP."""
import bpy,json
from pathlib import Path
from mathutils import Vector
scene=bpy.context.scene
result={'file':bpy.data.filepath,'scene':scene.name,'frame':scene.frame_current,'collections':{},'objects':[],'rigs':[]}
for collection in bpy.data.collections:
    result['collections'][collection.name]={'objects':len(collection.objects),'hidden':collection.hide_render}
for o in scene.objects:
    if o.type not in {'MESH','EMPTY','ARMATURE'}:continue
    record={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'collections':[c.name for c in o.users_collection],
        'hidden':o.hide_render,'location':list(o.matrix_world.translation),'dimensions':list(o.dimensions),'properties':{k:str(o[k]) for k in o.keys() if k!='_RNA_UI'}}
    if o.type=='MESH':
        record.update(vertices=len(o.data.vertices),materials=[s.material.name if s.material else None for s in o.material_slots],
            modifiers=[{'type':m.type,'name':m.name} for m in o.modifiers],groups=[g.name for g in o.vertex_groups])
    if o.type=='ARMATURE':result['rigs'].append({'name':o.name,'bones':[b.name for b in o.data.bones]})
    result['objects'].append(record)
Path('G:/DEV/mask-project-mayhem/VehicularCombat/Saved/Art/rhino-source-audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('RHINO_AUDIT_COMPLETE',len(result['objects']))
