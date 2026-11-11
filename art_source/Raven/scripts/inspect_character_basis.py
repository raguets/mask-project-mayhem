import bpy,json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
with bpy.data.libraries.load(str(P/'art_source/Hondo_MacLean/HondoMacLean_V1.blend'),link=False) as (src,dst):
    print('SOURCE_COLLECTIONS',src.collections)
    dst.collections=['HMC_Character']
C=dst.collections[0];bpy.context.scene.collection.children.link(C);C.name='CB_Character'
R=next(o for o in C.all_objects if o.type=='ARMATURE')
report={'objects':[{'name':o.name,'type':o.type,'hidden':o.hide_render,'materials':[m.name for m in o.data.materials if m] if o.type=='MESH' else []} for o in C.all_objects],'rig':R.name,'properties':dict(R.items()),'drivers':[(f.data_path,[(v.name,[(str(t.id),t.data_path) for t in v.targets]) for v in f.driver.variables]) for f in R.animation_data.drivers if not f.data_path.startswith('pose.bones[')],'bones':{b.name:{'head':list(b.head_local),'tail':list(b.tail_local)} for b in R.data.bones}}
(P/'art_source/Raven/calhoun_basis_inventory.json').write_text(json.dumps(report,indent=2,default=str))
bpy.ops.wm.save_as_mainfile(filepath=str(P/'art_source/Raven/Raven_V1_with_character_basis.blend'),compress=True)
print('CALHOUN_BASIS_INSPECTED',len(C.all_objects))
