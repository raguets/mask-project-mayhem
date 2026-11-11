import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Rhino';out={}
try:
 bpy.ops.wm.open_mainfile(filepath=str(A/'Rhino_V3_Vehicle.blend'));S=bpy.context.scene;R=bpy.data.objects['Rhino_Control'];assert not any(o.type=='ARMATURE' for o in S.objects);assert not bpy.data.objects.get('AlexSector_Rig');assert not bpy.data.objects.get('BruceSato_Rig')
 assert sum(o.name.endswith('_Tire') for o in S.objects)==10
 assert sum(o.name.startswith('RH_BullbarVertical_') for o in S.objects)==7
 states=[]
 for frame in [1,91,151,241]:
  S.frame_set(frame);R.update_tag();bpy.context.view_layer.update();states.append({'frame':frame,'bullbar_slide_x':bpy.data.objects['RH_BullbarSlide'].location.x,'cabinet_x':bpy.data.objects['RH_RearCabinetSlide'].location.x,'launcher_z':bpy.data.objects['RH_MissileLauncherLift'].location.z})
 assert abs(states[0]['bullbar_slide_x'])<.0001 and abs(states[2]['bullbar_slide_x']-.8)<.0001
 assert states[2]['cabinet_x']<-.79 and states[2]['launcher_z']>3.63
 invalid=[o.name+':'+f.data_path for o in S.objects if o.animation_data for f in o.animation_data.drivers if not f.driver.is_valid];assert not invalid,invalid
 out={'file':'Rhino_V3_Vehicle.blend','reopened':True,'no_character_dependency':True,'same_ten_tires':True,'vertical_bars':7,'closed_frame':bool(bpy.data.objects.get('RH_BullbarFrame')),'invalid_drivers':invalid,'states':states}
finally:
 bpy.ops.wm.open_mainfile(filepath=str(A/'Rhino_V3.blend'));(A/'standalone_vehicle_validation_v3.json').write_text(json.dumps(out,indent=2))
assert out.get('reopened');print('RHINO_V3_VEHICLE_REOPENED_AND_VERIFIED')
