import bpy
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Condor'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
CURRENT=bpy.data.collections['Condor_Vehicle'];root=bpy.data.objects['Condor_Control'];PARENT=root
rear=bpy.data.objects['Condor_RearWheelPivot'];rear.location.x-=.86
body=bpy.data.objects['Condor_RearMonobloc']
for v in body.data.vertices:
 if v.co.x< -1.30:v.co.x=-1.30+(v.co.x+1.30)*.81
cut=tube('Condor_RearWheelWell_Cutter',(-1.85,-.13,.355),(-1.85,.13,.355),.374,bpy.data.materials['Condor_Charcoal'],N=72)
cut.hide_render=True;cut.hide_set(True);cut.display_type='WIRE'
mod=body.modifiers.new('EditableRearWheelHousing','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut
for o in CURRENT.all_objects:
 if o.name.startswith('Condor_AngularBlackInset'):
  for v in o.data.vertices:v.co.y+=.020 if v.co.y>0 else -.020
root['rear_fit_note']='Rear wheel moved to actual rear of monobloc; editable boolean housing, same wheel becomes tail rotor.'
bpy.context.scene.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Condor_V5_Assembly.blend'),compress=True)
print('REAR_WHEEL_FIT_CORRECTED')
