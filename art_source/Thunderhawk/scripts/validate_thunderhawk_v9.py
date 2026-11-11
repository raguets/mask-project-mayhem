"""Measured V9 geometry and articulation checks in a separate Blender process."""
import bpy,json,io,contextlib,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('G:/DEV/mask-project-mayhem/art_source/Thunderhawk');S=bpy.context.scene
with contextlib.redirect_stdout(io.StringIO()):
    ns={};exec((ROOT/'scripts'/'audit_geometry_readonly.py').read_text(encoding='utf-8'),ns)
audit=ns['report'];(ROOT/'geometry_audit_v9.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
objects=[o for o in S.objects if o.type=='MESH' and o.name.startswith('THK_')]
def snapshot(fr):
    S.frame_set(fr);dg=bpy.context.evaluated_depsgraph_get();out={}
    for ob in objects:
        ev=ob.evaluated_get(dg);me=ev.to_mesh();out[ob.name]=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear()
    return out
rest=snapshot(1);back=snapshot(193)
endpoint=max((a-b).length for name in rest for a,b in zip(rest[name],back[name]))
points=[v for vv in rest.values() for v in vv]
bounds={'min':[min(p[i] for p in points) for i in range(3)],'max':[max(p[i] for p in points) for i in range(3)]}
bounds['dimensions']=[bounds['max'][i]-bounds['min'][i] for i in range(3)]
samples=[]
for fr in (1,25,45,55,65,85,97,121,151,161,165,193):
    S.frame_set(fr)
    samples.append({'frame':fr,'door_L_deg':math.degrees(bpy.data.objects['THK_Wing_Hinge_L'].rotation_euler.x),
        'door_R_deg':math.degrees(bpy.data.objects['THK_Wing_Hinge_R'].rotation_euler.x),
        'rear_Z_m':bpy.data.objects['THK_RearPanel_Lift'].location.z,
        'rear_rotation_rad':list(bpy.data.objects['THK_RearPanel_Lift'].rotation_euler),
        'spoiler_Z_m':bpy.data.objects['THK_Spoiler_Lift'].location.z,
        'cannon_local_Z_m':bpy.data.objects['THK_CannonDeploy_L'].location.z,
        'cannon_world_L':list(bpy.data.objects['THK_DoorCannon_L'].matrix_world.translation)})
pairs=[]
for side in 'LR':
    for target in ('THK_FrontFenderCrown_'+side,'THK_FrontQuarterSkin_'+side,'THK_RearFenderCrown_'+side,
                   'THK_RearQuarterSkin_'+side,'THK_C_Pillar_'+side,'THK_Windshield','THK_RearGlass',
                   'THK_FrontRoofHeader','THK_RearRoofHeader','THK_RoofSpine'):
        pairs.append(('THK_DoorShell_'+side,target))
    pairs.extend([('THK_RearPanel','THK_Reactor_'+side),('THK_DoorCannon_'+side,'THK_DoorShell_'+side)])
    for target in ('THK_Windshield','THK_WindshieldFrame','THK_FrontRoofHeader','THK_FrontFenderCrown_'+side):
        pairs.append(('THK_DoorAFrame_'+side,target))
pairs.extend([('THK_DoorShell_L','THK_DoorShell_R'),('THK_RearPanel','THK_FixedTailBand'),('THK_RearStabilizer','THK_RearGlass')])
S.frame_set(1);dg=bpy.context.evaluated_depsgraph_get();local={}
names=sorted(set(n for pair in pairs for n in pair))
for name in names:
    ob=bpy.data.objects[name];ev=ob.evaluated_get(dg);me=ev.to_mesh()
    local[name]=([v.co.copy() for v in me.vertices],[tuple(p.vertices) for p in me.polygons]);ev.to_mesh_clear()
hits=[];frames=[1+i*.5 for i in range(385)]
for idx,fr in enumerate(frames):
    S.frame_set(int(fr),subframe=fr-int(fr));trees={}
    for name in names:
        verts,faces=local[name];mw=bpy.data.objects[name].matrix_world
        trees[name]=BVHTree.FromPolygons([mw@v for v in verts],faces)
    for a,b in pairs:
        count=len(trees[a].overlap(trees[b]))
        if count:hits.append({'frame':fr,'a':a,'b':b,'triangle_pairs':count})
    if idx%80==0:print('THK9_COLLISION_PROGRESS',idx,len(frames),flush=True)
summary={}
for row in hits:
    key=row['a']+' / '+row['b'];summary[key]=summary.get(key,0)+1
report={'source':bpy.data.filepath,'frame_range':[1,193],'fps':24,'dimensions_estimated':True,
        'road_bounds_m':bounds,'endpoint_max_evaluated_vertex_error_m':endpoint,'pose_samples':samples,
        'geometry':{'base':audit['totals'],'evaluated':audit['evaluated_totals']},
        'collision_sample_count':len(frames),'collision_step_frames':.5,'tested_pairs':pairs,
        'intersection_rows':len(hits),'intersection_pair_summary':summary,'intersection_examples':hits[:100],
        'limitations':['Selected pairs only','Surface triangle intersections, not a solid-volume collision solver',
                      'Half-frame sampling, not mathematically continuous collision detection','No gameplay physics or multiplayer validation']}
(ROOT/'validation_v9.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
(ROOT/'intersection_v9.json').write_text(json.dumps(hits,indent=2),encoding='utf-8')
S.frame_set(1)
print('THK9_VALIDATION',json.dumps({k:report[k] for k in ('endpoint_max_evaluated_vertex_error_m','intersection_rows','intersection_pair_summary','road_bounds_m')}),flush=True)
