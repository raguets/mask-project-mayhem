import bpy
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Manta';S=bpy.context.scene
# The first pass exposed invalidated freshly-created drivers; force recompile with
# the existing target, and check the evaluated full deployment before rendering.
for o in bpy.data.objects:
 if not o.animation_data:continue
 for f in o.animation_data.drivers:
  if not f.driver.is_valid:
   print('RECOMPILE',o.name,[(v.name,[(str(t.id),t.data_path) for t in v.targets]) for v in f.driver.variables])
   e=f.driver.expression;f.driver.expression=e+'+0'
S.frame_set(121);bpy.context.view_layer.update()
for n in ['MA_SlidingHood','MA_UnderbodyWingPivot_1','MA_RearLightSpoilerHinge']:
 o=bpy.data.objects[n];print(n,list(o.location),list(o.rotation_euler),[(f.driver.expression,f.driver.is_valid) for f in o.animation_data.drivers])
S.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Manta_V2_Assembly.blend'),compress=True)
