import bpy, os
from mathutils.bvhtree import BVHTree
s=bpy.context.scene
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def tree(ob):
 dg=bpy.context.evaluated_depsgraph_get(); e=ob.evaluated_get(dg); me=e.to_mesh(); verts=[e.matrix_world @ v.co for v in me.vertices]; polys=[tuple(p.vertices) for p in me.polygons]; t=BVHTree.FromPolygons(verts,polys); e.to_mesh_clear(); return t
with open(os.path.join(root,'intersection_v1.csv'),'w',encoding='utf8') as f:
 f.write('frame,wing,body_triangle_pairs,roof_triangle_pairs\n')
 for frame in range(1,194):
  s.frame_set(frame)
  for side in 'LR':
   a=tree(bpy.data.objects['THK_Wing_'+side]); body=tree(bpy.data.objects['THK_Body']); roof=tree(bpy.data.objects['THK_Roof'])
   f.write('%d,%s,%d,%d\n'%(frame,side,len(a.overlap(body)),len(a.overlap(roof))))
print('INTERSECTION_SWEEP_COMPLETE 193 frames, both wings')
