import bpy,datetime,json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Hurricane';A.mkdir(parents=True,exist_ok=True)
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
assert not (A/'Hurricane_V1_Assembly.blend').exists()
previous={'file':bpy.data.filepath,'scene':bpy.context.scene.name,'objects':len(bpy.context.scene.objects),'frame':bpy.context.scene.frame_current}
backup=A/('Session_before_Hurricane_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(backup),copy=True,compress=True)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.shading.type='SOLID'
for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
for c in list(bpy.data.collections):bpy.data.collections.remove(c)
S=bpy.context.scene;S.name='Hurricane_V1_Surfacing';S.unit_settings.system='METRIC';S.unit_settings.scale_length=1;S.frame_set(1)
(A/'previous_session.json').write_text(json.dumps({'previous':previous,'backup':str(backup)},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Hurricane_prepared_v1.blend'),compress=True)
print('HURRICANE_PREPARED',previous)
