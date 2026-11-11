"""Conservative full vehicle envelopes against evaluated obstacle surfaces.
Run only after the render queue restores the scene. Not a dynamics simulation.
"""
import bpy,json,math,time
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
P=Path('G:/DEV/mask-project-mayhem');S=bpy.context.scene;R=bpy.data.objects['BoulderHill_Control']
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
saved_frame=S.frame_current
saved_action=R.animation_data.action;R.animation_data.action=None
keys=['battle_mode','gate_open','thunderhawk_exit','rhino_exit'];values={k:R[k] for k in keys}
def state(**kw):
    for k,v in kw.items():R[k]=v
    R.update_tag();bpy.context.view_layer.update()
def combine(objects):
    dg=bpy.context.evaluated_depsgraph_get();verts=[];faces=[];names=[]
    for o in objects:
        if o.type not in {'MESH','CURVE','FONT'}:continue
        e=o.evaluated_get(dg);m=e.to_mesh()
        if not m:continue
        n=len(verts);verts.extend(e.matrix_world@v.co for v in m.vertices)
        faces.extend(tuple(n+i for i in f.vertices) for f in m.polygons);names.extend([o.name]*len(m.polygons));e.to_mesh_clear()
    return BVHTree.FromPolygons(verts,faces,all_triangles=False,epsilon=.001),verts,faces,names
BOXF=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
def boxverts(L,W,H,matrix):return [matrix@Vector((x,y,z)) for x in [-L/2,L/2] for y in [-W/2,W/2] for z in [.06,H]]
def boxtree(L,W,H,matrix):return BVHTree.FromPolygons(boxverts(L,W,H,matrix),BOXF)
def names_overlap(tree,names,L,W,H,matrix):
    # Box faces use the vertex order x,y,z; the topology below is a proper cube.
    bv=boxverts(L,W,H,matrix)
    f=[(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)]
    bt=BVHTree.FromPolygons(bv,f)
    return sorted(set(names[i] for i,j in tree.overlap(bt)))
report={'method':'Evaluated obstacle surfaces versus conservative full road-vehicle rectangular envelopes; excludes floor contact, excludes route steering dynamics. Surface-crossing check, with separate parked rectangle and headroom checks.','route_samples':{},'mechanism_contacts':{}}
try:
    state(battle_mode=1,gate_open=1,thunderhawk_exit=0,rhino_exit=0)
    obstacles=[o for o in S.objects if o.get('BH_module') in {'shop','garage','hangar','rock','pumps','sign','turret'} and o.get('BH_group') not in {'floor'} and not o.name.startswith(('BH_HangarFloor','BH_ShopFloor'))]
    tree,vs,fs,names=combine(obstacles)
    measurements=json.loads((P/'art_source/Boulder_Hill/vehicle_measurements_v1.json').read_text())['assets']
    for label,key in [('Thunderhawk','thunderhawk_exit'),('Rhino','rhino_exit')]:
        d=measurements[label];actor=bpy.data.objects['BH_'+label+'_PathRoot'];hits=[];positions=[]
        for i in range(241):
            state(**{key:i/240});m=actor.matrix_world.copy();positions.append(list(m.translation));collisions=names_overlap(tree,names,d['length'],d['width'],d['height'],m)
            if collisions:hits.append({'sample':i,'progress':i/240,'center':list(m.translation),'obstacles':collisions})
        report['route_samples'][label]={'count':241,'collisions':hits,'start':positions[0],'end':positions[-1]}
        state(**{key:0})
    # Additional four bay checks with the largest current vehicle envelope.
    d=measurements['Rhino'];report['parking_bays']=[]
    for y in [15,21,27,33]:
        m=Matrix.Translation((-5.6,y,0));report['parking_bays'].append({'center':[-5.6,y,0],'vehicle':'Rhino envelope','collisions':names_overlap(tree,names,d['length'],d['width'],d['height'],m)})
    report['parking_pair_clearance_y_m']=6-d['width'];report['nominal_gate_height_margin_m']=5.43-d['height'];report['nominal_gate_width_margin_m']=6-d['width']
    # Mechanism surface intersections sampled through all deployment stages.
    groups=[('garage_shell',{'shop_static','rock_static','hangar_static'}),('store_armor',{'shop_static','pump_static'}),('cap',{'rock_static','turret','garage_shell'}),('turret',{'rock_static'}),('pump_gun_1',{'pump_static'}),('pump_gun_2',{'pump_static'}),('sign_panel',{'sign_guns'})]
    state(gate_open=0,thunderhawk_exit=0,rhino_exit=0)
    for moving,fixed in groups:
        contacts=[]
        for i in range(41):
            state(battle_mode=i/40)
            obs=[o for o in S.objects if o.get('BH_group') in fixed and not o.name.startswith(('BH_HangarFloor','BH_ShopFloor','BH_PumpFoot'))]
            mov=[o for o in S.objects if o.get('BH_group')==moving]
            if not mov:continue
            ta,va,fa,na=combine(obs);tb,vb,fb,nb=combine(mov)
            pairs=sorted(set((na[a],nb[b]) for a,b in ta.overlap(tb)))
            if pairs:contacts.append({'mode':i/40,'pairs':pairs[:40],'pair_count':len(pairs)})
        report['mechanism_contacts'][moving]=contacts
    (P/'docs/qa/boulder_geometry_v1.json').write_text(json.dumps(report,indent=2))
    print('GEOMETRY_QA',json.dumps({k:len(v['collisions']) for k,v in report['route_samples'].items()}),'MECHANISM_STAGES', {k:len(v) for k,v in report['mechanism_contacts'].items()})
finally:
    for k,v in values.items():R[k]=v
    R.animation_data.action=saved_action;S.frame_set(saved_frame);R.update_tag();bpy.context.view_layer.update()
