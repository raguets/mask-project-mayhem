import bpy
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Condor'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
o=bpy.data.objects['Condor_RearMonobloc']
for v in o.data.vertices:
 p=v.co;t=max(0,min(1,(p.x+1.82)/1.42));low=.60-.30*t
 if v.index%8 in [3,6]:p.z=low+.035
 elif v.index%8 in [4,5]:p.z=low
 p.y*=.73+.27*t
o.data.update();o['shape_note']='User 2026-11-12: lower edge slopes down toward seat base; aft section narrows in width and thickness.'
for ob in bpy.data.collections['Condor_Vehicle'].all_objects:
 if ob.name.startswith('Condor_RearBlockVent'):
  for v in ob.data.vertices:
   t=max(0,min(1,(v.co.x+1.82)/1.42));v.co.y*=.73+.27*t
 if ob.name.startswith('Condor_RearBlockStripe'):ob.hide_render=True;ob.hide_viewport=True
bpy.context.scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(A/'Condor_V6_Assembly.blend'),compress=True)
print('REAR_TAPER_V6_SAVED')
