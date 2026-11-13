import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Condor';s=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
s.frame_set(1);bpy.context.view_layer.update();spin=bpy.data.objects['Condor_TailRotorSpin'];tire=bpy.data.objects['Condor_Rear_PersistentTire'];dg=bpy.context.evaluated_depsgraph_get();ev=tire.evaluated_get(dg);me=ev.to_mesh();pts=[ev.matrix_world@v.co for v in me.vertices];center=Vector([(min(p[i] for p in pts)+max(p[i] for p in pts))/2 for i in range(3)]);ev.to_mesh_clear();delta=spin.matrix_world.translation-center;names=[]
for o in bpy.data.collections['Condor_Vehicle'].all_objects:
 if o.type=='MESH' and o.name.startswith(('Condor_Rear_PersistentTire','Condor_Rear_Rim','Condor_Rear_ThreeSpoke','Condor_Rear_Hub','Condor_Rear_Tread')):
  matrix=o.matrix_world.copy();matrix.translation+=delta;o.parent=spin;o.matrix_parent_inverse=spin.matrix_world.inverted();o.matrix_world=matrix;names.append(o.name)
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Condor_V17_Assembly.blend'),compress=True)
(A/'wheel_hierarchy_v17.json').write_text(json.dumps({'old_center':list(center),'new_center':list(spin.matrix_world.translation),'reparented':names},indent=2));print('ACTUAL_WHEEL_REBOUND',len(names),list(delta))
