import bpy,math,json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Manta';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
R=bpy.data.objects['VanessaWarfield_Rig'];body=bpy.data.objects['VW_ContinuousBodyAndFace'];R['driving_pose']=0.;R['in_vehicle']=0.;R.update_tag();bpy.context.view_layer.update()
for s,l in [(1,'L'),(-1,'R')]:
 for name in ['VW_RedBootFoot_'+l,'VW_BootSole_'+l]:
  ob=bpy.data.objects[name]
  for v in ob.data.vertices:v.co.y+=s*.045
  if 'RedBoot' in name:
   for v in ob.data.vertices:
    if v.co.x>.195:v.co.y=s*.15+(v.co.y-s*.15)*8;v.co.z+=.015
   m=ob.modifiers.new('RoundedBootUpper','SUBSURF');m.levels=1;m.render_levels=1
 # Retain underlying feet but fit their toe envelope beneath the footwear.
 for v in body.data.vertices:
  if v.co.z<.085 and v.co.y*s>0:
   v.co.y=s*.15+(v.co.y-s*.15)*.65;v.co.x=min(v.co.x,.181)
# An editable grip shape keeps continuous gloves and all fingers in both poses.
body.shape_key_add(name='Basis');key=body.shape_key_add(name='DrivingGrip')
for v,p in zip(body.data.vertices,key.data):
 c=v.co
 if abs(c.y)>.35 and c.z<.89:
  t=max(0,min(1,(.89-c.z)/.12));p.co.x+=.035*math.sin(t*math.pi);p.co.z+=.065*t*t
f=key.driver_add('value');var=f.driver.variables.new();var.name='p';var.targets[0].id=R;var.targets[0].data_path='["driving_pose"]';f.driver.expression='p'
R.animation_data.drivers.find('location',index=2).driver.expression='-.51*v'
# Exclude large studio cards from specular reflections to keep windshield readable.
for name in ['MA_Key','MA_Fill']:bpy.data.objects[name].visible_glossy=False
mat=bpy.data.objects['MA_Windshield'].data.materials[0];bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.32,.40,.48,1);bs.inputs['Transmission Weight'].default_value=.98;bs.inputs['Roughness'].default_value=.045
R['driving_pose']=1.;R['in_vehicle']=1.;R['mask_on']=False;R.update_tag();S.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Manta_V6_Assembly.blend'),compress=True)
print('V6_SAVED')
