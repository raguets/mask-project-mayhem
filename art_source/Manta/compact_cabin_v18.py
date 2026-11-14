import bpy,math,json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Manta';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((A/'rebuild_bindings_v15.py').read_text().split('# Front tires')[0],'<helpers>','exec'))
CURRENT=bpy.data.collections['Manta_Vehicle'];PARENT=None
glass=bpy.data.objects['MA_RearHatchGlass'].data.materials[0]
# Latest user fit criterion supersedes the initial 30% cabin approximation.
for sign in [-1,1]:
 o=bpy.data.objects['MA_DoorBody_'+str(sign)];pts=snap(o);lo=min(p.x for p in pts);hi=max(p.x for p in pts)
 for p in pts:p.x=-.70+(p.x-lo)*1.17/(hi-lo)
 localize(o,root,pts)
 o=bpy.data.objects['MA_DoorHandle_'+str(sign)];pts=snap(o);cx=sum(p.x for p in pts)/len(pts)
 for p in pts:p.x+=-.52-cx
 localize(o,root,pts)
for name in ['MA_TbarRoof','MA_RoofRearCross']:
 bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
newbox('MA_TbarRoof',(-.3875,0,1.233),(.705,.23,.055),purple,root)
newbox('MA_RoofRearCross',(-.72,0,1.226),(.085,1.29,.070),purple,root)
# Rebuild the three curved rear panes from the revised forward pillar position.
piece=(A/'rebuild_bindings_v15.py').read_text().split('# All THREE rear windows')[1].split("root['binding_note']")[0]
piece='# All THREE rear windows'+piece
piece=piece.replace('-1.08-1.04*t','-.76-1.36*t').replace('(-1.08,sign*.62,1.21)','(-.76,sign*.62,1.21)').replace('(-.995,sign*.84,.84)','(-.70,sign*.84,.84)')
exec(compile(piece,'<compact_rear_glazing>','exec'))
for o in bpy.data.objects:
 if o.type=='CURVE' and o.name.startswith('MA_QuarterWindowFrame'):o.data.bevel_depth=.036
 if o.type=='CURVE' and o.name.startswith('MA_Bpillar'):o.data.bevel_depth=.043
# The fixed rear parcel shelf closes the space behind the seats under the hatch.
CURRENT=bpy.data.collections['Manta_Interior'];seatmat=bpy.data.objects['MA_SeatBase_1'].data.materials[0]
newbox('MA_RearParcelShelf',(-1.08,0,.785),(.60,1.28,.045),seatmat,root)
root['cabin_latest_fit']='Latest correction: rear-side-window front pillar base X=-.70/top=-.76, just behind backrest rear X=-.66. Door/cabin length1.17m (25%) now shorter; front40% retained, rear35%. Latest seat-relative criterion supersedes initial approximate30% cabin.'
root['rear_glazing_note']='Three genuinely curved panes, slimmer height/width; front of quarter windows moved just behind seat backs, thicker curved frames, horizontal roof bar.'
for o in bpy.data.objects:
 if o.type=='MESH':o.data.update()
 o.update_tag()
R['driving_pose']=1.;R['in_vehicle']=1.;R['mask_on']=False;R.update_tag();S.frame_set(121);S.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Manta_V18_Assembly.blend'),compress=True)
print('V18_COMPACT_CABIN_SAVED')
