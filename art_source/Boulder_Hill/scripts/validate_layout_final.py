import bpy,json,math,ast
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from math import sin,cos,pi
P=Path('G:/DEV/mask-project-mayhem');S=bpy.context.scene;R=bpy.data.objects['BoulderHill_Control']
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
# Reuse inspected checker functions without executing its scene-wide top-level job.
tree=ast.parse((P/'art_source/Boulder_Hill/scripts/validate_geometry_v1.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'<checks>','exec'))
tree=ast.parse((P/'art_source/Boulder_Hill/scripts/build_base_v1.py').read_text())
fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='exit_route');exec(ast.unparse(fn).replace('* 15','* 8'))
saved_frame=S.frame_current;action=R.animation_data.action;R.animation_data.action=None
keys=['battle_mode','gate_open','thunderhawk_exit','rhino_exit'];values={k:R[k] for k in keys}
def rect(m,L,W):return [(m@Vector((x,y,0))).xy for x in [-L/2,L/2] for y in [-W/2,W/2]]
def overlaps(a,b):
    for p in [a,b]:
        for i,j in [(0,1),(0,2)]:
            edge=p[j]-p[i];axis=Vector((-edge.y,edge.x));pa=[v.dot(axis) for v in a];pb=[v.dot(axis) for v in b]
            if max(pa)<min(pb)-.001 or max(pb)<min(pa)-.001:return False
    return True
report={'method':'241 samples per route, full 9.18 x 3.19 x 4.485m Rhino road envelope. BVH against evaluated structure; 2D separating-axis test against three occupied bay envelopes. Not a continuous collision or steering simulation.','bays':[],'gate_contacts':[]}
try:
    state(battle_mode=1,gate_open=1,thunderhawk_exit=0,rhino_exit=0)
    obs=[o for o in S.objects if o.get('BH_module') in {'shop','garage','hangar','rock','pumps','sign','turret'} and o.get('BH_group')!='floor' and not o.name.startswith(('BH_HangarFloor','BH_ShopFloor'))]
    bt,verts,faces,names=combine(obs);d=json.loads((P/'art_source/Boulder_Hill/vehicle_measurements_v1.json').read_text())['assets']['Rhino'];L,W,H=[d[k] for k in ['length','width','height']]
    for bay in [15,21,27,33]:
        pts,length=exit_route(bay);hits=[];parked=[]
        for i,xyz in enumerate(pts):
            a=Vector(pts[max(0,i-1)]);b=Vector(pts[min(len(pts)-1,i+1)]);angle=math.atan2(b.y-a.y,b.x-a.x);m=Matrix.Translation(xyz)@Matrix.Rotation(angle,4,'Z')
            collisions=names_overlap(bt,names,L,W,H,m)
            if collisions:hits.append({'sample':i,'obstacles':collisions})
            rr=rect(m,L,W)
            for other in [15,21,27,33]:
                if other!=bay and overlaps(rr,rect(Matrix.Translation((-5.6,other,0)),L,W)):parked.append({'sample':i,'occupied_bay_y':other})
        report['bays'].append({'y':bay,'path_length_m':length,'structure_hits':hits,'parked_vehicle_hits':parked})
    for i in range(41):
        state(gate_open=i/40)
        fixed=[o for o in S.objects if o.get('BH_group') in {'garage_shell','shop_static','rock_static'}]
        moving=[o for o in S.objects if o.get('BH_group') in {'gate_1','gate_2'}]
        ta,va,fa,na=combine(fixed);tb,vb,fb,nb=combine(moving);pairs=sorted(set((na[a],nb[b]) for a,b in ta.overlap(tb)))
        if pairs:report['gate_contacts'].append({'progress':i/40,'pairs':pairs})
    report['invalid_drivers']=[o.name+':'+f.data_path for o in S.objects if o.animation_data for f in o.animation_data.drivers if not f.driver.is_valid]
    (P/'docs/qa/boulder_layout_final.json').write_text(json.dumps(report,indent=2))
    print('LAYOUT_FINAL',[(b['y'],len(b['structure_hits']),len(b['parked_vehicle_hits'])) for b in report['bays']],'GATE',len(report['gate_contacts']),'INVALID',report['invalid_drivers'])
finally:
    for k,v in values.items():R[k]=v
    R.animation_data.action=action;S.frame_set(saved_frame);R.update_tag();bpy.context.view_layer.update()
