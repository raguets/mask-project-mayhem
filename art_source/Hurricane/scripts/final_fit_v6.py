import bpy,bmesh
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Hurricane';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
S.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Session_before_fit_v6.blend'),copy=True,compress=True)
exec(compile((A/'scripts/geometry.py').read_text(),'<geometry>','exec'))
ROOT=bpy.data.objects['Hurricane_Control']
for sg,label in [(1,'L'),(-1,'R')]:drive(bpy.data.objects['HU_CentreWheelLateral_'+label],'location',1,str(sg*.04)+'*l',[('l',ROOT,'_lift')])
# Reserve clearance for the cannon envelope throughout the roof's rotation.
roof=bpy.data.objects['HU_OpeningRoofPanel'];bm=bmesh.new();bm.from_mesh(roof.data)
bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_center_median().x<.12 and .055<abs(f.calc_center_median().y)<.23],context='FACES');bm.to_mesh(roof.data);bm.free()
for v in roof.data.vertices:
 if v.co.x>.58:v.co.x-=.012*min(1,(v.co.x-.58)/.02)
for o in S.objects:
 if o.name.startswith('HU_RoofSlotCover_'):
  for v in o.data.vertices:v.co.x=-.45+(v.co.x+.45)*(.57/.25)
 if o.name.startswith('HU_RaisedRoofHingeBracket_'):
  # The fixed bracket stops at the elevated hinge rather than crossing the lid.
  for v in o.data.vertices:
   if v.co.x<.64:v.co.x=.64+(v.co.x-.60)*.15
 if o.name.startswith('HU_FrontFenderCrown_'):
  # Raise the gun-channel inner crown by 16mm, preserving its outer belt join.
  for v in o.data.vertices:
   t=max(0,min(1,(abs(v.co.y)-.60)/.34));v.co.z+=.016*sin(pi*t)
cover=bpy.data.objects['HU_WindshieldCannonCover']
for v in cover.data.vertices:v.co.x+=.012
for o in S.objects:
 if o.animation_data:
  for fc in o.animation_data.drivers:fc.driver.expression=fc.driver.expression.replace(' + 0.0','')+' + 0.0'
 o.update_tag()
S.frame_set(151);S.frame_set(1);bpy.context.view_layer.update();S.name='Hurricane_V6_Assembly';S['asset']='Hurricane V6 - reduced lift, tall black structure, right windshield cannon'
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Hurricane_V6_Assembly.blend'),compress=True);print('FIT_V6_SAVED')
