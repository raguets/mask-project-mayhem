import bpy
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Condor'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
CURRENT=bpy.data.collections['Condor_Vehicle'];PARENT=bpy.data.objects['Condor_Control']
cut=box('Condor_RearWheelEscape_Cutter',(-1.28,0,.27),(.70,.242,.74),bpy.data.materials['Condor_Charcoal'],.016);cut.hide_render=True;cut.hide_set(True);cut.display_type='WIRE'
body=bpy.data.objects['Condor_RearMonobloc'];m=body.modifiers.new('WheelSweptEscapeChannel','BOOLEAN');m.operation='DIFFERENCE';m.object=cut
body['wheel_channel_note']='Internal swept escape below cowl, preserving upper skin; rest wheel recessed under chassis and rear swing after mast clearance.'
bpy.context.scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(A/'Condor_V19_Assembly.blend'),compress=True);print('V19_SWEPT_ESCAPE_SAVED')
