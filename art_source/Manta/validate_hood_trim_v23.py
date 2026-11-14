import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
A=Path('G:/DEV/mask-project-mayhem/art_source/Manta');S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
def surf(n):
 o=bpy.data.objects[n];dg=bpy.context.evaluated_depsgraph_get();e=o.evaluated_get(dg);m=e.to_mesh();v=[e.matrix_world@p.co for p in m.vertices];f=[list(p.vertices) for p in m.polygons];e.to_mesh_clear();return BVHTree.FromPolygons(v,f)
hood=['MA_FixedHoodShoulder_L','MA_FixedHoodShoulder_R']
trims=[o.name for o in bpy.data.objects if o.name.startswith('MA_CircularArchLip')]
pairs=[('MA_SlidingHoodSkin',n) for n in hood]+[(w,t) for w in ['MA_FrontWheel_-1_Tire','MA_FrontWheel_1_Tire','MA_RearWheel_-1_Tire','MA_RearWheel_1_Tire'] for t in trims]
hits={a+' / '+b:[] for a,b in pairs}
for i in range(241):
 f=1+i/2;S.frame_set(int(f),subframe=f%1);bpy.context.view_layer.update();ss={n:surf(n) for n in set(n for pair in pairs for n in pair)}
 for a,b in pairs:
  count=len(ss[a].overlap(ss[b]))
  if count:hits[a+' / '+b].append({'frame':f,'triangles':count})
S.frame_set(1);(A/'hood_trim_validation_v23.json').write_text(json.dumps({'source':bpy.data.filepath,'phases':241,'overlaps':hits},indent=2));print(json.dumps({k:len(v) for k,v in hits.items() if v}))
