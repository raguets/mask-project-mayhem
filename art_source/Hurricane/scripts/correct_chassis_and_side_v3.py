import bpy,bmesh,json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Hurricane';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
S.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Session_before_user_chassis_correction_v3.blend'),copy=True,compress=True)
exec(compile((A/'scripts/geometry.py').read_text(),'<geometry>','exec'))
ROOT=bpy.data.objects['Hurricane_Control'];LIFT=bpy.data.objects['HU_UpperChassisLift'];R=bpy.data.objects['HondoMacLean_Rig'];BLACK=bpy.data.materials['HU_ChassisGraphite'];CURRENT=bpy.data.collections['HU_RunningGear'];PARENT=ROOT;GROUP='lower_chassis'
drive(LIFT,'location',2,'.30*l',[('l',ROOT,'_lift')]);drive(R,'location',2,'a*(.36+.71*g+.30*l)',[('a',R,'in_vehicle'),('g',R,'gunner_pose'),('l',R,'vehicle_lift')])
spare=bpy.data.objects['HU_SpareEjection'];drive(spare,'location',2,'.96+e-1.56*e*e-.30*l*e',[('e',ROOT,'spare_eject'),('l',ROOT,'_lift')])
for o in S.objects:
    if o.name.startswith('HU_ShockExtension_'):drive(o,'scale',2,'1+1.5*l',[('l',ROOT,'_lift')])
# Black telescopic central carrier: top follows the underside of the rising floor.
core=empty('HU_TallBlackChassisCore',(-.10,0,.17),ROOT);drive(core,'scale',2,'1+1.875*l',[('l',ROOT,'_lift')]);box('HU_BlackStructuralCore',(-.10,0,.25),(3.10,1.10,.16),BLACK,.018,core)
for x in [-.72,.72]:
    for sg in [-1,1]:
        post=empty('HU_BetweenWheelUpright_'+str((x,sg)),(x,sg*.76,.18),ROOT);drive(post,'scale',2,'1+1.20*l',[('l',ROOT,'_lift')]);box('HU_BlackUprightWeb_'+str((x,sg)),(x,sg*.76,.30),(.36,.17,.24),BLACK,.018,post)
        box('HU_BlackCarrierUpperRail_'+str((x,sg)),(x,sg*.71,.32),(.85,.12,.09),BLACK,.012,LIFT)
# Mirror the aperture, hatch, and complete cannon to the vehicle's right (-Y).
glass=bpy.data.objects['HU_WraparoundWindshield']
for v in glass.data.vertices:v.co.y=-v.co.y
bm=bmesh.new();bm.from_mesh(glass.data);bmesh.ops.reverse_faces(bm,faces=bm.faces);bm.to_mesh(glass.data);bm.free()
for name in ['HU_WindshieldHatchHinge','HU_WindshieldGunSlide']:
    root=bpy.data.objects[name];root.location.y=-root.location.y;root.update_tag();bpy.context.view_layer.update()
    for o in root.children:
        if o.type=='MESH':
            for v in o.data.vertices:v.co.y=-v.co.y
            bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.reverse_faces(bm,faces=bm.faces);bm.to_mesh(o.data);bm.free()
        elif o.type=='CURVE':
            for sp in o.data.splines:
                for p in sp.points:p.co.y=-p.co.y
        o.matrix_parent_inverse=root.matrix_world.inverted()
drive(bpy.data.objects['HU_WindshieldHatchHinge'],'rotation_euler',2,'1.65*min(1,w/.45)',[('w',ROOT,'_wind')])
bpy.data.objects['HU_LeftWindshieldBarrel'].name='HU_RightWindshieldBarrel'
ROOT['lift_travel_m']=.30;ROOT['user_correction']='Body lift reduced to 0.30m; middle tire top remains about 0.12m behind body edge. Taller full black carrier and uprights between wheels. Windshield cannon on right (-Y), corrected by user.'
for o in S.objects:
    if o.animation_data:
        for f in o.animation_data.drivers:f.driver.expression=f.driver.expression.replace(' + 0.0','')+' + 0.0'
    o.update_tag()
S.frame_set(151);bpy.context.view_layer.update();S.frame_set(1);bpy.context.view_layer.update();S.name='Hurricane_V3_Assembly';S['asset']='Hurricane V3 user chassis correction'
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Hurricane_V3_Assembly.blend'),compress=True);print('USER_CHASSIS_AND_RIGHT_CANNON_V3_SAVED')
