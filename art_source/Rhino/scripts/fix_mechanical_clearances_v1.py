import bpy,ast,re,json,shutil
from pathlib import Path
from mathutils import Vector
from math import sin,cos,pi
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Rhino';S=bpy.context.scene;R=bpy.data.objects['Rhino_Control'];assert not S.get('mechanical_clearances_v1')
shutil.copy2(A/'validation_v1.json',A/'validation_v1_before_clearance_fix.json')
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Rhino_V1_before_clearance_fix.blend'),copy=True,compress=True)
tree=ast.parse((A/'scripts/build_rhino_v1.py').read_text(encoding='utf-8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'<helpers>','exec'))
S.frame_set(1);bpy.context.view_layer.update()
for sg in [-1,1]:
 bpy.data.objects['RH_ExhaustCannonPivot_'+str(sg)].location.y+=sg*.07
 hinge=bpy.data.objects['RH_StackFixedHinge_'+str(sg)]
 for v in hinge.data.vertices:v.co.y+=sg*.07
ramp=bpy.data.objects['RH_RearCockpitHatchPivot'];matrices={ob:ob.matrix_world.copy() for ob in ramp.children};ramp.location.z=1.47;bpy.context.view_layer.update()
for ob,matrix in matrices.items():
 ob.matrix_parent_inverse=ramp.matrix_world.inverted();ob.matrix_world=matrix
 if ob.type=='MESH':
  for v in ob.data.vertices:v.co.y*=1.70/2.15
ramp.driver_remove('rotation_euler',1)
drive(ramp,'rotation_euler',1,'-2.108*max(v,min(1,max(0,(b-0.42)/0.36)))',[('v',R,'rear_open'),('b',R,'battle_mode')])
for sg in [-1,1]:
 hinge=bpy.data.objects['RH_HatchHinge_'+str(sg)]
 for v in hinge.data.vertices:v.co.z+=.18;v.co.y*=1.70/2.15
CURRENT=bpy.data.collections['Rhino_Truck'];red=bpy.data.materials['Rhino_DeepBurgundy']
for sg in [-1,1]:parent(box('RH_RearCabinetWing_'+str(sg),(-.72,sg*1.015,2.79),(.10,.27,2.94),red,.022),R)
S['mechanical_clearances_v1']='Exhaust/cannon lateral clearance +70mm; 1.70m ramp at raised hinge 1.47m, 120.8deg open; fixed rear wings. Estimated mechanics.'
S.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Rhino_V1.blend'),compress=True);print('RHINO_MEASURED_MECHANICAL_CLASHES_CORRECTED')
