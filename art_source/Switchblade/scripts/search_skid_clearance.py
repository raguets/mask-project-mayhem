import bpy,json,math
from pathlib import Path
from mathutils.bvhtree import BVHTree
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Switchblade'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
r=bpy.data.objects['Switchblade_Control'];s=bpy.context.scene;results=[]
def tree(name):
 o=bpy.data.objects[name];e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();t=BVHTree.FromPolygons([e.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]);e.to_mesh_clear();return t
for exponent in [.05,.10,.15,.20,.30,1.5,2.,3.]:
 for side in [-1,1]:
  sk=bpy.data.objects['SB_SkidToCannon_'+str(side)]
  drive(sk,'rotation_euler',0,str(side)+'*1.57079632679*pow(t,'+str(exponent)+')',[('t',r,'transform')])
  drive(sk,'location',2,'1.13+0.24*pow(t,'+str(exponent)+')',[('t',r,'transform')])
 hit=[]
 for frame in range(1,122,3):
  s.frame_set(frame);r.update_tag();bpy.context.view_layer.update()
  if tree('SB_MainWing_-1').overlap(tree('SB_LandingSkidCannon_-1')):hit.append(frame)
 results.append({'exponent':exponent,'hits':hit})
best=next((d for d in reversed(results) if not d['hits'] and d['exponent']<1),None)
if best:
 exponent=best['exponent']
 for side in [-1,1]:
  sk=bpy.data.objects['SB_SkidToCannon_'+str(side)]
  drive(sk,'rotation_euler',0,str(side)+'*1.57079632679*pow(t,'+str(exponent)+')',[('t',r,'transform')]);drive(sk,'location',2,'1.13+0.24*pow(t,'+str(exponent)+')',[('t',r,'transform')])
 s.frame_set(1);r.update_tag();bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Switchblade_V5_Assembly.blend'),compress=True)
(A/'skid_trajectory_search.json').write_text(json.dumps({'trials':results,'selected':best},indent=2));print('SKID_SEARCH',json.dumps(results),'BEST',best)
