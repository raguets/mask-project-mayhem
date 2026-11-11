import bpy,json
from pathlib import Path
from mathutils import Vector
A=Path('G:/DEV/mask-project-mayhem/art_source/Raven');S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
rows=[]
for o in S.objects:
    if not o.name.startswith('RV_'):continue
    if o.type not in ['MESH','EMPTY','CURVE']:continue
    if not any(k in o.name for k in ['Hood','Front','Dashboard','Cabin','Tunnel','Pedal','Floor','Reactor','Door','Fender','Nose','RimGun','HubCannon','Undertray','Roof','Windshield','Deck','Marker','Sill']):continue
    ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());pts=[ev.matrix_world@Vector(c) for c in ev.bound_box] if o.type!='EMPTY' else [ev.matrix_world.translation]
    row={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'location':list(o.location),'rotation':list(o.rotation_euler),'bounds':{'min':[min(p[i] for p in pts) for i in range(3)],'max':[max(p[i] for p in pts) for i in range(3)]},'modifiers':[m.type for m in o.modifiers]}
    if o.type=='MESH':row['vertices']=len(o.data.vertices)
    rows.append(row)
root=bpy.data.objects['Raven_Control'];report={'file':bpy.data.filepath,'dirty':bpy.data.is_dirty,'frame':S.frame_current,'selected':[o.name for o in bpy.context.selected_objects],'root_properties':dict(root.items()),'objects':rows}
(A/'inspection-before-v12.json').write_text(json.dumps(report,indent=2,default=str));print(json.dumps({'file':bpy.data.filepath,'dirty':bpy.data.is_dirty,'frame':S.frame_current,'objects_audited':len(rows),'root':dict(root.items())},default=str))
