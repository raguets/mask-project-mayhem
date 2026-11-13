import bpy
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Switchblade'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
root=bpy.data.objects['Switchblade_Control'];bpy.context.scene.frame_set(1);root.update_tag();bpy.context.view_layer.update()
def widen(p):
 if p.x<.15:p.y*=.65/.51
 elif p.x<.80:p.y*=.61/.59
for name in ['SB_MagentaFacetedGlazing','SB_CanopySill','SB_CanopySill.001','SB_CanopyRearFrame']:
 o=bpy.data.objects.get(name)
 if not o:continue
 if o.type=='MESH':
  for v in o.data.vertices:widen(v.co)
  o.data.update()
 elif o.type=='CURVE':
  for sp in o.data.splines:
   for p in sp.points:widen(p.co)
o=bpy.data.objects['SB_FittedRearCanopyJamb']
for v in o.data.vertices:v.co.y*=.65/.51
root['canopy_width_note']='User correction V13: rear sill width1.30m matches full cockpit width; narrows continuously toward nose. Dimensions estimated.'
root.update_tag();bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Switchblade_V13_Assembly.blend'),compress=True)
print('FULL_WIDTH_AFT_GLAZING_V13_SAVED')
