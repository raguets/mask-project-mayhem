import bpy,json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');path=P/'art_source/AnatomyBase/bundle/human_base_meshes_bundle.blend'
with bpy.data.libraries.load(str(path),link=False) as (src,dst):
    dst.objects=[n for n in src.objects if n in ['realistic_head_animation','realistic_head_sculpting','realistic_hand','Hand  - Realistic'] or n.startswith('GEO-head_animation_realistic')]
report=[]
for ob in dst.objects:
    if not ob:continue
    if not ob.users_collection:bpy.context.scene.collection.objects.link(ob)
    ob.hide_render=True;ob.hide_set(True)
    report.append({'name':ob.name,'type':ob.type,'location':list(ob.location),'rotation':list(ob.rotation_euler),'scale':list(ob.scale),
        'bbox':[list(p) for p in ob.bound_box],'vertices':len(ob.data.vertices) if ob.type=='MESH' else None,
        'children':[c.name for c in ob.children], 'instance_collection':ob.instance_collection.name if ob.instance_collection else None,
        'vertex_groups':[g.name for g in ob.vertex_groups], 'modifiers':[(m.name,m.type) for m in ob.modifiers],
        'asset':{'author':ob.asset_data.author,'license':ob.asset_data.license,'description':ob.asset_data.description} if ob.asset_data else None})
(P/'docs/qa/anatomy_objects.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
