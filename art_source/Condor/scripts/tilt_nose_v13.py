import bpy
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Condor'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
c=bpy.data.objects['Condor_AngularFrontCowl']
for v in c.data.vertices:
 if v.index<8 or v.index>=32:v.co.x=1.36-.35*(v.co.z-.78)
for v in bpy.data.objects['Condor_SquareWeaponSocket'].data.vertices:
 if v.co.x>1.30:v.co.x=1.362-.35*(v.co.z-.78)
c['front_face_note']='Weapon aperture face tilts upward about 19 degrees; lower edge farther forward. User correction 2026-11-12.'
bpy.context.scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(A/'Condor_V13_Assembly.blend'),compress=True)
print('UPWARD_NOSE_FACE_V13_SAVED')
