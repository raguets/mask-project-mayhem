import bpy
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
S.frame_set(1)
factor=(1.56-.38)/(1.95-.38)
for i in [1,2]:
    pivot=bpy.data.objects['BH_PumpCannonPivot_'+str(i)];pivot.location.z=1.60;bpy.context.view_layer.update()
    for ob in pivot.children:
        ob.matrix_parent_inverse=pivot.matrix_world.inverted()
        if ob.type=='MESH':
            for v in ob.data.vertices:v.co.z=.38+(v.co.z-.38)*factor
        elif ob.type=='CURVE':
            for sp in ob.data.splines:
                for p in sp.points:p.co.z=.38+(p.co.z-.38)*factor
S['pump_mechanism_note']='Blue barrel pivots below the fixed meter head; hidden swivel assembly interpreted.'
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P/'art_source/Boulder_Hill/BoulderHill_V2_Assembly.blend'),compress=True)
print('PUMP_CLEARANCE_FIXED')
