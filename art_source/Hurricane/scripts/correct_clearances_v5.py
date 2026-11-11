import bpy,bmesh,math
from pathlib import Path
from mathutils import Vector
from math import sin,cos,pi
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Hurricane';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
S.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Session_before_clearances_v5.blend'),copy=True,compress=True)
exec(compile((A/'scripts/geometry.py').read_text(),'<geometry>','exec'))
ROOT=bpy.data.objects['Hurricane_Control'];R=bpy.data.objects['HondoMacLean_Rig'];ROOF=bpy.data.objects['HU_RoofHinge'];LIFT=bpy.data.objects['HU_UpperChassisLift'];TEAL=bpy.data.materials['HU_TurquoisePaint'];CHROME=bpy.data.materials['HU_Chrome'];CURRENT=bpy.data.collections['HU_Body'];PARENT=LIFT;GROUP='body'
# Keep middle tire sidewalls behind the partially covering lower door edge.
for sg,label in [(1,'L'),(-1,'R')]:drive(bpy.data.objects['HU_CentreWheelLateral_'+label],'location',1,str(sg*.10)+'*l',[('l',ROOT,'_lift')])
# Real front-fender gun cavities replace overlapping skin behind each lamp pod.
for label in ['L','R']:
    o=bpy.data.objects['HU_SculptedSide_'+label];bm=bmesh.new();bm.from_mesh(o.data);faces=[f for f in bm.faces if f.calc_center_median().x>2.0 and f.calc_center_median().z>.78];bmesh.ops.delete(bm,geom=faces,context='FACES');bm.to_mesh(o.data);bm.free()
    pod=bpy.data.objects['HU_TurquoiseHeadlampPod_'+label]
    for v in pod.data.vertices:
        if v.co.x<2.2:v.co.x=1.99
# Hood and lip leave a reserved lane between each gun housing and central hood.
for name in ['HU_CurvedHood','HU_HoodFrontLip']:
    for v in bpy.data.objects[name].data.vertices:v.co.y*=.60/.68
for o in S.objects:
    if o.name.startswith('HU_HoodSideShutLine_'):
        for sp in o.data.splines:
            for p in sp.points:p.co.y*=.605/.69
for o in S.objects:
    if o.name.startswith('HU_FrontFenderCrown_'):
        for v in o.data.vertices:
            x,y,z=v.co;w=profile(x,[(-2.62,.88),(-2.38,.97),(-1.4,.97),(0,.98),(1.5,.94),(2.27,.94),(2.55,.85)]);t=(abs(y)-.64)/(w-.64);v.co.y=(1 if y>0 else -1)*(.60+(w-.60)*t);base=profile(x,[(.89,1.145),(1.45,1.13),(2.37,1.045)]);belt=profile(x,[(-2.62,1.28),(-2.28,1.22),(-1.25,1.12),(.15,1.13),(.85,1.12),(1.8,1.10),(2.55,1.12)]);v.co.z=base*(1-t)+belt*t+.080*sin(pi*t)
# A small raised hinge clears the curved front header instead of rotating through it.
children={o:o.matrix_world.copy() for o in ROOF.children};ROOF.location=(.68,0,1.73);ROOF.update_tag();bpy.context.view_layer.update()
for o,m in children.items():o.matrix_parent_inverse=ROOF.matrix_world.inverted();o.matrix_world=m
for o in S.objects:
    if o.name.startswith('HU_RoofHingePin_'):
        for v in o.data.vertices:v.co.x+=.08;v.co.z+=.07
for sg in [-1,1]:tube('HU_RaisedRoofHingeBracket_'+str(sg),(.60,sg*.50,1.65),(.68,sg*.50,1.73),.018,CHROME,root=LIFT)
# Preserve the final hand-to-cannon fit after the corrected hinge changes gun height.
drive(R,'location',0,'a*(-.10+.16*g+.50*min(1,g/.15)*(1-g))',[('a',R,'in_vehicle'),('g',R,'gunner_pose')]);u='min(1,max(0,(g-.18)/.82))';drive(R,'location',2,'a*(.36+.86*('+u+')**2*(3-2*('+u+'))+.30*l)',[('a',R,'in_vehicle'),('g',R,'gunner_pose'),('l',R,'vehicle_lift')]);drive(bpy.data.objects['HU_GunnerFootPlatform'],'location',2,'.58+.62*p',[('p',ROOT,'_roofgun')])
# Real small gaps along the closed roof seal, not interpenetrating side rails.
for name in ['HU_OpeningRoofPanel']+[o.name for o in S.objects if o.name.startswith('HU_RoofSlotCover_')]:
    for v in bpy.data.objects[name].data.vertices:
        if abs(v.co.y)>.58:
            t=min(1,(abs(v.co.y)-.58)/.06);v.co.y-=(1 if v.co.y>0 else -1)*.010*t*t*(3-2*t)
        if v.co.x<-.43:v.co.x+=.006*min(1,(-.43-v.co.x)/.02)
# Weather-strip clearance around the right windshield port, including its hinge edge.
cover=bpy.data.objects['HU_WindshieldCannonCover'];center=sum((v.co for v in cover.data.vertices),Vector())/len(cover.data.vertices)
for v in cover.data.vertices:v.co.y=center.y+(v.co.y-center.y)*.96;v.co.z=center.z+(v.co.z-center.z)*.96
drive(bpy.data.objects['HU_SpareEjection'],'location',2,'.96+e-1.608*e*e-.30*l*e',[('e',ROOT,'spare_eject'),('l',ROOT,'_lift')])
for o in S.objects:
    if o.animation_data:
        for f in o.animation_data.drivers:f.driver.expression=f.driver.expression.replace(' + 0.0','')+' + 0.0'
    o.update_tag()
S.frame_set(151);S.frame_set(1);bpy.context.view_layer.update();S.name='Hurricane_V5_Assembly';S['asset']='Hurricane V5 evaluated clearance corrections';S['roof_hinge_note']='Estimated raised hinge to clear the curved header; telescope platform and Hondo final placement preserve hand grip. Body lift remains user-corrected 0.30m.'
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Hurricane_V5_Assembly.blend'),compress=True);print('CLEARANCE_CORRECTIONS_V5_SAVED')
