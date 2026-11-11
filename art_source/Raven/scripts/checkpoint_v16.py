import bpy,json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Raven';S=bpy.context.scene
assert Path(bpy.data.filepath).name=='Raven_V16_Assembly.blend'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
root=bpy.data.objects['Raven_Control'];R=bpy.data.objects['CalhounBurns_Rig']
root['hover_height']=0.;root['disc_launch']=0.;R['driving_pose']=1.;R['in_vehicle']=1.;R['mask_on']=False;R.update_tag();S.frame_set(1);bpy.context.view_layer.update()
bpy.ops.object.select_all(action='DESELECT');root.select_set(True);bpy.context.view_layer.objects.active=root
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Raven_V16_Assembly.blend'),compress=True)
report={'source':bpy.data.filepath,'frame':S.frame_current,'hover':root['hover_height'],'active':bpy.context.view_layer.objects.active.name,'review_active':bool(bpy.app.driver_namespace.get('_mask_asset_review_active')),'saved':not bpy.data.is_dirty,'assembly_objects':len(S.objects)}
(A/'checkpoint_v16.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
