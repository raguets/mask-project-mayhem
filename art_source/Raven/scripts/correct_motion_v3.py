import bpy,json,math
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Raven';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
assert not (A/'Raven_V3_Assembly.blend').exists()
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(encoding='utf-8'),'<geometry>','exec'))
root=bpy.data.objects['Raven_Control'];S.frame_set(1)
# Keep the transform control floating-point: integer ID-properties stepped.
root.animation_data_clear();root['transform']=0.
for f,value in [(1,0.),(31,0.),(121,1.),(151,1.)]:root['transform']=value;root.keyframe_insert(data_path='["transform"]',frame=f)
for layer in root.animation_data.action.layers:
    for strip in layer.strips:
        for bag in strip.channelbags:
            for fcurve in bag.fcurves:
                for key in fcurve.keyframe_points:key.interpolation='LINEAR'
hood=bpy.data.objects['RV_Hood_LongitudinalPivot']
# Interpreted cam lift provides a swept-volume reserve for the rotating shell.
drive(hood,'location',2,'.71+.75*sin(3.141592653589793*t)',[('t',root,'transform')])
hood['mechanism_estimate']='Unshown cam lift peaks at0.75m while rotating on longitudinal axis; simultaneous with all other mechanisms. Estimated clearance, not official kinematics.'
deck=bpy.data.objects['RV_HoodBayArmoredDeck']
for v in deck.data.vertices:v.co.x=1.24+(v.co.x-1.28)*(1.55/1.70)
for v in bpy.data.objects['RV_RearUndertray'].data.vertices:v.co.z+=.10
for side in ['L','R']:
    for axle,x in [('Front','1.22'),('Rear','-1.22')]:
        panel=bpy.data.objects['RV_WheelWellBulkhead_'+side+x];fold=bpy.data.objects['RV_'+axle+'WheelFold_'+side]
        matrix=panel.matrix_world.copy();panel.parent=fold;panel.matrix_parent_inverse=fold.matrix_world.inverted();panel.matrix_world=matrix
        panel['mechanism_estimate']='Inner liner follows the folding wheel carrier; unshown mounting interpreted.'
root['hover_height']=0.;root['disc_launch']=0.;R=bpy.data.objects['CalhounBurns_Rig'];R['driving_pose']=1.;R['in_vehicle']=1.;R['mask_on']=False
S.frame_set(1);R.update_tag();bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Raven_V3_Assembly.blend'),compress=True)
print('RAVEN_V3_MOTION_CORRECTED')
