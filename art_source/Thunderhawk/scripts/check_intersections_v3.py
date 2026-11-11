import bpy,os,math
from mathutils.bvhtree import BVHTree
s=bpy.context.scene; root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def tree(ob):
 e=ob.evaluated_get(bpy.context.evaluated_depsgraph_get()); me=e.to_mesh(); t=BVHTree.FromPolygons([e.matrix_world @ v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons]); e.to_mesh_clear(); return t
pairs=[('THK_Wing_L','THK_Body'),('THK_Wing_R','THK_Body'),('THK_Wing_L','THK_Roof'),('THK_Wing_R','THK_Roof'),('THK_RearHatch','THK_Body'),('THK_RearHatch','THK_Reactor_L'),('THK_RearHatch','THK_Reactor_R'),('THK_RearHatch','THK_RearStabilizer'),('THK_RearHatch','THK_StabilizerSupport_L'),('THK_RearHatch','THK_StabilizerSupport_R')]
with open(os.path.join(root,'intersection_v3.csv'),'w',encoding='utf8') as f:
 f.write('frame,object_a,object_b,triangle_pairs\n')
 for frame in range(1,194):
  s.frame_set(frame)
  for a,b in pairs: f.write('%d,%s,%s,%d\n'%(frame,a,b,len(tree(bpy.data.objects[a]).overlap(tree(bpy.data.objects[b])))))
 for frame in [1,45,55,85,121,161,165,193]:
  s.frame_set(frame); p=bpy.data.objects['THK_RearPanel_Lift']; a=bpy.data.objects['THK_RearStabilizer']; print('REAR_STATE',frame,'panel_z',round(p.location.z,4),'panel_rotation_deg',tuple(round(math.degrees(x),4) for x in p.rotation_euler),'spoiler_z',round(a.location.z,4),'independent',a.parent.name)
print('SWEEP_DONE')
