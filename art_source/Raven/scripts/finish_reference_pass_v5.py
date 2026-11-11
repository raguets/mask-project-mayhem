import bpy,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Raven';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
assert not (A/'Raven_V5_Assembly.blend').exists()
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(encoding='utf-8'),'<geometry>','exec'))
root=bpy.data.objects['Raven_Control'];R=bpy.data.objects['CalhounBurns_Rig'];S.frame_set(1);root['hover_height']=0.;R['in_vehicle']=0.;R['driving_pose']=0.;R.update_tag();bpy.context.view_layer.update()
cover=bpy.data.objects['RV_ReactorCover_VerticalSlide']
drive(cover,'location',2,'.845+.32*t',[('t',root,'transform')])
for name in ['RV_ReactorCover_RearSkirt','RV_ReactorCover_SideSkirt_-1','RV_ReactorCover_SideSkirt_1']:
    o=bpy.data.objects[name];center=sum(v.co.z for v in o.data.vertices)/len(o.data.vertices)
    for v in o.data.vertices:v.co.z=.72+(v.co.z-center)*(1.5 if 'Rear' in name else 1.65)
    o.data.update()
CURRENT=bpy.data.collections['RV_Body'];PARENT=None;GROUP='body'
box('RV_ReactorCover_FrontSkirt',(-1.913,0,.725),(.025,1.44,.20),bpy.data.materials['RV_Obsidian_Clearcoat'],.005,root=cover)
for sg in [-1,1]:
    tube('RV_ReactorSlideGuide_'+str(sg),(-2.15,sg*.65,.65),(-2.15,sg*.65,1.15),.013,bpy.data.materials['RV_Gunmetal'],N=24,root=root)
    # Guides are inferred hidden hardware; the short cover translates without rotation.
hair=bpy.data.objects['CB_ContinuousSweptHairCap'];m=hair.modifiers.new('HairSurfaceRelax','SMOOTH');m.factor=.5;m.iterations=3
CURRENT=bpy.data.collections['CB_Character'];PARENT=None;GROUP='calhoun'
dg=bpy.context.evaluated_depsgraph_get();ev=hair.evaluated_get(dg);me=ev.to_mesh();tree=BVHTree.FromPolygons([v.co for v in me.vertices],[list(f.vertices) for f in me.polygons]);ev.to_mesh_clear();mat=bpy.data.materials['CB_ChestnutHair']
def bind(o):
    group=o.vertex_groups.new(name='head');group.add(list(range(len(o.data.vertices))),1,'REPLACE');modifier=o.modifiers.new('CalhounHairSkin','ARMATURE');modifier.object=R;modifier.use_deform_preserve_volume=True;o.parent=R
    for prop in ['hide_render','hide_viewport']:drive(o,prop,None,'m',[('m',R,'mask_on')])
for j in range(70):
    y=-.094+.188*j/69;points=[]
    for x in seq(30,.095,-.082):
        hit=tree.ray_cast(Vector((x,y,1.95)),Vector((0,0,-1)),.3)
        if hit[0]:points.append(tuple(hit[0]+hit[1]*.0006))
    if len(points)<8:continue
    curve=path('CB_FineCombedHair_'+str(j),points,.00065,mat)
    dg=bpy.context.evaluated_depsgraph_get();data=bpy.data.meshes.new_from_object(curve.evaluated_get(dg),depsgraph=dg);o=bpy.data.objects.new(curve.name+'_Mesh',data);CURRENT.objects.link(o);bpy.data.objects.remove(curve,do_unlink=True);bind(o)
R['driving_pose']=1.;R['in_vehicle']=1.;R['mask_on']=False;R.update_tag();S.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Raven_V5_Assembly.blend'),compress=True)
print('RAVEN_V5_FINISHING_SAVED')
