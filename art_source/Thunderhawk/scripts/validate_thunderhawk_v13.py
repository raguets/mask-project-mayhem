"""Reuse the 193-frame audit with the refined hands and new rear additions."""
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
source=(P/'art_source/Thunderhawk/scripts/validate_thunderhawk_v12.py').read_text()
source=source.replace('v12','v13').replace('V12','V13')
source=source.replace("('MT_GlovePalm_'+sd,'MT_GloveFinger_'+sd,'MT_GloveThumb_'+sd)","('MT_GloveSkin_'+sd,)")
source=source.replace("frames=iter(range(1,194))",'''plateobs=[o for o in bpy.data.collections['THK11_Interior'].objects if o.name.startswith('THK_RearPlate_')]
platetree,_=tree(plateobs)
shelftree,_=tree([bpy.data.objects['THK_ParcelShelf'],bpy.data.objects['THK_ParcelShelf_FrontLip']])
report['parcel_shelf_vertical_occlusion']=[shelftree.ray_cast(Vector((x,y,1.4)),Vector((0,0,-1)),1.0)[0] is not None for x in [-1.0,-1.3,-1.6] for y in [-.6,0,.6]]
report['anatomy']='Human interpretation authorized 2026-11-02. Generic CC0 anatomical head/hand adapted to the existing rig; no specific-person likeness.'
frames=iter(range(1,194))''')
source=source.replace("hp=len(helmet.overlap(collider));bp=len(body.overlap(collider))",'''hp=len(helmet.overlap(collider));bp=len(body.overlap(collider))
            panel,_=tree([bpy.data.objects['THK_RearPanel']])
            reactors,_=tree([o for o in s.objects if o.type=='MESH' and o.name.startswith('THK_Reactor')])
            pc=len(platetree.overlap(panel));pr=len(platetree.overlap(reactors));sm=len(shelftree.overlap(collider))''')
source=source.replace("'cover_translation_vertical':vertical}","'cover_translation_vertical':vertical,'plate_cover_pairs':pc,'plate_reactor_pairs':pr,'shelf_moving_pairs':sm}")
source=source.replace("report['reactor_order_ok']=", "report['rear_collision_frames']=[x for x in report['frames'] if x['plate_cover_pairs'] or x['plate_reactor_pairs'] or x['shelf_moving_pairs']]\n                report['reactor_order_ok']=")
exec(compile(source,'validate_thunderhawk_v13_expanded.py','exec'))
