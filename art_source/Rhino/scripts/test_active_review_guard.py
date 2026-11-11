import bpy,json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');active=dict(bpy.app.driver_namespace['_mask_asset_review_active']);before=(bpy.context.scene.frame_current,bpy.context.scene.camera.matrix_world.copy());out={}
tests=[('render_review_queue.py',{'RENDER_JOB':{'rig':'Rhino_Control','output_dir':str(P/'docs/qa/should_not_be_created_duplicate_review'),'rig_properties':[],'views':[]}}),('export_components.py',{'EXPORT_JOB':{'source_blend':str(P/'art_source/Rhino/Rhino_V2.blend'),'manifest':str(P/'docs/qa/should_not_be_created_duplicate_export.json'),'components':[]}})]
for filename,namespace in tests:
 try:exec(compile((P/'art_source/shared_tools'/filename).read_text(encoding='utf-8'),filename,'exec'),namespace)
 except AssertionError as error:out[filename]={'blocked_while_review_active':True,'reason':str(error)}
 else:raise AssertionError('Overlapping operation was not blocked: '+filename)
assert active==bpy.app.driver_namespace['_mask_asset_review_active'];assert before[0]==bpy.context.scene.frame_current;assert before[1]==bpy.context.scene.camera.matrix_world
assert not (P/'docs/qa/should_not_be_created_duplicate_review').exists();assert not (P/'docs/qa/should_not_be_created_duplicate_export.json').exists()
(P/'docs/qa/rhino_active_review_guard.json').write_text(json.dumps(out,indent=2));print('ACTIVE_REVIEW_REJECTS_OVERLAP_BEFORE_SCENE_OR_FILESYSTEM_MUTATION')
