import bpy,json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Rhino';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
canonical=bpy.data.objects['RH_Hood'].data.materials[0];replaced=[]
for ob in S.objects:
 if ob.type not in ['MESH','CURVE','FONT']:continue
 for index,material in enumerate(ob.data.materials):
  if material and material.name=='Rhino_DeepBurgundy' and material!=canonical:ob.data.materials[index]=canonical;replaced.append(ob.name)
S['cabinet_finish_v2']='Rear wings, upper window frames and front jambs use the same actual burgundy shader as the hood, instead of an unused material left by the failed first initialization.'
(A/'material_finish_v2.json').write_text(json.dumps({'canonical_material':canonical.name,'corrected_objects':replaced},indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(A/'Rhino_V2.blend'),compress=True);print('RHINO_BURGUNDY_TRIM_CORRECTED',replaced)
