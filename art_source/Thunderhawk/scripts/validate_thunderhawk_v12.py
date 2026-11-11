"""Incremental live-MCP geometric audit, every integer transform frame."""
import bpy,json,traceback,time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path('G:/DEV/mask-project-mayhem');T=P/'art_source/Thunderhawk';Q=P/'docs/qa'
(Q/'validation_v12_COMPLETE').unlink(missing_ok=True);(Q/'validation_v12_ERROR.txt').unlink(missing_ok=True)
(Q/'validation_v12_progress.json').unlink(missing_ok=True)
s=bpy.context.scene;r=bpy.data.objects['MattTrakker_Rig'];started=time.time()
saved=(s.frame_current,r['driving_pose'],r['mask_on'],r.location.copy())
report={'frame_sampling':'All integer frames 1..193; no continuous-time or watertight-volume collision certification.',
        'reference_limits':'Toy/replica photographs and illustrated portrait. Footwear dimensions, anatomy and cockpit interpreted.',
        'four_states':[],'frames':[]}
def restore():
    fr,drive,mask,loc=saved;r['driving_pose']=drive;r['mask_on']=mask;r.location=loc;r.update_tag();s.frame_set(fr);bpy.context.view_layer.update()
def evaluated_geometry(obs):
    dg=bpy.context.evaluated_depsgraph_get();vv=[];ff=[]
    for ob in obs:
        if ob.type not in ('MESH','CURVE'):continue
        ev=ob.evaluated_get(dg);me=ev.to_mesh()
        if not me:continue
        off=len(vv);vv.extend(ev.matrix_world@v.co for v in me.vertices)
        ff.extend(tuple(off+i for i in p.vertices) for p in me.polygons);ev.to_mesh_clear()
    return vv,ff
def tree(obs):
    vv,ff=evaluated_geometry(obs);return BVHTree.FromPolygons(vv,ff,all_triangles=False),vv
def gap(points,bvh):
    ds=[bvh.find_nearest(v)[3] for v in points];return min(ds) if ds else None
char=bpy.data.collections['MT11_Character'];mask=bpy.data.collections['Spectrum11_Asset']
assert sum(o.type=='ARMATURE' for o in char.all_objects)==1
assert sum(o.name=='MT_Head_AnatomicalSurface' for o in s.objects)==1
assert bpy.data.objects['THK_DoorCannon_L']!=bpy.data.objects['THK_DoorCannon_R']
report['one_armature_one_head']=True
report['separate_door_cannons']=['THK_DoorCannon_L','THK_DoorCannon_R']
report['spoiler_independent_of_rear_cover']=bpy.data.objects['THK_Spoiler_Lift'].parent!=bpy.data.objects['THK_RearPanel_Lift']
identities={o.name:o.data.as_pointer() for o in char.all_objects if o.type=='MESH'}
for pose in [0,1]:
    for masked in [False,True]:
        r['driving_pose']=pose;r['mask_on']=masked;r.update_tag();s.frame_set(1+pose);bpy.context.view_layer.update()
        visible=sum(not o.hide_render for o in mask.objects)
        same=all(o.data.as_pointer()==identities[o.name] for o in char.all_objects if o.type=='MESH')
        assert same and (visible>0)==masked
        report['four_states'].append({'driving_pose':pose,'mask_on':masked,'visible_mask_parts':visible,'same_meshes':same})
