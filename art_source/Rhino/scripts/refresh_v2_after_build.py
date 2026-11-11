import bpy,gc,types,json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Rhino';S=bpy.context.scene;R=bpy.data.objects['Rhino_Control']
# End the current incomplete audit before changing driver evaluation state.
for fn in gc.get_objects():
 if isinstance(fn,types.FunctionType) and fn.__name__=='step' and 'pairs' in fn.__globals__ and 'report' in fn.__globals__ and bpy.app.timers.is_registered(fn):
  namespace=fn.__globals__;bpy.app.timers.unregister(fn);namespace['restore']();(A/'validation_v2_interrupted_driver_refresh.json').write_text(json.dumps({'reason':'New drivers were still invalid after construction; incomplete audit stopped before refresh.','frames_evaluated':len(namespace['report']['frames'])}))
for ob in S.objects:
 if ob.animation_data:
  for f in ob.animation_data.drivers:
   if not f.driver.is_valid:f.driver.expression=f.driver.expression+' + 0.0';f.mute=False;ob.update_tag()
states=[]
for frame in [1,151,241]:
 S.frame_set(frame);R.update_tag();bpy.context.view_layer.update();states.append({'frame':frame,'parts':[{ 'name':name,'location':list(bpy.data.objects[name].location),'rotation':list(bpy.data.objects[name].rotation_euler),'valid':all(f.driver.is_valid for f in bpy.data.objects[name].animation_data.drivers)} for name in ['RH_RearCabinetSlide','RH_MissileLauncherLift','RH_RadarRotation']]})
assert all(part['valid'] for state in states for part in state['parts']),states
assert states[1]['parts'][0]['location'][0]<-.79 and states[1]['parts'][1]['location'][2]>3.63
(A/'driver_states_v2.json').write_text(json.dumps(states,indent=2));S.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Rhino_V2.blend'),compress=True);print('RHINO_V2_DRIVERS_VALID_THREE_STATES')
