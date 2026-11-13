import bpy
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Switchblade'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
root=bpy.data.objects['Switchblade_Control']
removed=[]
for o in list(bpy.data.objects):
 if o.name.startswith('SB_WingRootBearing') or o.name.startswith('SB_MastShoulderFin'):
  removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
# Low main-rotor installation; no tall exposed tower over the lowered glazing.
mast=bpy.data.objects['SB_MainRotorMast'];drive(mast,'location',2,'2.34-0.09*t',[('t',root,'transform')])
root['concealed_hardware']='User correction 2026-11-13: external spherical wing hinge covers and silver roof appendages removed; low rotor mast retained only as functional mount.'
root.update_tag();bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Switchblade_V8_Assembly.blend'),compress=True)
print('HARDWARE_CONCEALED',removed)
