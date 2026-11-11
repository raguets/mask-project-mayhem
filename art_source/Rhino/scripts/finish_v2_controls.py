import bpy,ast,re
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Rhino';S=bpy.context.scene;R=bpy.data.objects['Rhino_Control'];assert Path(bpy.data.filepath).name=='Rhino_V2.blend'
tree=ast.parse((A/'scripts/build_rhino_v1.py').read_text(encoding='utf-8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'<helpers>','exec'))
S.frame_set(1);bpy.context.view_layer.update();launch=bpy.data.objects['RH_MissileLauncherLift'];launch.driver_remove('location',2)
request='max(v,min(1,max(0,(b-0.85)/0.15)))';rear='min(1,max(0,(max(h,min(1,max(0,(b-0.42)/0.36)))-0.92)/0.08))';cab='min(1,max(0,(max(c,min(1,max(0,(b-0.50)/0.33)))-0.95)/0.05))';u='min('+request+','+rear+','+cab+')'
drive(launch,'location',2,'2.74+0.90*('+u+')',[('v',R,'launcher_up'),('h',R,'rear_open'),('c',R,'cabinet_slide'),('b',R,'battle_mode')])
CURRENT=bpy.data.collections['Rhino_Truck'];red=bpy.data.materials['Rhino_DeepBurgundy'];slide=bpy.data.objects['RH_RearCabinetSlide']
for sg in [-1,1]:
 ob=bpy.data.objects['RH_UpperCockpitSide_'+str(sg)]
 for v in ob.data.vertices:
  if v.co.x>.9:v.co.x=.79
 if not bpy.data.objects.get('RH_CabinetFrontJamb_'+str(sg)):parent(box('RH_CabinetFrontJamb_'+str(sg),(.91,sg*1.13,2.23),(.20,.085,1.92),red,.012),R)
ob=bpy.data.objects['RH_UpperCockpitRoof']
for v in ob.data.vertices:
 if v.co.x>.28:v.co.x=.245
S.frame_set(151);R.update_tag();bpy.context.view_layer.update()
assert all(f.driver.is_valid for o in [launch,slide,bpy.data.objects['RH_RadarRotation']] for f in o.animation_data.drivers)
assert launch.location.z>3.63 and slide.location.x<-.79
S.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Rhino_V2.blend'),compress=True);print('RHINO_V2_CONTROLS_AND_CABINET_SEAMS_VERIFIED')
