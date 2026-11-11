import bpy,ast,re,shutil
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Rhino';S=bpy.context.scene;R=bpy.data.objects['Rhino_Control']
assert not S.get('ramp_final_clearance_v1');shutil.copy2(A/'validation_v1.json',A/'validation_v1_ramp_second_review.json')
tree=ast.parse((A/'scripts/build_rhino_v1.py').read_text(encoding='utf-8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'<helpers>','exec'))
S.frame_set(1);bpy.context.view_layer.update();ramp=bpy.data.objects['RH_RearCockpitHatchPivot'];matrices={ob:ob.matrix_world.copy() for ob in ramp.children};ramp.location.z=1.50;bpy.context.view_layer.update()
for ob,matrix in matrices.items():ob.matrix_parent_inverse=ramp.matrix_world.inverted();ob.matrix_world=matrix
ramp.driver_remove('rotation_euler',1);drive(ramp,'rotation_euler',1,'-2.126*max(v,min(1,max(0,(b-0.42)/0.36)))',[('v',R,'rear_open'),('b',R,'battle_mode')])
for sg in [-1,1]:
 for v in bpy.data.objects['RH_HatchHinge_'+str(sg)].data.vertices:v.co.z+=.03
S['ramp_final_clearance_v1']='Hinge 1.50m, angle 121.81 degrees; 30mm final adjustment after evaluated-frame clash check.'
S.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Rhino_V1.blend'),compress=True);print('RHINO_RAMP_FINAL_CLEARANCE_SAVED')