r['driving_pose']=1;r['mask_on']=True;r.location=(0,.4,0);r.update_tag();s.frame_set(1);bpy.context.view_layer.update()
helmet,helmet_pts=tree([o for o in mask.objects if o.type=='MESH'])
body,body_pts=tree([bpy.data.objects['MT_ContinuousFlightSuit'],bpy.data.objects['MT_Head_AnatomicalSurface']]+[o for o in char.objects if o.name.startswith(('MT_Boot','MT_Glove'))])
roofnames=('THK_RoofSpine','THK_FrontRoofHeader','THK_RearRoofHeader','THK_Windshield','THK_RearGlass','THK_QuarterGlass')
moving=[o for o in s.objects if o.type in ('MESH','CURVE') and o.name.startswith(('THK_Door','THK_Cannon','THK_InnerDoor'))]
fixed=[o for o in s.objects if o.type=='MESH' and o.name.startswith(roofnames)]
colliders=moving+fixed
report['colliders']=[o.name for o in colliders]
# Contact distances use actual evaluated vertices and triangles, not origins/AABBs.
contact={}
for sd,idx in [('R',0),('L',2)]:
    boot,pts=tree([bpy.data.objects['MT_BootUpper_'+sd]])
    sole,sole_pts=tree([bpy.data.objects['MT_BootSole_'+sd]])
    pedal,pedal_pts=tree([bpy.data.objects['THK_Pedal'+str(idx)]])
    floor,floor_pts=tree([bpy.data.objects['THK_RecessedFootwell_L']])
    contact[sd]={'upper_to_pedal_gap_m':gap(pts,pedal),'upper_pedal_surface_pairs':len(boot.overlap(pedal)),
                 'sole_to_footwell_gap_m':gap(sole_pts,floor),'sole_floor_surface_pairs':len(sole.overlap(floor))}
rim,rim_pts=tree([bpy.data.objects['THK_SteeringRim']])
for sd in ['L','R']:
    hand,pts=tree([o for o in char.objects if o.name.startswith(('MT_GlovePalm_'+sd,'MT_GloveFinger_'+sd,'MT_GloveThumb_'+sd))])
    contact['hand_'+sd]={'to_rim_gap_m':gap(pts,rim),'surface_pairs':len(hand.overlap(rim))}
seat,seat_pts=tree([o for o in bpy.data.collections['THK11_Interior'].objects if o.name.startswith(('THK_SeatCushion','THK_SeatBack')) and o.name.endswith('_L')])
suit,suit_pts=tree([bpy.data.objects['MT_ContinuousFlightSuit']])
contact['seat']={'suit_to_cushion_back_gap_m':gap(suit_pts[::8],seat),'surface_pairs':len(suit.overlap(seat)),
                 'note':'Surface contact/penetration requires visual assessment; upholstered compression is not simulated.'}
report['contacts']=contact
report['contact_tolerances_m']={'pedal':.001,'floor':.002}
report['foot_contact_within_tolerance']=all(contact[sd]['upper_to_pedal_gap_m']<=.001 and contact[sd]['sole_to_footwell_gap_m']<=.002 for sd in ['L','R'])
frames=iter(range(1,194))
def step():
    try:
        for _ in range(6):
            try:fr=next(frames)
            except StopIteration:
                report['elapsed_seconds']=round(time.time()-started,2)
                report['collision_frames']=[x for x in report['frames'] if x['helmet_pairs'] or x['body_pairs']]
                report['reactor_order_ok']=all(x['reactor_order_ok'] for x in report['frames'])
                (T/'validation_v12.json').write_text(json.dumps(report,indent=2));restore();(Q/'validation_v12_COMPLETE').write_text('done');return None
            s.frame_set(fr);bpy.context.view_layer.update();collider,_=tree(colliders)
            hp=len(helmet.overlap(collider));bp=len(body.overlap(collider))
            cover=bpy.data.objects['THK_RearPanel_Lift']
            ok=all(bpy.data.objects['THK_Reactor_Deploy_'+sd].location.x>=-.00001 or abs(cover.location.z-.215)<1e-5 for sd in ['L','R'])
            vertical=abs(cover.location.x)<1e-6 and abs(cover.location.y)<1e-6 and Vector(cover.rotation_euler).length<1e-6
            report['frames'].append({'frame':fr,'helmet_pairs':hp,'body_pairs':bp,'reactor_order_ok':ok,'cover_translation_vertical':vertical})
        (Q/'validation_v12_progress.json').write_text(json.dumps({'frames':len(report['frames']),'last':report['frames'][-1]}));return .1
    except Exception:
        (Q/'validation_v12_ERROR.txt').write_text(traceback.format_exc());restore();return None
bpy.app.timers.register(step,first_interval=.25)
print('V12_GEOMETRIC_AUDIT_STARTED',json.dumps(contact))
