"""Evaluate actual surfaces and state identities; no continuous-time certificate.
Timer scheduled, output COMPLETE/ERROR and a detailed report.
"""
import bpy,json,time,traceback
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Rhino';S=bpy.context.scene;R=bpy.data.objects['Rhino_Control']
initial_frame=S.frame_current;initial_props={k:R[k] for k in ['rear_detach','bullbar','cannons','rear_open','launcher_up']};actor_state={n:(dict(bpy.data.objects[n].items()),bpy.data.objects[n].location.copy()) for n in ['AlexSector_Rig','BruceSato_Rig']}
report={'scope':'Evaluated triangle surface intersections at all 241 integer frames, curated mechanical pairs; not continuous time or contained volume certification. Intentional joints, fasteners, upholstery contact excluded.','characters':{},'frames':[]};cache={};local={};started=time.time()
def geometry(ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();v=[p.co.copy() for p in me.vertices];f=[tuple(p.vertices) for p in me.polygons];ev.to_mesh_clear();return v,f
def tree_for(name):
 ob=bpy.data.objects[name];ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());matrix=ev.matrix_world.copy();key=(name,tuple(x for row in matrix for x in row))
 if key in cache:return cache[key]
 if name not in local:local[name]=geometry(ob)
 vv,ff=local[name];vv=[matrix@v for v in vv];bounds=([min(v[i] for v in vv) for i in range(3)],[max(v[i] for v in vv) for i in range(3)])
 item=(BVHTree.FromPolygons(vv,ff),bounds);cache[key]=item;return item
def overlap(a,b):
 ta,aa=tree_for(a);tb,bb=tree_for(b)
 if any(aa[1][i]<bb[0][i]-.00001 or bb[1][i]<aa[0][i]-.00001 for i in range(3)):return 0
 return len(ta.overlap(tb))
def nearest_gap(name,target):
 ob=bpy.data.objects[name];v,f=geometry(ob);v=[ob.matrix_world@p for p in v];tree=tree_for(target)[0];dist=[tree.find_nearest(p)[3] for p in v];return min(d for d in dist if d is not None)
fixed=[ob.name for ob in bpy.data.objects if ob.name.startswith(('RH_TruckFrame_','RH_FrameCrossmember_','RH_TruckAxleOutrigger_','RH_TruckMiddleStub_','RH_FrontFender_','RH_AirCleaner_','RH_CabLowerFront','RH_CabRoof','RH_DoorLower_','RH_DoorAFrame_','RH_DoorBFrame_','RH_DoorGlass_','RH_Windshield_','RH_CabVisor','RH_MirrorHousing_','RH_UpperCockpitSide_','RH_UpperCockpitRoof','RH_UpperCockpitGlass_','RH_FixedBumper','RH_Hood')) and ob.type in ['MESH','CURVE']]
fixed+=['RH_Front_-1_Tire','RH_Front_1_Tire','RH_MiddleOuter_Truck_-1_Tire','RH_MiddleOuter_Truck_1_Tire']
fixed += [ob.name for ob in bpy.data.objects if ob.name.startswith('RH_RearCabinetWing_')]
pod=[ob.name for ob in bpy.data.objects if ob.name.endswith('_Tire') and 'Pod' in ob.name]+['RH_PodDeck','RH_PodFrame_-0.36','RH_PodFrame_0.36','RH_PodSeatBack','RH_PodSeatBase','RH_PodControlPanel']
hatch=['RH_RearCockpitHatch']
guns=['RH_ExhaustCannonTube_-1','RH_ExhaustCannonTube_1','RH_ExhaustHeatShield_-1','RH_ExhaustHeatShield_1']
launcher=[ob.name for ob in bpy.data.objects if ob.name.startswith(('RH_LaunchTube_','RH_MissileNose_','RH_LauncherCradle'))]
bull=['RH_BullbarUpright_-1','RH_BullbarUpright_1','RH_BullbarLower','RH_BullbarCross']
pairs=list(dict.fromkeys([(a,b) for group in [pod,hatch,guns,launcher,bull] for a in group for b in fixed]+[(a,b) for a in hatch for b in pod]+[(a,b) for a in launcher for b in hatch]))
def restore():
 for k,v in initial_props.items():R[k]=v
 for n,(props,loc) in actor_state.items():
  ob=bpy.data.objects[n];ob.location=loc
  for key in ['mask_on','driving_pose']:ob[key]=props[key]
  ob.update_tag()
 R.update_tag();S.frame_set(initial_frame);bpy.context.view_layer.update()
