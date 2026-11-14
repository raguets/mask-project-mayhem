"""Compare evaluated source road bounds to the ACTUAL baked game-ready meshes."""
import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Manta'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
bpy.ops.wm.open_mainfile(filepath=str(A/'Manta_V24_Assembly.blend'))
S=bpy.context.scene;S.frame_set(2);S.frame_set(1);bpy.context.view_layer.update();groups={}
for o in S.objects:
 if o.type not in {'MESH','CURVE','FONT'} or not any(c.name in ('Manta_Vehicle','Manta_Interior') for c in o.users_collection) or o.hide_render:continue
 owner=o.parent
 while owner and owner.type!='EMPTY':owner=owner.parent
 name=owner.name if owner else 'Manta_Control'
 wheel=next((letter+side for axle,letter in [('Front','F'),('Rear','R')] for sign,side in [(1,'L'),(-1,'R')] if o.name.startswith(f'MA_{axle}Wheel_{sign}_')),None)
 glass=any(s.material and 'Glass' in s.material.name for s in o.material_slots)
 key='SM_MA_'+wheel if wheel else 'SM_'+name+('_Glass' if glass else '')
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();groups.setdefault(key,[]).extend(ev.matrix_world@v.co for v in me.vertices);ev.to_mesh_clear()
def bounds(v):return [min(p[i] for p in v) for i in range(3)]+[max(p[i] for p in v) for i in range(3)]
expected={k:bounds(v) for k,v in groups.items()}
bpy.ops.wm.open_mainfile(filepath=str(P/'art_source/GameReady/Manta/Manta_GameReady.blend'))
rows=[]
for k,v in expected.items():
 o=bpy.data.objects[k];actual=bounds([o.matrix_world@p.co for p in o.data.vertices]);delta=max(abs(a-b) for a,b in zip(actual,v));rows.append({'part':k,'max_bound_delta_m':delta,'source':v,'baked':actual})
r={'passed':all(x['max_bound_delta_m']<.025 for x in rows),'parts':rows}
(A/'export_geometry_validation.json').write_text(json.dumps(r,indent=2));print(json.dumps({'passed':r['passed'],'largest':sorted([(x['part'],x['max_bound_delta_m']) for x in rows],key=lambda x:-x[1])[:5]}))
bpy.ops.wm.open_mainfile(filepath=str(A/'Manta_V24_Assembly.blend'))
