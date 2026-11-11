"""Focused V3 check: evaluated bullbar envelope, topology and all 241 slide frames.
Other mechanism/character checks remain the unchanged V2 baseline, explicitly cited.
"""
import bpy,bmesh,json,time,traceback
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Rhino';S=bpy.context.scene;R=bpy.data.objects['Rhino_Control'];saved_frame=S.frame_current;saved_bull=R['bullbar'];started=time.time();local={};cache={}
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
parts=['RH_BullbarFrame']+[f'RH_BullbarVertical_{i:02}' for i in range(1,8)];moving=parts+['RH_BullbarGuide_-1','RH_BullbarGuide_1']
excluded=set(moving+['RH_BullbarFixedSleeve_-1','RH_BullbarFixedSleeve_1','RH_BullbarFixedMount_-1','RH_BullbarFixedMount_1'])
obstacles=[o for o in bpy.data.collections['Rhino_Truck'].all_objects if o.type in ['MESH','CURVE','FONT'] and o.name not in excluded]
report={'source':bpy.data.filepath,'scope':'Modified bullbar/slide evaluated against truck surfaces at 241 integer frames. Intentional joints within bullbar and telescopic mounts excluded. Other mechanisms/character tests retained from unchanged V2 baseline; no continuous-time/contained-volume certification.','baseline':'validation_v2.json','reference':'Images de reference/rhino/rhino pare buffle.jpg','frames':[]}
def geometry(ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();v=[p.co.copy() for p in me.vertices];f=[tuple(p.vertices) for p in me.polygons];ev.to_mesh_clear();return v,f
def bbox(ob,dg):
 ev=ob.evaluated_get(dg);v=[ev.matrix_world@Vector(p) for p in ev.bound_box];return ([min(p[i] for p in v) for i in range(3)],[max(p[i] for p in v) for i in range(3)])
def tree_for(ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());matrix=ev.matrix_world.copy();key=(ob.name,tuple(x for row in matrix for x in row))
 if key not in cache:
  if ob.name not in local:local[ob.name]=geometry(ob)
  v,f=local[ob.name];cache[key]=BVHTree.FromPolygons([matrix@p for p in v],f)
 return cache[key]
def overlaps(a,b):return all(a[0][i]<=b[1][i]+1e-6 and b[0][i]<=a[1][i]+1e-6 for i in range(3))
bm=bmesh.new();bm.from_mesh(bpy.data.objects['RH_BullbarFrame'].data);report['closed_frame_topology']={'boundary_edges':sum(e.is_boundary for e in bm.edges),'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'vertices':len(bm.verts),'faces':len(bm.faces)};bm.free();assert report['closed_frame_topology']['non_manifold_edges']==0
def restore():R['bullbar']=saved_bull;R.update_tag();S.frame_set(saved_frame);bpy.context.view_layer.update()
def step():
 try:
  for iteration in range(6):
   frame=len(report['frames'])+1
   if frame>241:
    report['collision_frames']=[f['frame'] for f in report['frames'] if f['collisions']];report['vertical_bar_count']=7;report['elapsed_seconds']=round(time.time()-started,2)
    assert not report['collision_frames'],report['collision_frames'];restore();(A/'bullbar_validation_v3.json').write_text(json.dumps(report,indent=2));(A/'bullbar_validation_v3_COMPLETE').write_text('Bullbar envelope, topology and 241 integer frames checked. Read scope in JSON.');return None
   R['bullbar']=0.;R.update_tag();S.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();boxes={ob.name:bbox(ob,dg) for ob in obstacles};collisions=[];forward_gaps=[]
   for name in moving:
    ob=bpy.data.objects[name];a=bbox(ob,dg)
    for other in obstacles:
     b=boxes[other.name]
     if all(a[0][i]<=b[1][i] and b[0][i]<=a[1][i] for i in [1,2]):forward_gaps.append(a[0][0]-b[1][0])
     if overlaps(a,b):
      count=len(tree_for(ob).overlap(tree_for(other)))
      if count:collisions.append({'a':name,'b':other.name,'surface_pairs':count})
   border=bbox(bpy.data.objects['RH_BullbarFrame'],dg);grille=[bbox(ob,dg) for ob in S.objects if ob.name.startswith(('RH_GrilleSide_','RH_GrilleCross_'))];limits=([min(b[0][i] for b in grille) for i in range(3)],[max(b[1][i] for b in grille) for i in range(3)])
   delta=max(abs(border[k][i]-limits[k][i]) for k in [0,1] for i in [1,2]);assert delta<.0001,(frame,delta)
   report['frames'].append({'frame':frame,'bullbar_x':bpy.data.objects['RH_BullbarSlide'].location.x,'outline_difference_from_grille_m':delta,'forward_gap_min_m':min(forward_gaps) if forward_gaps else None,'collisions':collisions})
   if frame==1:
    report['outline_bounds_m']={'bullbar':border,'grille':limits};frame_tree=tree_for(bpy.data.objects['RH_BullbarFrame']);assert frame_tree.ray_cast(Vector((6,.10,1.78)),Vector((-1,0,0)),2)[0] is None;assert tree_for(bpy.data.objects['RH_BullbarVertical_04']).ray_cast(Vector((6,0,1.78)),Vector((-1,0,0)),2)[0] is not None;report['open_center_and_vertical_bar_ray_checks']=True
  (A/'bullbar_validation_v3_progress.json').write_text(json.dumps({'frame':len(report['frames']),'collision_frames_so_far':sum(bool(f['collisions']) for f in report['frames'])}));return .01
 except Exception:
  restore();(A/'bullbar_validation_v3_ERROR.json').write_text(json.dumps({'error':traceback.format_exc(),'frames_completed':len(report['frames'])}));return None
for name in ['bullbar_validation_v3_COMPLETE','bullbar_validation_v3_ERROR.json']:(A/name).unlink(missing_ok=True)
bpy.app.timers.register(step,first_interval=.4);print('RHINO_BULLBAR_V3_VALIDATION_STARTED',len(obstacles),'truck obstacles')
