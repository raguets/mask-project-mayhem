import bpy,os,math
from mathutils.bvhtree import BVHTree
s=bpy.context.scene; root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def tree(ob):
 dg=bpy.context.evaluated_depsgraph_get(); e=ob.evaluated_get(dg); me=e.to_mesh(); verts=[e.matrix_world @ v.co for v in me.vertices]; polys=[tuple(p.vertices) for p in me.polygons]; t=BVHTree.FromPolygons(verts,polys); e.to_mesh_clear(); return t
pairs=[('THK_Wing_L','THK_Body'),('THK_Wing_R','THK_Body'),('THK_Wing_L','THK_Roof'),('THK_Wing_R','THK_Roof'),('THK_RearHatch','THK_Body'),('THK_RearHatch','THK_Reactor_L'),('THK_RearHatch','THK_Reactor_R')]
with open(os.path.join(root,'intersection_v2.csv'),'w',encoding='utf8') as f:
 f.write('frame,object_a,object_b,triangle_pairs\n')
 for frame in range(1,194):
  s.frame_set(frame)
  for a,b in pairs:
   f.write('%d,%s,%s,%d\n'%(frame,a,b,len(tree(bpy.data.objects[a]).overlap(tree(bpy.data.objects[b])))))
 for frame in [1,61,85,97,121,157,173,193]:
  s.frame_set(frame); print('HATCH_ANGLE',frame,round(math.degrees(bpy.data.objects['THK_RearHatch_Hinge'].rotation_euler.y),3))
print('SWEEP_DONE')
