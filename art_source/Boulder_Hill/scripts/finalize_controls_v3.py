import bpy,json,re
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');S=bpy.context.scene;R=bpy.data.objects['BoulderHill_Control']
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
S.frame_set(1)
cap=bpy.data.objects['BH_FallingBoulder']
for index,vals in [(0,(7,11,29,26)),(1,(6,1,-8,-7)),(2,(13.22,17.3,8,.85))]:
    a,b,c,d=vals;f=cap.driver_add('location',index);f.driver.expression=f'{a}*(1-t)**3+{3*b}*(1-t)**2*t+{3*c}*(1-t)*t*t+{d}*t**3'
    while f.driver.variables:f.driver.variables.remove(f.driver.variables[0])
    v=f.driver.variables.new();v.name='t';v.type='SINGLE_PROP';v.targets[0].id=R;v.targets[0].data_path='["_cap"]'
cap['trajectory_note']='Estimated forward/right drop clears the enlarged backing mountain and lands outside the rectangular slab, at (26,-7,.85). Animated path, not dynamics.'
# Keep drivers short; Blender limits scripted expressions to 255 characters.
garage=bpy.data.objects['BH_GarageQuarterPivot'];f=garage.driver_add('rotation_euler',2)
while f.driver.variables:f.driver.variables.remove(f.driver.variables[0])
v=f.driver.variables.new();v.name='g';v.type='SINGLE_PROP';v.targets[0].id=R;v.targets[0].data_path='["_garage"]';f.driver.expression='-1.57079632679*g'
for o in S.objects:
    if o.animation_data:
        for f in o.animation_data.drivers:f.driver.expression=f.driver.expression.replace(' + 0.0','')+' + 0.0'
    o.update_tag()
for fr in [1,65,130,181,211,311,510,541,1]:S.frame_set(fr);bpy.context.view_layer.update()
bad=[o.name+':'+f.data_path for o in S.objects if o.animation_data for f in o.animation_data.drivers if not f.driver.is_valid]
assert not bad,bad
S.name='BoulderHill_V3_Assembly';S['BoulderVersion']='V3'
text=bpy.data.texts.get('ASSET_README') or bpy.data.texts.new('ASSET_README');text.clear();text.write('BOULDER HILL V3\nSelect BoulderHill_Control. Timeline: 1 station; 65 prism halfway; 181 defense; 211 gate open; 311 Thunderhawk exit; 510 Rhino exit. Native editable drivers, no Python namespace needed after reopen.\nThe storefront is a SINGLE triangular prism: its glazed face folds to the ground while its inclined steel face becomes exposed. Backing mountain roughly 46m high. Simple rectangular slab, no exit road. Four interpreted parking bays.\nIndependent environment: BoulderHill_V3_Base.blend. Assembly includes road-state demo copies of Thunderhawk V14 and Rhino V3; original vehicle sources unchanged.\nDimensions, hidden mechanisms, mountain terrain, interior and cap trajectory are interpretations. See README.md and QA reports for exact validation scope.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(P/'art_source/Boulder_Hill/BoulderHill_V3_Assembly.blend'),compress=True)
print('FINAL_CONTROLS_SAVED invalid=',bad)
