import bpy
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Condor'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
# Close exposed ends of tubular structural curves seen from the rear.
for o in bpy.data.collections['Condor_Vehicle'].all_objects:
 if o.type=='CURVE':o.data.use_fill_caps=True
# Regular triangular vocal grille; remove irregular inherited material fragments.
m=bpy.data.objects['BT_HocusPocus_OnePiece'];N=128;voiceidx=len(m.data.materials)-1
for f in m.data.polygons:
 if f.index>=13*N:continue
 row=f.index//N;i=f.index%N;k=min(i,N-1-i)
 if row not in [8,9]:
  f.material_index=0
  if 2<=row<=6 and k<8-(row-2):f.material_index=voiceidx if k%3!=2 else 0
bpy.context.scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(A/'Condor_V15_Assembly.blend'),compress=True);print('FINISH_V15_SAVED')
