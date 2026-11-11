"""Calibrate wheelbase to the 1985 Camaro datum, without flattening wheels.

101 inches = 2.5654 m, GM Heritage 1985 Camaro information kit. This is a real-car
datum, NOT a verified measurement of the cartoon Thunderhawk. Other dimensions
remain design estimates. The smooth monotone longitudinal map is rigid around
both wheel/arch regions and commutes with the X-axis door rotations and Z lifts.
"""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
S=bpy.context.scene;ROOT=Path('G:/DEV/mask-project-mayhem/art_source/Thunderhawk')
save=globals().get('calibration_save',True)
def tire_center(name):
    ob=bpy.data.objects[name];return sum((ob.matrix_world@v.co for v in ob.data.vertices),Vector())/len(ob.data.vertices)
S.frame_set(1)
actual_before=tire_center('THK_Tire_FL').x-tire_center('THK_Tire_RL').x
if abs(actual_before-2.5654)>1e-5:
    assert abs(actual_before-2.82)<1e-4,actual_before
    S.frame_set(1)
    if save and not (ROOT/'Thunderhawk_V9_before_dimension_calibration.blend').exists():
        bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Thunderhawk_V9_before_dimension_calibration.blend'),copy=True,compress=True)
    rear_delta=.1746;front_delta=-.08
    def blend(x,a,b,da,db):
        t=max(0,min(1,(x-a)/(b-a)));t=t*t*(3-2*t);return x+da+(db-da)*t
    def warp(x):
        if x<=-1.81:return blend(x,-2.43,-1.81,0,rear_delta)
        if x<=-1.03:return x+rear_delta
        if x<=1.01:return blend(x,-1.03,1.01,rear_delta,front_delta)
        if x<=1.79:return x+front_delta
        return blend(x,1.79,2.43,front_delta,0)
    obs=list(bpy.data.collections['THK9_Exterior'].objects)
    old_mw={o:o.matrix_world.copy() for o in obs};old_loc={o:o.location.copy() for o in obs}
    positions={o:[old_mw[o]@v.co for v in o.data.vertices] for o in obs if o.type=='MESH'}
    def depth(ob):return 0 if not ob.parent else 1+depth(ob.parent)
    for ob in sorted(obs,key=depth):
        mw=old_mw[ob].copy()
        if ob.name!='THK_Root':mw.translation.x=warp(mw.translation.x)
        ob.matrix_world=mw;bpy.context.view_layer.update()
    for ob,vv in positions.items():
        inverse=ob.matrix_world.inverted()
        for v,p in zip(ob.data.vertices,vv):
            p.x=warp(p.x);v.co=inverse@p
        ob.data.update()
    for ob in obs:
        if not ob.animation_data or not ob.animation_data.action:continue
        delta=ob.location.x-old_loc[ob].x;act=ob.animation_data.action
        curves=list(getattr(act,'fcurves',[]))
        for layer in getattr(act,'layers',[]):
            for strip in layer.strips:
                for bag in getattr(strip,'channelbags',[]):curves.extend(bag.fcurves)
        for fc in curves:
            if fc.data_path=='location' and fc.array_index==0:
                for k in fc.keyframe_points:k.co.y+=delta;k.handle_left.y+=delta;k.handle_right.y+=delta
    S['THK9_dimension_calibrated']=True
    S['THK9_wheelbase_datum_m']=2.5654
    S['THK9_dimension_source']='GM Heritage 1985 Camaro: wheelbase 101 inches; cartoon geometry not certified'
    S.frame_set(1);bpy.context.view_layer.update()
    wheelbase=bpy.data.objects['THK_WheelPivot_FL'].matrix_world.translation.x-bpy.data.objects['THK_WheelPivot_RL'].matrix_world.translation.x
    assert abs(wheelbase-2.5654)<1e-5,wheelbase
    actual_after=tire_center('THK_Tire_FL').x-tire_center('THK_Tire_RL').x
    assert abs(actual_after-2.5654)<1e-5,actual_after
    report={'wheelbase_before_m':actual_before,'wheelbase_after_m':actual_after,'pivot_wheelbase_m':wheelbase,'source_url':'https://news.chevrolet.com/content/dam/company/no_search/heritage-archive-docs/vehicle-information-kits/chevrolet/1985-Chevrolet-Camaro.pdf',
            'datum':'101 inches, real 1985 Camaro','cartoon_dimensions_validated':False,'method':'Smooth monotone X remap, rigid translation through wheel and arch regions; X animation offsets updated'}
    (ROOT/'dimensions_calibration_v9.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    if save:bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Thunderhawk_V9.blend'),compress=True)
    print('THK9_DIMENSION_CALIBRATION '+json.dumps(report))
else:print('THK9_DIMENSION_CALIBRATION_ALREADY_APPLIED')
