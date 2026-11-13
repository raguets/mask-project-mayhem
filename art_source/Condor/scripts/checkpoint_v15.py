import bpy,json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Condor';s=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
root=bpy.data.objects['Condor_Control'];R=bpy.data.objects['BradTurner_Rig'];root['forward_flight']=0.;root['hover_height']=0.;root['rotor_angle']=0.;R['driving_pose']=1.;R['in_vehicle']=1.;R['mask_on']=True;R.update_tag();root.update_tag();s.frame_set(1);bpy.context.view_layer.update()
bpy.ops.object.select_all(action='DESELECT');root.select_set(True);bpy.context.view_layer.objects.active=root
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   sp=area.spaces.active;sp.overlay.show_extras=False;sp.shading.color_type='MATERIAL';sp.region_3d.view_location=(-.2,0,.85);sp.region_3d.view_distance=4.6
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Condor_V15_Assembly.blend'),compress=True)
proof={'source':bpy.data.filepath,'frame':s.frame_current,'review_complete':(A/'renders/v15_review/COMPLETE').exists(),'review_active':bool(bpy.app.driver_namespace.get('_mask_asset_review_active')),'independent_sources_passed':all(v['passed'] for v in json.loads((A/'standalone_validation_v15.json').read_text())),'essential_state_saved':True}
(A/'checkpoint_v15.json').write_text(json.dumps(proof,indent=2));print('CHECKPOINT',json.dumps(proof))
