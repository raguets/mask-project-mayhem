import bpy
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Condor'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
c=bpy.data.objects['Condor_AngularFrontCowl']
for v in c.data.vertices:
 if v.index<8:
  v.co.x=1.36
  v.co.z=[.87,.87,.825,.72,.70,.70,.72,.825][v.index]
 elif v.index<16:
  if v.index%8 in [0,1]:v.co.z=.975
  elif v.index%8 in [2,7]:v.co.z=.925
 elif v.index>=32:
  v.co.x=1.365;v.co.y*=.75;v.co.z=.78+(v.co.z-.816)*.75
socket=bpy.data.objects['Condor_SquareWeaponSocket']
for v in socket.data.vertices:
 if v.co.x>1.40:v.co.x=1.364
 v.co.y*=.75;v.co.z=.78+(v.co.z-.816)*.75
for o in bpy.data.objects['Condor_HeadlampCannon'].children:
 if o.type=='MESH':
  for v in o.data.vertices:v.co.x-=.04;v.co.z-=.036
c['nose_profile']='Short nose top follows windshield descent: screen lower (1.20,0.99), nose (1.36,0.87). User 2026-11-12.'
bpy.context.scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(A/'Condor_V10_Assembly.blend'),compress=True)
print('SHORT_CONTINUOUS_NOSE_V10_SAVED')
