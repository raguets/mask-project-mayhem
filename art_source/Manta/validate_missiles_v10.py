import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
S=bpy.context.scene;A=Path('G:/DEV/mask-project-mayhem/art_source/Manta')
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
def surface(o):
 dg=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(dg);me=ev.to_mesh();v=[ev.matrix_world@p.co for p in me.vertices];f=[list(p.vertices) for p in me.polygons];ev.to_mesh_clear();return BVHTree.FromPolygons(v,f),v
direction=Vector((1,.371,.163)).normalized()
def inside(tree,p):
 p=p.copy();count=0
 for i in range(30):
  hit=tree.ray_cast(p,direction,20)
  if hit[0] is None:return bool(count%2)
  count+=1;p=hit[0]+direction*.00001
 return False
parts=[o for o in bpy.data.objects if o.name.startswith(('MA_PersistentMissile','MA_MissileRedTip','MA_MissileGuide','MA_TripleLauncherCassette'))]
panels=[bpy.data.objects[n] for n in ['MA_SlidingHoodSkin','MA_FixedHoodRearQuarter','MA_FixedHoodShoulder_L','MA_FixedHoodShoulder_R']]
hits=[];min_above_cannon=[]
for frame in range(1,122):
 S.frame_set(frame);bpy.context.view_layer.update();ps={o.name:surface(o) for o in panels}
 for o in parts:
  tr,v=surface(o);samples=[sum(v,Vector())/len(v)]+v[::max(1,len(v)//16)]
  for n,(pt,pv) in ps.items():
   overlap=len(tr.overlap(pt));contained=sum(inside(pt,p) for p in samples)
   if overlap or contained:hits.append({'frame':frame,'part':o.name,'panel':n,'triangle_pairs':overlap,'sample_points_inside_panel':contained})
S.frame_set(121);bpy.context.view_layer.update()
hood=bpy.data.objects['MA_SlidingHoodSkin'];tr,v=surface(hood);front=max(p.x for p in v);frontz=max(p.z for p in v if p.x>front-.025)
root=bpy.data.objects['Manta_Control'];axes=[]
for s in [-1,1]:
 ob=bpy.data.objects['MA_MainWingForwardCannon_'+str(s)];axis=(ob.matrix_world.to_3x3()@Vector((0,-s,0))).normalized();axes.append({'side':s,'forward_axis':list(axis),'dot_project_forward':axis.x})
S.frame_set(1)
r={'phases':121,'parts':[o.name for o in parts],'hood_panels':[o.name for o in panels],'intersections_or_containment':hits,'hammerhead_front_max_z':frontz,'front_cannon_axis_z':.58,'nose_below_cannon_axis':frontz<.58,'wing_cannon_axes_flight':axes,'method':'Evaluated triangle overlap plus ray parity at centres and up to 17 mesh samples. Containment samples complement surfaces; not an exhaustive volume proof.'}
(A/'missile_validation_v10.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
