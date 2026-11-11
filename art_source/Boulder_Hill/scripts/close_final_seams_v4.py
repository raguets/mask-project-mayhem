import bpy,json,math
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
S.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'art_source/Boulder_Hill/Session_before_final_seams_v4.blend'),copy=True,compress=True)
outer=bpy.data.objects['BH_RockColumnOuter'];rim=bpy.data.objects['BH_RockColumnInnerRim']
for i in range(128):outer.data.vertices[48*128+i].co=rim.data.vertices[i].co
# Match the complete side-portal width, including the ramp down to terrain.
left=bpy.data.objects['BH_RockFrontReturn_Left']
for v in left.data.vertices:
    if abs(v.co.x+12.9)<.01:v.co.x=-15.7
    elif abs(v.co.x+13.8)<.01:v.co.x=-16.2
right=bpy.data.objects['BH_RockFrontReturn_Right']
for v in right.data.vertices:
    if abs(v.co.x-14.7)<.01:v.co.x=17.5
    elif abs(v.co.x-15.4)<.01:v.co.x=18.0
# Slightly deepen the same prism to meet the underside of the roof when deployed.
pivot=bpy.data.objects['BH_StorefrontPivot'];scale=5.45/5.30
for ob in pivot.children:
    if ob.type=='MESH':
        for v in ob.data.vertices:v.co.y=-11+(v.co.y+11)*scale
    elif ob.type=='CURVE':
        for sp in ob.data.splines:
            for p in sp.points:p.co.y=-11+(p.co.y+11)*scale
    elif ob.type=='FONT':ob.location.y=-11+(ob.location.y+11)*scale
pivot['cross_section_m']=[5.3,5.45]
for ob in S.objects:ob.update_tag()
S.frame_set(211);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P/'art_source/Boulder_Hill/BoulderHill_V4_Assembly.blend'),compress=True)
print('FINAL_SEAMS_CLOSED')
