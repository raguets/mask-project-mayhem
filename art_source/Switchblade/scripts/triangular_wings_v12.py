import bpy
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Switchblade'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
root=bpy.data.objects['Switchblade_Control'];bpy.context.scene.frame_set(121);root.update_tag();bpy.context.view_layer.update()
def taper(p):
 t=max(0,min(1,(abs(p.y)-.71)/(3.84-.71)));oldrear=-.96+.12*t;oldfront=.17-.50*t;u=(p.x-oldrear)/(oldfront-oldrear);p.x=-.96+(.17-.74*t+.96)*u
for side in [-1,1]:
 for o in bpy.data.objects['SB_WingSweep_'+str(side)].children:
  if o.type=='MESH':
   for v in o.data.vertices:taper(v.co)
   o.data.update()
  elif o.type=='CURVE':
   for sp in o.data.splines:
    for p in sp.points:taper(p.co)
root['wing_planform']='User correction V12: trailing edge perpendicular to longitudinal fuselage (constant X); swept leading edge; chord1.13m at root to0.39m at outer tip, estimated scale.'
root.update_tag();bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Switchblade_V12_Assembly.blend'),compress=True)
print('TRIANGULAR_PLANFORM_V12_SAVED')
