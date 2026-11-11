import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
A=Path('G:/DEV/mask-project-mayhem/art_source/Raven');S=bpy.context.scene;root=bpy.data.objects['Raven_Control'];R=bpy.data.objects['CalhounBurns_Rig']
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
saved=(S.frame_current,root['hover_height'],R['driving_pose'],R['in_vehicle'],R['mask_on'])
root['hover_height']=0.;R['in_vehicle']=1.;R['driving_pose']=1.;R['mask_on']=True;R.update_tag();S.frame_set(1);bpy.context.view_layer.update()
def worldverts(name):
    ob=bpy.data.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get());me=ob.to_mesh();pts=[ob.matrix_world@v.co for v in me.vertices];faces=[tuple(f.vertices) for f in me.polygons];ob.to_mesh_clear();return pts,faces
def bounds(name):
    pts,_=worldverts(name);return {'min':[min(v[i] for v in pts) for i in range(3)],'max':[max(v[i] for v in pts) for i in range(3)]}
def outer_surface(name):
    ob=bpy.data.objects[name];return [ob.matrix_world@v.co for v in ob.data.vertices]
def tree(name):
    pts,faces=worldverts(name);return BVHTree.FromPolygons(pts,faces)
def descendant(ob,parent):
    while ob:
        if ob==parent:return True
        ob=ob.parent
    return False
checks={};data={};clip=bpy.data.objects['RV_CompleteFront_LongitudinalPivot'];cassette=bpy.data.objects['RV_ReactorBlock_VerticalSlide']
checks['whole_front_retained']=all(descendant(bpy.data.objects[name],clip) for name in ['RV_Hood_OuterSkin','RV_FrontFender_L','RV_NoseFascia','RV_FrontWheelFold_L','RV_FrontWheelFold_R'])
checks['fixed_floor_stops_before_front']=bounds('RV_CabinFloor')['max'][0]<=.42501
checks['fixed_tunnel_stops_before_front']=bounds('RV_TransmissionTunnel')['max'][0]<=.40501
checks['projecting_dashboard_removed']=bounds('RV_Dashboard')['max'][0]<.44
hoodpts,_=worldverts('RV_Hood_OuterSkin');shoulderpts,_=worldverts('RV_FrontUpperShoulder_L')
hoodedge=[v for v in hoodpts if abs(v.y-.6785)<1e-5];shoulderedge=[v for v in shoulderpts if abs(v.y-.6815)<1e-5]
edge_deltas=[abs(v.z-min(shoulderedge,key=lambda w:abs(w.x-v.x)).z) for v in hoodedge]
data['hood_edge_max_level_difference_m']=max(edge_deltas);checks['hood_level_with_shoulders']=max(edge_deltas)<.003
data['front_fixed_limits']={name:bounds(name) for name in ['RV_CabinFloor','RV_TransmissionTunnel','RV_Dashboard']}
for join,left,right in [('front_roof','RV_RoofTarga','RV_Windshield'),('rear_roof','RV_RearHatchGlass','RV_RoofTarga')]:
    lp=outer_surface(left);rp=outer_surface(right);x=max(p.x for p in lp);a=sorted([p for p in lp if abs(p.x-x)<1e-5],key=lambda p:p.y);b=sorted([p for p in rp if abs(p.x-x)<1e-5],key=lambda p:p.y)
    delta=max((p-q).length for p,q in zip(a,b));data[join+'_max_edge_gap_m']=delta;checks[join+'_continuous_positions']=len(a)==len(b) and delta<1e-5
checks['rounded_black_shell_is_single_mesh']=bpy.data.objects['RV_ReactorCassette_RoundedTopAndSides'].type=='MESH'
checks['reactors_share_moving_cassette']=all(descendant(o,cassette) for o in bpy.data.objects if o.name.startswith('RV_ReactorCassette_'))
widths={}
for axle in ['Front','Rear']:
    for side in ['L','R']:
        ob=bpy.data.objects['RV_'+axle+'HubCannon_'+side];widths[axle+side]=max(v.co.z for v in ob.data.vertices)-min(v.co.z for v in ob.data.vertices)
data['gun_width_m']=widths;checks['four_guns_width_doubled']=all(abs(w-.09)<1e-5 for w in widths.values())
initial_nozzles=bounds('RV_ReactorCassette_FourNozzleBank');initial_shell=bounds('RV_ReactorCassette_RoundedTopAndSides');baselinehood=[(hoodpts[i]-hoodpts[0]).length for i in range(0,len(hoodpts),max(1,len(hoodpts)//95))]
checks['nozzles_hidden_below_fascia_at_rest']=initial_nozzles['max'][2]<.66
contacts=[];rigid_error=0
pair_names=[]
for side in ['L','R']:
    pair_names += [('RV_FrontTire_'+side,'RV_FrontUndertray'),('RV_FrontTire_'+side,'RV_FrontFender_'+side),('RV_Hood_OuterSkin','RV_FrontTire_'+side),('RV_RearTire_'+side,'RV_RearUndertray')]
for frame in [1]+list(range(31,122,3))+[151]:
    S.frame_set(frame);R.update_tag();bpy.context.view_layer.update();cache={name:tree(name) for pair in pair_names for name in pair};hits=[]
    for a,b in pair_names:
        count=len(cache[a].overlap(cache[b]))
        if count:hits.append({'a':a,'b':b,'triangle_pairs':count})
    if hits:contacts.append({'frame':frame,'pairs':hits})
    points,_=worldverts('RV_Hood_OuterSkin');distances=[(points[i]-points[0]).length for i in range(0,len(points),max(1,len(points)//95))];rigid_error=max(rigid_error,max(abs(a-b) for a,b in zip(baselinehood,distances)))
S.frame_set(151);bpy.context.view_layer.update();deployed_nozzles=bounds('RV_ReactorCassette_FourNozzleBank');deployed_shell=bounds('RV_ReactorCassette_RoundedTopAndSides')
data['rear']={'rest_nozzles':initial_nozzles,'deployed_nozzles':deployed_nozzles,'rest_shell':initial_shell,'deployed_shell':deployed_shell,'lift_m':cassette.location.z,'clearance_above_fascia_m':deployed_nozzles['min'][2]-.66}
checks['compact_reactor_lift']=.20<cassette.location.z<.215
checks['complete_nozzle_row_just_above_fascia']=0<deployed_nozzles['min'][2]-.66<.02
checks['cassette_never_tilts']=max(abs(v) for v in cassette.rotation_euler)<1e-6
checks['hood_rigid_through_motion']=rigid_error<1e-5;data['hood_rigid_max_distance_error_m']=rigid_error
checks['sampled_tire_body_pairs_clear']=not contacts;data['sampled_motion_contacts']=contacts
data['footwell_driving_bounds']={name:bounds(name) for name in ['CB_BootUpper_L','CB_BootUpper_R']}
S.frame_set(saved[0]);root['hover_height']=saved[1];R['driving_pose'],R['in_vehicle'],R['mask_on']=saved[2:];R.update_tag();bpy.context.view_layer.update()
report={'passed':all(checks.values()),'checks':checks,'data':data,'method':'Actual evaluated meshes,33 motion states on named tire/body pairs, canopy edge continuity and rigid distances. Separate rendered inspection required; not exhaustive swept-volume certification.'}
(A/'validation_v12.json').write_text(json.dumps(report,indent=2));print(json.dumps({'passed':report['passed'],'failed':[k for k,v in checks.items() if not v],'rear':data['rear'],'motion_contacts':contacts}))
