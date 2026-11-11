from pathlib import Path
A=Path('G:/DEV/mask-project-mayhem/art_source/Raven')
exec(compile((A/'scripts/verify_exports_v5.py').read_text(encoding='utf-8').replace('V5','V11').replace('_v5','_v11'),'<verify-exports-v11>','exec'))
import bpy,json,math
path=A/'standalone_validation_v11.json';report=json.loads(path.read_text());checks={};states=[]
try:
    bpy.ops.wm.open_mainfile(filepath=str(A/'Raven_V11_Vehicle.blend'));S=bpy.context.scene
    clip=bpy.data.objects['RV_CompleteFront_LongitudinalPivot']
    def belongs(ob,parent):
        while ob:
            if ob==parent:return True
            ob=ob.parent
        return False
    checks['whole_front_includes_body_lamps_and_wheels']=all(belongs(bpy.data.objects[name],clip) for name in ['RV_FrontFender_L','RV_FrontFender_R','RV_NoseFascia','RV_FrontDrivingLamp_1','RV_FrontWheelFold_L','RV_FrontWheelFold_R'])
    hood_animation=bpy.data.objects['RV_HoodSkin_FixedInFrontUnit'].animation_data
    checks['no_separate_hood_cam_driver']=not hood_animation or not hood_animation.drivers
    for frame in [1,151]:
        S.frame_set(frame);bpy.context.view_layer.update();entry={'frame':frame,'front_roll_degrees':math.degrees(clip.rotation_euler.x),'guns':[]}
        for axle in ['Front','Rear']:
            for sg,side in [(1,'L'),(-1,'R')]:
                hinge=bpy.data.objects['RV_'+axle+'RimGunHinge_'+side]
                entry['guns'].append({'wheel':axle+side,'angle_degrees':math.degrees(hinge.rotation_euler.z),'normal_location':hinge.location.y})
        states.append(entry)
    checks['front_roll_180_degrees']=abs(states[1]['front_roll_degrees']-180)<1e-4
    checks['all_four_guns_recessed_angle_zero_at_rest']=all(abs(v['angle_degrees'])<1e-4 for v in states[0]['guns'])
    checks['all_four_guns_45_degrees_deployed']=all(abs(abs(v['angle_degrees'])-45)<1e-4 for v in states[1]['guns'])
    checks['slight_gun_normal_travel_18mm']=all(abs(abs(b['normal_location']-a['normal_location'])-.018)<1e-5 for a,b in zip(states[0]['guns'],states[1]['guns']))
    report['user_mechanism_checks']=checks;report['mechanism_states']=states
    report['passed']=report['passed'] and all(checks.values());path.write_text(json.dumps(report,indent=2))
finally:bpy.ops.wm.open_mainfile(filepath=str(A/'Raven_V11_Assembly.blend'))
assert report['passed'],report
print('USER_MECHANISM_CORRECTIONS_REOPENED_AND_VERIFIED')
