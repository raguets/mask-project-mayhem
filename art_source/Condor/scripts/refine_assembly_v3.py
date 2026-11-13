import bpy,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Condor'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
root=bpy.data.objects['Condor_Control'];R=bpy.data.objects['BradTurner_Rig'];CURRENT=bpy.data.collections['Condor_Vehicle'];PARENT=root
for side in [-1,1]:
 h=bpy.data.objects['Condor_BladeHinge_'+str(side)];h.location.y=side*.30
 h.animation_data.drivers[0].driver.expression=str(-side)+'*1.570796*(1-max(0,(t-0.72)/0.28))'
bpy.data.objects['Condor_RotorSupport'].animation_data.drivers[0].driver.expression='1.570796*min(1,t/0.72)'
green=bpy.data.materials['Condor_LimePaint'];green.diffuse_color=(.065,.44,.002,1);next(n for n in green.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'].default_value=green.diffuse_color
for name,col in [('BT_YellowFlightFabric',(.57,.29,.006,1)),('BT_HocusPocusYellow',(.70,.37,.006,1))]:
 m=bpy.data.materials[name];m.diffuse_color=col;next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'].default_value=col
bpy.context.scene.view_settings.look='AgX - Medium High Contrast';bpy.context.scene.view_settings.exposure=-.5
suit=bpy.data.objects['BT_ContinuousFlightSuit'];red=bpy.data.materials['BT_BordeauxLeather'];black=bpy.data.materials['BT_BlackLeather'];suit.data.materials.append(red);ri=len(suit.data.materials)-1;suit.data.materials.append(black);bi=len(suit.data.materials)-1
for f in suit.data.polygons:
 p=f.center
 if abs(p.y)>.20 and .94<p.z<1.16:f.material_index=ri
 if p.z<.45:f.material_index=bi
# Rebuild fitted scalp from anatomical skull polygons; remove inherited conical cap.
CURRENT=bpy.data.collections['BT_Character'];PARENT=None
for o in list(CURRENT.all_objects):
 if any(k in o.name for k in ['Hair','FineCombed']):bpy.data.objects.remove(o,do_unlink=True)
head=bpy.data.objects['BT_Head_AnatomicalSurface'];head.data.update();vv=[];ff=[];mapping={}
for face in head.data.polygons:
 p=face.center
 if not(p.z>1.744+.006*max(0,p.x/.12) or (p.x<-.035 and p.z>1.68)):continue
 ids=[]
 for idx in face.vertices:
  if idx not in mapping:
   v=head.data.vertices[idx];q=v.co+v.normal*.007
   mapping[idx]=len(vv);vv.append(tuple(q))
  ids.append(mapping[idx])
 ff.append(ids)
hair=mesh('BT_FittedSweptHair',vv,ff,bpy.data.materials['BT_DarkBrownHair'],smooth=True);hair.parent=R;hair.vertex_groups.new(name='head').add(list(range(len(vv))),1,'REPLACE');hair.modifiers.new('EditableSkin','ARMATURE').object=R
for key in ['hide_render','hide_viewport']:drive(hair,key,None,'m',[('m',R,'mask_on')])
for o in CURRENT.all_objects:
 if 'Sunglass' in o.name and o.type=='MESH':
  for v in o.data.vertices:v.co.x-=.012;v.co.z-=.010
visor=bpy.data.objects['BT_Hocus_Goggles']
for v in visor.data.vertices:v.co.z=1.725+(v.co.z-1.725)*1.50
# Keep wheel persistent and expose independent rotor rotation.
CURRENT=bpy.data.collections['Condor_Vehicle'];PARENT=None;rear=bpy.data.objects['Condor_RearWheelPivot'];spin=empty('Condor_TailRotorSpin',(-.99,0,.355),rear)
for o in list(CURRENT.all_objects):
 if any(o.name.startswith(p) for p in ['Condor_Rear_PersistentTire','Condor_Rear_Rim','Condor_Rear_ThreeSpoke','Condor_Rear_Hub','Condor_Rear_Tread']):
  mw=o.matrix_world.copy();o.parent=spin;o.matrix_world=mw
drive(spin,'rotation_euler',1,'a*t',[('a',root,'rotor_angle'),('t',root,'transform')])
# All vehicle geometry lives in one clearly isolated collection (fix studio/vehicle alias bug).
vehicle=CURRENT
for o in list(bpy.context.scene.objects):
 if o.name.startswith('Condor_') and o.type not in ['CAMERA','LIGHT'] and o.name!='Condor_ReviewCamera':
  for co in list(o.users_collection):
   if co!=vehicle:co.objects.unlink(o)
  if o.name not in vehicle.objects:vehicle.objects.link(o)
root['mechanism_note']='Major mechanisms start together. Mast rises during first 72%; blades unfold after mast clearance, per supplied fiche. Estimated timing.'
R['mask_on']=True;R['driving_pose']=1.;R['in_vehicle']=1.;R.update_tag();bpy.context.scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Condor_V3_Assembly.blend'),compress=True)
print('V3_CORRECTED',[(c.name,len(c.all_objects)) for c in bpy.data.collections if len(c.all_objects)])
