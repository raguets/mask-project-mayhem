import bpy
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Raven';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
assert not (A/'Raven_V8_Assembly.blend').exists()
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(encoding='utf-8'),'<geometry>','exec'))
root=bpy.data.objects['Raven_Control'];R=bpy.data.objects['CalhounBurns_Rig'];root['hover_height']=0.;S.frame_set(1)
# The first seat position left the helmet touching the sloping rear hatch.
drive(R,'location',0,'.20*a',[('a',R,'in_vehicle')])
for ob in bpy.data.collections['RV_Interior'].objects:
    if any(key in ob.name for key in ['Seat','Headrest','Dashboard','Steering','Instrument','Pedal','Shift']):ob.location.x+=.18
R['asset_version']='Calhoun Burns first publication V1 (Raven V8 assembly)'
R['driving_pose']=1.;R['in_vehicle']=1.;R['mask_on']=False;R.update_tag();S.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Raven_V8_Assembly.blend'),compress=True)
print('RAVEN_V8_COCKPIT_FIT_SAVED')
