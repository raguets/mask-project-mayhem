import bpy,ast,json
from pathlib import Path
from mathutils import Vector
from math import sin,cos,pi
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Hurricane';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
S.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(A/'Session_before_vehicle_v2.blend'),copy=True,compress=True)
exec(compile((A/'scripts/geometry.py').read_text(),'<geometry>','exec'))
tree=ast.parse((A/'scripts/build_vehicle_v1.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['width','belt','bottom','side_y']],type_ignores=[]),'<surfaces>','exec'))
ROOT=bpy.data.objects['Hurricane_Control'];LIFT=bpy.data.objects['HU_UpperChassisLift'];CURRENT=bpy.data.collections['HU_Body'];PARENT=LIFT;GROUP='body'
TEAL=bpy.data.materials['HU_TurquoisePaint'];CHROME=bpy.data.materials['HU_Chrome'];DARK=bpy.data.materials['HU_Recess'];BLACK=bpy.data.materials['HU_ChassisGraphite'];LEATHER=bpy.data.materials['HU_SeatLeather']
p=next(n for n in TEAL.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Metallic'].default_value=.32;p.inputs['Roughness'].default_value=.30;p.inputs['Coat Weight'].default_value=.25
bpy.data.objects['HU_Key'].data.size=2.2;bpy.data.objects['HU_Key'].data.energy=950;bpy.data.objects['HU_SoftFill'].data.size=4
# Central tires retract inward and stay below the belt line.
centre=bpy.data.objects['HU_CentreAxleRetract'];drive(centre,'location',2,'.74-.36*l',[('l',ROOT,'_lift')]);centre.update_tag();bpy.context.view_layer.update()
for sg,label in [(1,'L'),(-1,'R')]:
    parts=[o for o in list(centre.children) if o.name.startswith('HU_CentreWheel_'+label)]
    lateral=empty('HU_CentreWheelLateral_'+label,parent=centre)
    drive(lateral,'location',1,str(sg*.12)+'*l',[('l',ROOT,'_lift')])
    for o in parts:
        mw=o.matrix_world.copy();o.parent=lateral;o.matrix_parent_inverse=lateral.matrix_world.inverted();o.matrix_world=mw
        if o.type=='MESH':
            for v in o.data.vertices:v.co.y-=sg*.12
        elif o.type=='CURVE':
            for sp in o.data.splines:
                for p in sp.points:p.co.y-=sg*.12
axle=bpy.data.objects['HU_Axle_0'];axle.parent=centre;axle.matrix_parent_inverse=centre.matrix_world.inverted()
for v in axle.data.vertices:v.co.z+=.36
# Cabin-side wheel pockets, instead of hiding tires by clipping them through the floor.
for name in ['HU_CabinFloor','HU_FloorCarpet']:
    o=bpy.data.objects[name]
    for v in o.data.vertices:v.co.y*=1.10/(1.31 if name=='HU_CabinFloor' else 1.27)
for label,sg in [('Driver',1),('Passenger',-1)]:
    for o in list(bpy.data.collections['HU_Interior'].objects):
        if o.name.startswith('HU_'+label+'Seat'):
            if o.type=='MESH':
                for v in o.data.vertices:
                    v.co.y=sg*.37+(v.co.y-sg*.40)*(.85 if 'Pan' in o.name else 1)
            elif o.type=='CURVE':
                for sp in o.data.splines:
                    for p in sp.points:p.co.y-=sg*.03
    old=bpy.data.objects['HU_DoorInnerTrim_'+str(sg)];bpy.data.objects.remove(old,do_unlink=True)
    CURRENT=bpy.data.collections['HU_Interior'];GROUP='interior'
    patch('HU_DoorInnerPocketTrim_'+str(sg),seq(48,-.94,.78),seq(10,.70,1.10),lambda x,z,sg=sg:(x,sg*profile(x,[(-.94,.75),(-.46,.75),(-.35,.55),(.35,.55),(.48,.75),(.78,.75)]),z),LEATHER,sub=0,thick=.014,orient=(0,-sg,0))
    for sp in bpy.data.objects['HU_DoorPull_'+str(sg)].data.splines:
        for p in sp.points:p.co.y=sg*.53
CURRENT=bpy.data.collections['HU_Body'];GROUP='body'
for sg,label in [(1,'L'),(-1,'R')]:
    patch('HU_DoorShoulderClosure_'+label,seq(55,-1.17,1.01),seq(10),lambda x,t,sg=sg:(x,sg*(.825+(side_y(x,belt(x))-.825)*t),1.15*(1-t)+belt(x)*t),TEAL,orient=(0,0,1))
    tube('HU_TurquoiseHeadlampPod_'+label,(2.13,sg*.79,1.),(2.49,sg*.79,1.),.195,TEAL,r2=.188,caps=False)
    tube('HU_HeadlampOuterRing_'+label,(2.47,sg*.79,1.),(2.51,sg*.79,1.),.192,CHROME,r2=.184,caps=False)
patch('HU_HoodFrontLip',seq(12,2.34,2.51),seq(30,-.68,.68),lambda x,y:(x,y,1.047+.020*(1-(y/.68)**2)-.04*((x-2.34)/.17)),TEAL,orient=(0,0,1))
old=bpy.data.objects['HU_HoodShutLine'];bpy.data.objects.remove(old,do_unlink=True)
for sg in [-1,1]:path('HU_HoodSideShutLine_'+str(sg),[(x,sg*.69,profile(x,[(.89,1.145),(1.45,1.13),(2.37,1.045)])+.003) for x in seq(50,.89,2.37)],.003,DARK)
# Taper the windshield into the narrower roof, preserving the left hatch as a real part.
names=['HU_WraparoundWindshield','HU_WindshieldCannonCover']+[o.name for o in S.objects if o.name.startswith(('HU_WindshieldChrome_','HU_A_Pillar_'))]
for name in names:
    o=bpy.data.objects[name]
    points=o.data.vertices if o.type=='MESH' else [p for sp in o.data.splines for p in sp.points]
    for p in points:t=max(0,min(1,(p.co.z-1.15)/.49));p.co.y*=1-.17*t
hatch=bpy.data.objects['HU_WindshieldHatchHinge'];hatch.location.y=.34*(1-.17*.16);bpy.context.view_layer.update()
for o in hatch.children:o.matrix_parent_inverse=hatch.matrix_world.inverted()
# More rounded crown, with a continuous fixed header into the wraparound screen.
for name in ['HU_OpeningRoofPanel','HU_RearRoofArch']:
    for v in bpy.data.objects[name].data.vertices:v.co.z+=.031*max(0,1-(v.co.y/.66)**2)
patch('HU_CurvedRoofFrontHeader',seq(28,-.665,.665),seq(10),lambda y,t:(profile(t,[(0,.665-.055*(y/.80)**2),(1,.60)]),y,1.64*(1-t)+(1.66+.055*(1-(y/.66)**2))*t),TEAL,orient=(0,0,1))
for o in S.objects:
    if o.animation_data:
        for f in o.animation_data.drivers:f.driver.expression=f.driver.expression.replace(' + 0.0','')+' + 0.0'
    o.update_tag()
S.frame_set(151);S.frame_set(1);bpy.context.view_layer.update();S.name='Hurricane_V2_Assembly';S['asset']='Hurricane V2 surfacing refinement'
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Hurricane_V2_Assembly.blend'),compress=True);print('HURRICANE_V2_WHEEL_POCKETS_AND_SURFACES')
