import bpy,json,math
from pathlib import Path
from mathutils import Quaternion,Matrix
from mathutils.bvhtree import BVHTree
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Switchblade'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
r=bpy.data.objects['Switchblade_Control'];s=bpy.context.scene;results=[]
def tree(name):
 o=bpy.data.objects[name];e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();t=BVHTree.FromPolygons([e.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]);e.to_mesh_clear();return t
def set_trial(roll_rate,exponent,lateral):
 for side in [-1,1]:
  ya=bpy.data.objects['SB_WingSweep_'+str(side)];ro=bpy.data.objects['SB_WingFold_'+str(side)];sk=bpy.data.objects['SB_SkidToCannon_'+str(side)]
  drive(ro,'rotation_euler',1,'-1.57079632679*(1-min(1,'+str(roll_rate)+'*t))',[('t',r,'transform')])
  drive(ya,'location',1,str(side)+'*(0.70+'+str(lateral)+'*pow(sin(3.14159265359*t),0.5))',[('t',r,'transform')])
  drive(sk,'rotation_euler',0,str(side)+'*1.57079632679*pow(t,'+str(exponent)+')',[('t',r,'transform')]);drive(sk,'location',2,'1.13+0.24*pow(t,'+str(exponent)+')',[('t',r,'transform')])
for rate,exponent,lat in [(2.,.5,.7),(3.,.3,.7),(3.,.3,1.),(3.,.5,1.),(3.,.3,1.3),(2.,.3,1.3),(3.,1.,1.3)]:
 set_trial(rate,exponent,lat);hit=[];body=[]
 for frame in range(1,122,3):
  s.frame_set(frame);r.update_tag();bpy.context.view_layer.update();wing=tree('SB_MainWing_-1')
  if wing.overlap(tree('SB_LandingSkidCannon_-1')):hit.append(frame)
  if wing.overlap(tree('SB_FixedTailFuselage')):body.append(frame)
 result={'roll_rate':rate,'skid_exponent':exponent,'lateral_m':lat,'hits':hit,'body_hits':body};results.append(result)
 if not hit and not body:break
best=next((d for d in results if not d['hits'] and not d['body_hits']),None)
if best:
 set_trial(best['roll_rate'],best['skid_exponent'],best['lateral_m']);s.frame_set(1);r.update_tag();bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Switchblade_V5_Assembly.blend'),compress=True)
(A/'hinge_trajectory_search.json').write_text(json.dumps({'trials':results,'selected':best},indent=2));print('HINGE_SEARCH',json.dumps(results),'BEST',best)
