import bpy,json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
s=bpy.context.scene
r=bpy.data.objects.get('MattTrakker_Rig')
data={'file':bpy.data.filepath,'scene':s.name,'collections':[c.name for c in bpy.data.collections]}
if r:
    data['rig']={'location':list(r.location),'properties':dict(r.items()),'bones':[{ 'name':b.name,'head':list(b.head_local),'tail':list(b.tail_local)} for b in r.data.bones]}
    data['character_objects']=[{'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'vertices':len(o.data.vertices) if o.type=='MESH' else None,'materials':[m.name for m in o.data.materials if m] if o.type=='MESH' else []} for o in bpy.data.collections['MT11_Character'].all_objects]
(P/'docs/qa/rhino_source_inspection.json').write_text(json.dumps(data,indent=2))
print('RHINO_SOURCE_INSPECTED',bpy.data.filepath)
