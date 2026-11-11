"""V14 four-state fit review and 193-frame evaluated-surface collision audit."""
import bpy,json,time,traceback
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path('G:/DEV/mask-project-mayhem');T=P/'art_source/Thunderhawk';Q=P/'docs/qa';s=bpy.context.scene;r=bpy.data.objects['MattTrakker_Rig'];started=time.time()
for name in ['validation_v14_COMPLETE','validation_v14_ERROR.json']:(Q/name).unlink(missing_ok=True)
saved=(s.frame_current,r['driving_pose'],r['mask_on'],r.location.copy())
def restore():
    frame,drive,mask,loc=saved;r['driving_pose']=drive;r['mask_on']=mask;r.location=loc;r.update_tag();s.frame_set(frame);bpy.context.view_layer.update()
def geom(obs):
    dg=bpy.context.evaluated_depsgraph_get();vv=[];ff=[]
    for ob in obs:
        if ob.type not in ['MESH','CURVE']:continue
        ev=ob.evaluated_get(dg);me=ev.to_mesh()
        if me:
            off=len(vv);vv.extend(ev.matrix_world@v.co for v in me.vertices);ff.extend(tuple(off+i for i in f.vertices) for f in me.polygons);ev.to_mesh_clear()
    assert ff,'Empty collision/contact set'
    return BVHTree.FromPolygons(vv,ff),vv
def bounds(points):return {'min':[min(p[i] for p in points) for i in range(3)],'max':[max(p[i] for p in points) for i in range(3)]}
def min_gap(points,tree):return min(tree.find_nearest(p)[3] for p in points)
char=bpy.data.collections['MT11_Character'];mask=bpy.data.collections['Spectrum11_Asset'];head=bpy.data.objects['MT_Head_AnatomicalSurface'];suit=bpy.data.objects['MT_ContinuousFlightSuit'];collar=bpy.data.objects['Spectrum_NeckSealConnectingBody']
assert sum(ob.type=='ARMATURE' for ob in char.all_objects)==1
assert sum(ob.name=='MT_Head_AnatomicalSurface' for ob in s.objects)==1
pointers={ob.name:ob.data.as_pointer() for ob in char.all_objects if ob.type=='MESH'}
report={'scope':'Every integer vehicle frame, evaluated surface triangles. Not continuous-time or contained-volume certification.','four_states':[],'collar_fit':[],'frames':[],'one_character_one_armature_one_head':True,'interpretation':'Supplied replica photos/illustrations; neck dimensions and flexible collar construction estimated and authorized.'}
for drive in [0,1]:
    for masked in [False,True]:
        r['driving_pose']=drive;r['mask_on']=masked;r.location=(0,.4 if drive else 0,0);r.update_tag();s.frame_set(1+drive);bpy.context.view_layer.update()
        visible=sum(not ob.hide_render for ob in mask.objects)
        assert (visible>0)==masked and not head.hide_render
        assert all(ob.data.as_pointer()==pointers[ob.name] for ob in char.all_objects if ob.type=='MESH')
        _,hv=geom([head]);report['four_states'].append({'drive':drive,'mask':masked,'visible_mask_parts':visible,'same_meshes':True,'face_retained':True,'head_bounds':bounds(hv)})
    suit_tree,_=geom([suit]);dg=bpy.context.evaluated_depsgraph_get();ev=collar.evaluated_get(dg);me=ev.to_mesh();start=len(collar.data.vertices)-128;base=[ev.matrix_world@me.vertices[i].co for i in range(start,start+128)];ev.to_mesh_clear()
    ds=[];signed=[]
    for p in base:
        near,normal,idx,d=suit_tree.find_nearest(p);ds.append(d);signed.append((p-near).dot(normal))
    report['collar_fit'].append({'drive':drive,'base_samples':128,'gap_min_m':min(ds),'gap_mean_m':sum(ds)/len(ds),'gap_max_m':max(ds),'samples_more_than_2mm_inside_suit':sum(v<-.002 for v in signed)})
