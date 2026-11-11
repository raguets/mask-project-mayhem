import bpy,json
from pathlib import Path
from mathutils import Vector
S=bpy.context.scene;names=[o.name for o in S.objects if o.name.startswith(('RH_Grille','RH_Bullbar','RH_FixedBumper'))];data={'file':bpy.data.filepath,'scene':S.name,'frame':S.frame_current,'dirty':bpy.data.is_dirty,'active_review':bpy.app.driver_namespace.get('_mask_asset_review_active'),'objects':[]}
for name in names:
 o=bpy.data.objects[name];pts=[]
 if o.type in ['MESH','CURVE','FONT']:
  ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();pts=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear()
 data['objects'].append({'name':name,'type':o.type,'parent':o.parent.name if o.parent else None,'location':list(o.location),'bounds':[[min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]] if pts else None,'materials':[m.name for m in o.data.materials if m] if o.type in ['MESH','CURVE'] else []})
Path('G:/DEV/mask-project-mayhem/docs/qa/rhino_bullbar_before_v3.json').write_text(json.dumps(data,indent=2));print(json.dumps(data))
