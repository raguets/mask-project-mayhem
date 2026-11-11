import bpy,json
from pathlib import Path
from mathutils import Matrix
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Raven';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
assert not (A/'Raven_V6_Assembly.blend').exists()
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(encoding='utf-8'),'<geometry>','exec'))
root=bpy.data.objects['Raven_Control'];root['hover_height']=0.;S.frame_set(1);bpy.context.view_layer.update()
# Keep presentation translation on a separate node, avoiding a self-driven root.
root.driver_remove('location',2);root.location=(0,0,0)
CURRENT=bpy.data.collections['RV_Body'];PARENT=None;GROUP='presentation'
children=list(root.children);offset=empty('RV_PresentationOffset',parent=root)
drive(offset,'location',2,'h',[('h',root,'hover_height')])
for ob in children:
    matrix=ob.matrix_world.copy();ob.parent=offset;ob.matrix_parent_inverse=offset.matrix_world.inverted();ob.matrix_world=matrix
cover=bpy.data.objects['RV_ReactorCover_VerticalSlide']
for ob in cover.children:
    if ob.type!='MESH':continue
    for v in ob.data.vertices:v.co.x=-2.24+(v.co.x+2.24)*(.39/.33)
    ob.data.update()
for sg in [-1,1]:
    guide=bpy.data.objects['RV_ReactorSlideGuide_'+str(sg)]
    for v in guide.data.vertices:v.co.z=.65+(v.co.z-.65)*(.19/.50)
    guide.shape_key_add(name='Basis');key=guide.shape_key_add(name='TelescopicExtension')
    for v in key.data:v.co.z=.65+(v.co.z-.65)*(.51/.19)
    drive(key,'value',None,'t',[('t',root,'transform')])
# Prove the car and the occupied pilot receive exactly one presentation offset.
R=bpy.data.objects['CalhounBurns_Rig'];R['in_vehicle']=1.;R['driving_pose']=1.;R['mask_on']=False;R.update_tag();bpy.context.view_layer.update()
tests=[]
for h in [0.,.6]:
    root['hover_height']=h;root.update_tag();S.frame_set(1);bpy.context.view_layer.update()
    tests.append({'hover':h,'car_offset_z':offset.matrix_world.translation.z,'pilot_z':R.matrix_world.translation.z})
assert abs(tests[1]['car_offset_z']-tests[0]['car_offset_z']-.6)<1e-5,tests
assert abs(tests[1]['pilot_z']-tests[0]['pilot_z']-.6)<1e-5,tests
(A/'presentation_offset_v6.json').write_text(json.dumps({'passed':True,'measurements':tests},indent=2))
root['hover_height']=0.;S.frame_set(1);root.update_tag();R.update_tag();bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Raven_V6_Assembly.blend'),compress=True)
print('RAVEN_V6_PRESENTATION_OFFSET_VERIFIED')
