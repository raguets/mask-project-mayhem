from pathlib import Path
A=Path('G:/DEV/mask-project-mayhem/art_source/Raven')
code=(A/'scripts/audit_v15.py').read_text(encoding='utf-8').replace('v15','v16').replace('V15','V16')
# audit_v15 loads v14 dynamically: ensure its report destination is also current.
code=code.replace("exec(compile(code,'<audit-v16>','exec'))", "exec(compile(code,'<base-audit-v16>','exec'))")
exec(compile(code,'<audit-v16>','exec'))
import bpy,json
from mathutils.bvhtree import BVHTree
S=bpy.context.scene;saved=S.frame_current;contacts=[]
def tree(name):
    ob=bpy.data.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get());me=ob.to_mesh();pts=[ob.matrix_world@v.co for v in me.vertices];faces=[tuple(p.vertices) for p in me.polygons];ob.to_mesh_clear();return BVHTree.FromPolygons(pts,faces)
pairs=[(a+s,b) for s in ['L','R'] for a in ['RV_DoorRoofWing_','RV_DoorGlassRoof_RoundedBend_'] for b in ['RV_Windshield','RV_RearHatchGlass','RV_RoofTarga']]
for frame in list(range(34,122,3))+[151]:
    S.frame_set(frame);bpy.context.view_layer.update();cache={n:tree(n) for pair in pairs for n in pair}
    for a,b in pairs:
        count=len(cache[a].overlap(cache[b]))
        if count:contacts.append({'frame':frame,'a':a,'b':b,'triangle_pairs':count})
S.frame_set(saved);bpy.context.view_layer.update()
p=A/'validation_v16.json';report=json.loads(p.read_text());report['data']['new_roof_motion_contacts']=contacts
report['checks']['new_roof_parts_clear_fixed_glass_during_sampled_motion']=not contacts
report['method']='Evaluated meshes:33 tire/body motion states;31 moving-roof/fixed-glass states (rest mating edges excluded). Rigid hood distances, limits and parent relationships. Rendered inspection separate; not an exhaustive swept-volume check.'
report['passed']=all(report['checks'].values());p.write_text(json.dumps(report,indent=2));print('V16_ROOF_CLEARANCE',not contacts,contacts[:8])
