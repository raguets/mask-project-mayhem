import bpy,json
from pathlib import Path
S=bpy.context.scene;R=bpy.data.objects['Manta_Control'];S.frame_set(121);bpy.context.view_layer.update()
for n in ['Manta_Control','MA_UnderbodyWingPivot_1','MA_SlidingHood','MA_FrontWheelFlip_1','MA_RearLightSpoilerHinge','MA_TripleReactorTravel','VanessaWarfield_Rig']:
 o=bpy.data.objects[n];print(n,list(o.location),list(o.rotation_euler),list(o.matrix_world.translation), 'props',dict(o.items()))
 if o.animation_data:
  print('DRIVERS',[(d.data_path,d.array_index,d.driver.expression,d.driver.is_valid) for d in o.animation_data.drivers])
print('FEMALE_MESH_BOUNDS')
o=bpy.data.objects['VW_ContinuousBodyAndFace'];print([list(v) for v in o.bound_box]);print('weights missing',sum(not v.groups for v in o.data.vertices))
S.frame_set(1)
