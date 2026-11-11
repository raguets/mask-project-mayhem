import bpy
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
S.frame_set(1)
for o in S.objects:
    if o.type=='MESH' and o.name.startswith(('BH_PrismArmorChannel_','BH_PrismSideEdge_')):
        ymin=min(v.co.y for v in o.data.vertices);ymax=max(v.co.y for v in o.data.vertices);limit=-5.60 if o.name.startswith('BH_PrismArmorChannel_') else -5.57
        if ymax>limit:
            scale=(limit-ymin)/(ymax-ymin)
            for v in o.data.vertices:v.co.y=ymin+(v.co.y-ymin)*scale
S.frame_set(211);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P/'art_source/Boulder_Hill/BoulderHill_V4_Assembly.blend'),compress=True)
print('STIFFENER_ROOF_CLEARANCE')
