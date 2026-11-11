import bpy,json,datetime
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Raven';A.mkdir(parents=True,exist_ok=True)
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
assert not (A/'Raven_V1_Assembly.blend').exists(),'Preserve previous version'
previous={'file':bpy.data.filepath,'objects':len(bpy.context.scene.objects)}
backup=A/('Session_before_Raven_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.blend')
bpy.ops.wm.save_as_mainfile(filepath=str(backup),copy=True,compress=True)
for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
for c in list(bpy.data.collections):bpy.data.collections.remove(c)
S=bpy.context.scene;S.name='Raven_V1_ReferenceStudy';S.unit_settings.system='METRIC';S.unit_settings.scale_length=1
(A/'previous_session.json').write_text(json.dumps({'previous':previous,'backup':str(backup)},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Raven_prepared_v1.blend'),compress=True)
print('RAVEN_PREPARED')