def start_characters():
 for code,n in [('AS','AlexSector_Rig'),('BS','BruceSato_Rig')]:
  r=bpy.data.objects[n];head=bpy.data.objects[code+'_Head_AnatomicalSurface'];body=bpy.data.objects[code+'_ContinuousFlightSuit'];identity=(head.data.as_pointer(),body.data.as_pointer(),r.data.as_pointer());states=[]
  for pose in [0,1]:
   for masked in [False,True]:
    r['driving_pose']=pose;r['mask_on']=masked;r.location=(2,-.6 if code=='AS' else .6,1.37) if pose else (0,0,0);r.update_tag();S.frame_set(1);bpy.context.view_layer.update()
    maskparts=sum(not o.hide_render for o in bpy.data.collections[code+'_Mask'].all_objects);assert (maskparts>0)==masked;assert not head.hide_render;assert identity==(head.data.as_pointer(),body.data.as_pointer(),r.data.as_pointer())
    states.append({'pose':pose,'mask':masked,'visible_mask_parts':maskparts,'same_body_head_rig':True,'face_retained':True})
  report['characters'][n]={'four_states':states,'one_character':True}
  r['driving_pose']=1;r['mask_on']=True;r.location=(2,-.6 if code=='AS' else .6,1.37);r.update_tag()
 S.frame_set(1);bpy.context.view_layer.update()
 # Static occupied-cab envelopes in the most bulky masked seated state.
 cabin_colliders=[n for n in fixed if any(k in n for k in ['CabRoof','Door','Windshield'])]+['RH_SeatHeadrest_-0.6','RH_SeatHeadrest_0.6']
 for code,n in [('AS','AlexSector_Rig'),('BS','BruceSato_Rig')]:
  parts=[code+'_Head_AnatomicalSurface',code+'_ContinuousFlightSuit']+[o.name for o in bpy.data.collections[code+'_Mask'].all_objects if o.type=='MESH']
  collisions=[]
  for a in parts:
   for b in cabin_colliders:
    count=overlap(a,b)
    if count:collisions.append({'a':a,'b':b,'triangles':count})
  contacts={}
  for sd in ['L','R']:
   contacts[sd]={'pedal_gap_m':nearest_gap(code+'_BootUpper_'+sd,'RH_Pedal_'+n+'_'+sd)}
   if code=='BS':contacts[sd]['wheel_gap_m']=nearest_gap(code+'_GloveSkin_'+sd,'RH_SteeringRim')
  yy=-.6 if code=='AS' else .6
  contacts['seat']={kind:{'surface_gap_m':nearest_gap(code+'_ContinuousFlightSuit','RH_Seat'+kind+'_'+str(yy)),'surface_pairs':overlap(code+'_ContinuousFlightSuit','RH_Seat'+kind+'_'+str(yy))} for kind in ['Cushion','Back']}
  report['characters'][n].update({'masked_cabin_intersections':collisions,'contacts':contacts})
 # Assert separate humans, not two states of the same object data.
 assert bpy.data.objects['AS_Head_AnatomicalSurface'].data!=bpy.data.objects['BS_Head_AnatomicalSurface'].data
 report['distinct_character_data']=True
 local.clear();cache.clear()
 for k in initial_props:R[k]=0.
 R.update_tag();S.frame_set(1);bpy.context.view_layer.update()
 for name in set(a for a,b in pairs)|set(b for a,b in pairs):local[name]=geometry(bpy.data.objects[name])
def step():
 try:
  if not report['characters']:start_characters()
  frame=len(report['frames'])+1
  if frame>241:
   report['collision_frames']=[f['frame'] for f in report['frames'] if f['collisions']];report['launcher_order_ok']=all(f['launcher_progress']<=.00001 or f['rear_open_progress']>.92 for f in report['frames']);report['tires']=json.loads((A/'wheel_partition_v1.json').read_text());report['persistent_tire_count']=sum(o.name.endswith('_Tire') for o in S.objects);assert report['persistent_tire_count']==10
   report['elapsed_seconds']=round(time.time()-started,2);restore();(A/'validation_v1.json').write_text(json.dumps(report,indent=2));(A/'validation_v1_COMPLETE').write_text('All integer frames evaluated; read report for failures and scope.');return None
  S.frame_set(frame);R.update_tag();bpy.context.view_layer.update();collisions=[]
  for a,b in pairs:
   count=overlap(a,b)
   if count:collisions.append({'a':a,'b':b,'triangles':count})
  progress=(bpy.data.objects['RH_MissileLauncherLift'].location.z-2.72)/.55
  report['frames'].append({'frame':frame,'battle':R['battle_mode'],'collisions':collisions,'rear_open_progress':-bpy.data.objects['RH_RearCockpitHatchPivot'].rotation_euler.y/2.126,'launcher_progress':progress,'pod_location':list(bpy.data.objects['Rhino_RearVehicle_Root'].location)})
  if frame%12==0:(A/'validation_v1_progress.json').write_text(json.dumps({'frame':frame,'collisions_so_far':sum(bool(f['collisions']) for f in report['frames'])}))
  if len(cache)>1800:cache.clear()
  return .01
 except Exception:
  error=traceback.format_exc();restore();(A/'validation_v1_ERROR.json').write_text(json.dumps({'error':error,'frames_completed':len(report['frames'])}));return None
for name in ['validation_v1_COMPLETE','validation_v1_ERROR.json']:(A/name).unlink(missing_ok=True)
bpy.app.timers.register(step,first_interval=.5);print('RHINO_GEOMETRY_AUDIT_STARTED',len(pairs),'surface pairs')