r['driving_pose']=1;r['mask_on']=True;r.location=(0,.4,0);r.update_tag();s.frame_set(1);bpy.context.view_layer.update()
helmet,helmet_pts=geom([ob for ob in mask.objects if ob.type=='MESH'])
body,_=geom([suit,head]+[ob for ob in char.objects if ob.name.startswith(('MT_Boot','MT_Glove'))])
colliders=[ob for ob in s.objects if ob.type in ['MESH','CURVE'] and ob.name.startswith(('THK_Door','THK_Cannon','THK_InnerDoor','THK_RoofSpine','THK_FrontRoofHeader','THK_RearRoofHeader','THK_Windshield','THK_RearGlass','THK_QuarterGlass'))]
plate,_=geom([ob for ob in s.objects if ob.name.startswith('THK_RearPlate_')]);shelf,_=geom([bpy.data.objects['THK_ParcelShelf'],bpy.data.objects['THK_ParcelShelf_FrontLip']])
headrest,_=geom([ob for ob in s.objects if ob.name.startswith('THK_Headrest_L')]);report['helmet_headrest_surface_pairs']=len(helmet.overlap(headrest))
report['contacts']={}
for sd,idx in [('R',0),('L',2)]:
    boot,pts=geom([bpy.data.objects['MT_BootUpper_'+sd]]);pedal,_=geom([bpy.data.objects['THK_Pedal'+str(idx)]])
    rim,_=geom([bpy.data.objects['THK_SteeringRim']]);glove,hpts=geom([bpy.data.objects['MT_GloveSkin_'+sd]])
    report['contacts'][sd]={'shoe_pedal_gap_m':min_gap(pts,pedal),'glove_rim_gap_m':min_gap(hpts,rim),'glove_rim_surface_pairs':len(glove.overlap(rim))}
report['collider_names']=[ob.name for ob in colliders]
frames=iter(range(1,194))
def step():
    try:
        for _ in range(5):
            try:frame=next(frames)
            except StopIteration:
                report['vehicle_collision_frames']=[v for v in report['frames'] if v['helmet_pairs'] or v['body_pairs'] or v['shelf_moving_pairs'] or v['plate_cover_pairs'] or v['plate_reactor_pairs']]
                report['reactor_order_ok']=all(v['reactors_after_cover'] and v['cover_vertical'] for v in report['frames']);report['elapsed_seconds']=round(time.time()-started,2)
                (T/'validation_v14.json').write_text(json.dumps(report,indent=2));restore();(Q/'validation_v14_COMPLETE').write_text('Complete, scene restored');return None
            s.frame_set(frame);bpy.context.view_layer.update();ct,_=geom(colliders);panel,_=geom([bpy.data.objects['THK_RearPanel']]);reactors,_=geom([ob for ob in s.objects if ob.type=='MESH' and ob.name.startswith('THK_Reactor')])
            cover=bpy.data.objects['THK_RearPanel_Lift'];ordered=all(bpy.data.objects['THK_Reactor_Deploy_'+sd].location.x>=-.00001 or abs(cover.location.z-.215)<1e-5 for sd in ['L','R'])
            report['frames'].append({'frame':frame,'helmet_pairs':len(helmet.overlap(ct)),'body_pairs':len(body.overlap(ct)),'shelf_moving_pairs':len(shelf.overlap(ct)),'plate_cover_pairs':len(plate.overlap(panel)),'plate_reactor_pairs':len(plate.overlap(reactors)),'reactors_after_cover':ordered,'cover_vertical':abs(cover.location.x)<1e-6 and abs(cover.location.y)<1e-6 and Vector(cover.rotation_euler).length<1e-6})
        (Q/'validation_v14_progress.json').write_text(json.dumps({'done':len(report['frames']),'last':report['frames'][-1]}));return .1
    except Exception:
        error=traceback.format_exc();restore();(Q/'validation_v14_ERROR.json').write_text(json.dumps({'error':error,'done':len(report['frames'])},indent=2));return None
bpy.app.timers.register(step,first_interval=.25)
print('V14_GEOMETRIC_AUDIT_STARTED',json.dumps(report['collar_fit']))
