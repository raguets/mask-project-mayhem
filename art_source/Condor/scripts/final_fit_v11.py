import bpy
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Condor'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
CURRENT=bpy.data.collections['Condor_Vehicle'];PARENT=bpy.data.objects['Condor_Control'];black=bpy.data.materials['Condor_Charcoal']
# Correct the local geometry offset after shortening the rotor support hierarchy.
for o in CURRENT.all_objects:
 if o.type=='MESH' and o.name.startswith(('Condor_MainBlade','Condor_MainRotorSpindle')):
  for v in o.data.vertices:v.co.x-=.222
for side in [-1,1]:tube('Condor_RearPivotChassisBracket_'+str(side),(-1.45,side*.10,.72),(-1.57,side*.11,.80),.042,black)
bpy.context.scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(A/'Condor_V11_Assembly.blend'),compress=True)
print('ROTOR_ALIGNMENT_AND_FIXED_BRACKETS_SAVED')
