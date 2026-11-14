import bpy,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
S=bpy.context.scene;A=Path('G:/DEV/mask-project-mayhem/art_source/Manta');D=json.loads((A/'proportions_v13.json').read_text());fx=D['front_axle_x']
def surf(o):
 dg=bpy.context.evaluated_depsgraph_get();e=o.evaluated_get(dg);me=e.to_mesh();v=[e.matrix_world@p.co for p in me.vertices];f=[list(p.vertices) for p in me.polygons];e.to_mesh_clear();return BVHTree.FromPolygons(v,f),v,f
r=[]
for frame in [1,41,61,81,101,111,121]:
 S.frame_set(frame);bpy.context.view_layer.update();bt,bv,bf=surf(bpy.data.objects['MA_MainBody']);wt,wv,wf=surf(bpy.data.objects['MA_FrontWheel_1_Tire']);ov=bt.overlap(wt)
 r.append({'frame':frame,'centre':list(sum(wv,Vector())/len(wv)),'max_wheel_xz_r':max(math.hypot(p.x-fx,p.z-.34) for p in wv),'overlap_pairs':len(ov),'hit_body_points':[list(bv[bf[i][0]]) for i,j in ov[:8]]})
S.frame_set(1);(A/'contact_diagnosis_v16.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
