"""Measured articulation audit; triangle overlaps are not a complete collision solver."""
import bpy, json, csv, math
from pathlib import Path
from mathutils.bvhtree import BVHTree
from mathutils import Vector
root=Path(__file__).resolve().parents[1]
s=bpy.context.scene
pairs=[]
for side in 'LR':
    for target in ('THK_Body','THK_Windshield','THK_RearGlass'):
        pairs.append(('THK_Wing_'+side,target))
    pairs.append(('THK_DoorCannon_'+side,'THK_Body'))
    pairs.append(('THK_RearPanel','THK_Reactor_'+side))
pairs += [('THK_Wing_L','THK_Wing_R'),('THK_RearPanel_TopAndSides','THK_Body'),
          ('THK_RearPanel','THK_RearStabilizer'),('THK_RearPanel','THK_FixedRearTailBand'),
          ('THK_RearPanel_TopAndSides','THK_FixedRearTailBand')]
for side in 'LR':
    pairs.append(('THK_RearPanel_TopAndSides','THK_Reactor_'+side))
    pairs.append(('THK_DoorCannon_'+side,'THK_Wing_'+side))
def tree(ob):
    e=ob.evaluated_get(bpy.context.evaluated_depsgraph_get()); me=e.to_mesh()
    t=BVHTree.FromPolygons([e.matrix_world @ v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons])
    e.to_mesh_clear(); return t
hits=[]; sampled=[]
with (root/'intersection_v8.csv').open('w',newline='',encoding='utf-8') as fp:
    w=csv.writer(fp); w.writerow(['frame','object_a','object_b','triangle_pairs'])
    for fr in range(1,194):
        s.frame_set(fr); cache={n:tree(bpy.data.objects[n]) for pair in pairs for n in pair}
        for a,b in pairs:
            count=len(cache[a].overlap(cache[b])); w.writerow([fr,a,b,count])
            if count: hits.append({'frame':fr,'a':a,'b':b,'pairs':count})
        if fr in (1,25,45,55,85,97,121,161,165,193):
            sampled.append({'frame':fr,
                'door_L_deg':math.degrees(bpy.data.objects['THK_Wing_Hinge_L'].rotation_euler.x),
                'door_R_deg':math.degrees(bpy.data.objects['THK_Wing_Hinge_R'].rotation_euler.x),
                'rear_panel_Z_m':bpy.data.objects['THK_RearPanel_Lift'].location.z,
                'rear_panel_rotation':list(bpy.data.objects['THK_RearPanel_Lift'].rotation_euler),
                'spoiler_Z_m':bpy.data.objects['THK_Spoiler_Lift'].location.z})
            sampled[-1]['cannon_deploy_L_local_Z_m']=bpy.data.objects['THK_CannonDeploy_L'].location.z
            sampled[-1]['cannon_deploy_R_local_Z_m']=bpy.data.objects['THK_CannonDeploy_R'].location.z
s.frame_set(1)
objects=[o for o in s.objects if o.type=='MESH' and o.name.startswith('THK_')]
bb=[]
for ob in objects: bb.extend([ob.matrix_world @ Vector(v) for v in ob.bound_box])
bounds={'min':[min(p[i] for p in bb) for i in range(3)],'max':[max(p[i] for p in bb) for i in range(3)]}
bounds['dimensions']=[bounds['max'][i]-bounds['min'][i] for i in range(3)]
# Endpoint identity checks actual evaluated vertex positions, including sliding cannons.
def snapshot(fr):
    s.frame_set(fr); dg=bpy.context.evaluated_depsgraph_get(); data={}
    for ob in objects:
        e=ob.evaluated_get(dg); me=e.to_mesh(); data[ob.name]=[e.matrix_world@v.co for v in me.vertices]; e.to_mesh_clear()
    return data
a,b=snapshot(1),snapshot(193)
err=max((pa-pb).length for name in a for pa,pb in zip(a[name],b[name]))
report={'frame_range':[1,193],'pairs_per_frame':len(pairs),'overlap_rows':len(hits),
        'endpoint_max_vertex_error_m':err,'road_world_bounds_m':bounds,'pose_samples':sampled,
        'tested_pairs':pairs,'overlap_examples':hits[:50],
        'limitations':['Selected pairs only','Integer frames only','Triangle surface intersection does not detect full containment','Contacts at assembly seams may be reported']}
(root/'validation_v8.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('V8_VALIDATION',json.dumps({'overlap_rows':len(hits),'endpoint_error_m':err,'dimensions':bounds['dimensions']}))
s.frame_set(1)

