"""User corrections: tucked wheel, clearance-dependent sequence, rigid seat/skids."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Condor';s=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
assert bpy.data.objects.get('Condor_Control') and bpy.data.objects.get('BradTurner_Rig')
s.frame_set(1);bpy.context.view_layer.update()
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
CURRENT=bpy.data.collections['Condor_Vehicle'];root=bpy.data.objects['Condor_Control'];PARENT=root;R=bpy.data.objects['BradTurner_Rig'];black=bpy.data.materials['Condor_Charcoal'];chrome=bpy.data.materials['Condor_WheelAlloy']
# Same persistent wheel moved deeper beneath the tail; fixed roof-level arm hinge.
rear=bpy.data.objects['Condor_RearWheelPivot'];spin=bpy.data.objects['Condor_TailRotorSpin'];oldspin=spin.matrix_world.copy()
rear.location=(-1.45,0,.82);bpy.context.view_layer.update();oldspin.translation=Vector((-1.05,0,.355));spin.matrix_world=oldspin;bpy.context.view_layer.update()
root['rear_wheel_deploy']=0.;root.id_properties_ui('rear_wheel_deploy').update(min=0,max=1)
drive(root,'["rear_wheel_deploy"]',None,'min(1,max(0,(t-0.36)/0.64))',[('t',root,'transform')])
drive(rear,'rotation_euler',1,'2.2*w*w*(3-2*w)',[('w',root,'rear_wheel_deploy')])
for o in list(CURRENT.all_objects):
 if o.name.startswith(('Condor_ConnectedRearFork','Condor_FixedRearPivot','Condor_RearPivotChassisBracket','Condor_RearWheelWell_Cutter')):bpy.data.objects.remove(o,do_unlink=True)
bpy.context.view_layer.update()
for side in [-1,1]:
 tube('Condor_ConnectedRearFork_'+str(side),(-1.45,side*.11,.82),(-1.05,side*.11,.355),.030,black,root=rear)
 tube('Condor_FixedRearPivot_'+str(side),(-1.45,side*.075,.82),(-1.45,side*.13,.82),.043,chrome)
 tube('Condor_RearPivotChassisBracket_'+str(side),(-1.33,side*.075,.73),(-1.45,side*.11,.82),.035,black)
cut=tube('Condor_RearWheelWell_Cutter',(-1.05,-.09,.355),(-1.05,.09,.355),.377,black,N=80);cut.hide_render=True;cut.hide_set(True);cut.display_type='WIRE'
body=bpy.data.objects['Condor_RearMonobloc'];mod=next(m for m in body.modifiers if m.type=='BOOLEAN');mod.object=cut
# Rebuild compact skis below seat: no lateral spread, no independent transform.
block=bpy.data.objects['Condor_SeatSkidBlock']
for o in list(CURRENT.all_objects):
 if o.name.startswith(('Condor_SkidCarriage','Condor_LandingSkid','Condor_SkidStrut')):bpy.data.objects.remove(o,do_unlink=True)
for side in [-1,1]:
 path('Condor_LandingSkid_'+str(side),[(.145,side*.145,.205),(.10,side*.145,.16),(.055,side*.145,.15),(-.43,side*.145,.15),(-.49,side*.145,.18)],.025,black,block)
 for x in [-.34,.015]:tube('Condor_SeatSkidFixedStrut',(x,side*.145,.16),(x,side*.145,.39),.022,black,root=block)
# Reserve the moving seat cassette's volume by concentrating the fixed engine forward.
for o in CURRENT.all_objects:
 if o.type=='MESH' and o.name.startswith(('Condor_Engine','Condor_CoolingFin')):
  for v in o.data.vertices:v.co.x=.25+(v.co.x-.05)*.45
# Slim posterior helmet, bound against actual anatomical skull to avoid cutting it.
mask=bpy.data.objects['BT_HocusPocus_OnePiece'];head=bpy.data.objects['BT_Head_AnatomicalSurface'];tree=BVHTree.FromPolygons([v.co for v in head.data.vertices],[list(f.vertices) for f in head.data.polygons]);before=[];after=[]
for v in mask.data.vertices:
 p=v.co
 if p.x<-.03 and p.z>1.57:
  before.append(p.x);nx=-.03+(p.x+.03)*.73;hit=tree.ray_cast(Vector((-.4,p.y,p.z)),Vector((1,0,0)),.5)
  if hit[0]:nx=min(nx,hit[0].x-.006)
  p.x=nx;after.append(p.x)
# Two molded black vertical ribs per side, integrated into the SAME shell topology.
N=128;columns={24,25,34,35,92,93,102,103};ribcols={24,25,26,34,35,36,92,93,94,102,103,104}
for v in mask.data.vertices:
 if v.index<14*N and 4<=v.index//N<=10 and v.index%N in ribcols:v.co.y+=.0045 if v.co.y>0 else -.0045
for f in mask.data.polygons:
 if f.index<13*N and 4<=f.index//N<=9 and f.index%N in columns:f.material_index=1
mask.data.update();mask['rear_and_ribs_note']='Posterior depth reduced 27% where skull clearance allows. Two integrated raised vertical black ribs per side. User 2026-11-12.'
root['wheel_sequence_note']='Rear wheel tucked at X=-1.05m; starts rotating only after transform0.36, when mast has risen45deg. Smooth rotation126deg after clearance. Estimated kinematics supersede simultaneous wheel start.'
root['seat_skid_note']='Two short parallel skids directly below seat cassette, fixed to same translating block. No lateral deployment or independent skid animation.'
for o in CURRENT.all_objects:
 if o.type=='CURVE':o.data.use_fill_caps=True
R['mask_on']=True;R['driving_pose']=1.;R.update_tag();s.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Condor_V16_Assembly.blend'),compress=True)
(A/'changes_v16.json').write_text(json.dumps({'posterior_min_x_before':min(before),'posterior_min_x_after':min(after),'wheel_rest_center':list(spin.matrix_world.translation),'seat_skid_rigid':True},indent=2))
print('V16_CORRECTIONS_SAVED',list(spin.matrix_world.translation))
