import bpy,json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
with bpy.data.libraries.load(str(P/'art_source/Calhoun_Burns/CalhounBurns_V2.blend'),link=False) as (src,dst):dst.collections=['CB_Character']
c=dst.collections[0];bpy.context.scene.collection.children.link(c);c.name='BT_Character'
r=next(o for o in c.all_objects if o.type=='ARMATURE');r.name='BradTurner_Rig'
report={'objects':[{'name':o.name,'type':o.type,'materials':[m.name for m in o.data.materials if m] if o.type=='MESH' else []} for o in c.all_objects],'bones':{b.name:{'head':list(b.head_local),'tail':list(b.tail_local)} for b in r.data.bones},'drivers':[{'bone':b.name,'rotation':list(b.rotation_euler)} for b in r.pose.bones], 'properties':dict(r.items())}
(P/'art_source/Condor/brad_basis_inventory.json').write_text(json.dumps(report,indent=2,default=str))
print('BRAD_BASIS',len(c.all_objects))
