"""Correct defects seen in the anatomical-fit renders, keeping the same rig."""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
from math import pi,sqrt,cos,sin,exp
P=Path('G:/DEV/mask-project-mayhem');T=P/'art_source/Thunderhawk';s=bpy.context.scene;r=bpy.data.objects['MattTrakker_Rig'];char=bpy.data.collections['MT11_Character']
r['driving_pose']=0;r['mask_on']=False;r.location=(0,0,0);r.update_tag();s.frame_set(1);bpy.context.view_layer.update()
head=bpy.data.objects['MT_Head_AnatomicalSurface'];me=head.data
# The reference bust's lower shoulders must not protrude through a flight-suit collar.
for v in me.vertices:
    z=v.co.z
    if z<1.564:
        blend=max(0,min(1,(1.564-z)/.060));limit=.043+.004*(1-blend)
        y=v.co.y
        if abs(y)>limit:v.co.y=y*(1-blend)+math.copysign(limit,y)*blend
        x=v.co.x+.015
        if abs(x)>limit:v.co.x=(x*(1-blend)+math.copysign(limit,x)*blend)-.015
# Trim the lowest open bust rim inside the collar and remove its visible fringe.
verts=[tuple(v.co) for v in me.vertices];faces=[tuple(f.vertices) for f in me.polygons if all(me.vertices[i].co.z>1.493 for i in f.vertices)]
me.clear_geometry();me.from_pydata(verts,[],faces);me.update();head.vertex_groups.clear();gh=head.vertex_groups.new(name='head');gn=head.vertex_groups.new(name='neck')
for v in me.vertices:
    w=max(0,min(1,(v.co.z-1.535)/.065));w=w*w*(3-2*w)
    if w:gh.add([v.index],w,'REPLACE')
    if w<1:gn.add([v.index],1-w,'REPLACE')
# Smooth per-vertex tint replaces the visibly jagged polygon material boundary.
skin=bpy.data.materials['MT4_Skin'];me.materials.clear();me.materials.append(skin)
attr=me.color_attributes.get('MattSkinTint') or me.color_attributes.new(name='MattSkinTint',type='FLOAT_COLOR',domain='POINT')
for v in me.vertices:
    y=v.co.y;z=v.co.z;x=v.co.x
    w=.62*exp(-(abs(y)/.026)**8-((z-1.634)/.0072)**4) if x>.072 else 0
    base=(.57,.338,.228);lips=(.36,.17,.125)
    attr.data[v.index].color=tuple(a*(1-w)+b*w for a,b in zip(base,lips))+(1,)
ns=skin.node_tree.nodes;ls=skin.node_tree.links;vc=ns.get('MattSkinTint') or ns.new('ShaderNodeVertexColor');vc.name='MattSkinTint';vc.layer_name='MattSkinTint';ls.new(vc.outputs['Color'],next(n for n in ns if n.type=='BSDF_PRINCIPLED').inputs['Base Color'])

# Reposition the iris cap in front of the actual sclera surface, with a round pupil.
for sd in ['L','R']:
    sclera=bpy.data.objects['MT_Eyeball_'+sd];vv=[v.co for v in sclera.data.vertices]
    cy=(min(v.y for v in vv)+max(v.y for v in vv))/2;cz=(min(v.z for v in vv)+max(v.z for v in vv))/2;front=max(v.x for v in vv)
    ob=bpy.data.objects['MT_Iris_'+sd];verts=[];faces=[];N=96;Z=25;rad=.0057
    for j in range(Z):
        rho=rad*j/(Z-1)
        for i in range(N):
            a=2*pi*i/N;verts.append((front+.00035-.0014*(rho/rad)**2,cy+rho*cos(a),cz+rho*sin(a)))
    for j in range(Z-1):
        for i in range(N):faces.append((j*N+i,(j+1)*N+i,(j+1)*N+(i+1)%N,j*N+(i+1)%N))
    me=ob.data;me.clear_geometry();me.from_pydata(verts,[],faces);me.update();ob.vertex_groups.clear();ob.vertex_groups.new(name='head').add(list(range(len(verts))),1,'REPLACE')
    me.materials.clear();me.materials.append(bpy.data.materials['MT4_IrisFibers']);me.materials.append(bpy.data.materials['MT4_Pupil'])
    color=me.color_attributes.get('IrisColor') or me.color_attributes.new(name='IrisColor',type='FLOAT_COLOR',domain='POINT')
    for v in me.vertices:
        y=v.co.y-cy;z=v.co.z-cz;rho=sqrt(y*y+z*z)/rad;a=math.atan2(z,y);f=(.55+.45*sin(a*73+rho*8))*(.40+.60*min(1,(1-rho)*7))
        color.data[v.index].color=(.045*f,.16*f,.19*f,1)
    for f in me.polygons:
        j=f.index//N;f.material_index=int((j+.5)/(Z-1)*rad<.0021);f.use_smooth=True
    bs=next(n for n in bpy.data.materials['MT4_IrisFibers'].node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Roughness'].default_value=.13;bs.inputs['Coat Weight'].default_value=.35

# Restore a stable rest-space patch from the preserved character, then make it thin.
before_objects=set(bpy.data.objects)
with bpy.data.libraries.load(str(P/'art_source/Matt_Trakker/MattTrakker_V3.blend'),link=False) as (src,dst):
    dst.objects=['MT_KneePatch_L','MT_KneePatch_R']
patches={sd:ob.data for sd,ob in zip(['L','R'],dst.objects)}
for sd,sg in [('L',1),('R',-1)]:
    ob=bpy.data.objects['MT_KneePatch_'+sd];source=patches[sd]
    vv=[(.077+(v.co.x-.076)*.2-.007*((v.co.y-sg*.11)/.044)**2,v.co.y,v.co.z) for v in source.vertices];ff=[tuple(f.vertices) for f in source.polygons]
    ob.data.clear_geometry();ob.data.from_pydata(vv,[],ff);ob.data.update();ob.vertex_groups.clear();ob.vertex_groups.new(name='shin.'+sd).add(list(range(len(vv))),1,'REPLACE')
    for m in list(ob.modifiers):ob.modifiers.remove(m)
    mod=ob.modifiers.new('ClothPatchRoundedEdges','BEVEL');mod.width=.002;mod.segments=3
    mod=ob.modifiers.new('SameMattKnee','ARMATURE');mod.object=r
for ob in list(bpy.data.objects):
    if ob not in before_objects:bpy.data.objects.remove(ob,do_unlink=True)
# The fixed plate bracket passes below, then behind the translating fascia.
ob=bpy.data.objects['THK_RearPlate_CentralMount']
for v in ob.data.vertices:
    v.co.z=.280+(v.co.z-.428)*(.030/.045)
co=bpy.data.collections['THK11_Interior'];old=bpy.data.objects.get('THK_RearPlate_VerticalStand')
if old:bpy.data.objects.remove(old,do_unlink=True)
vv=[(-2.443+sx*.004,y*.035,.356+sz*.077) for sx,y,sz in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
me=bpy.data.meshes.new('THK_RearPlate_VerticalStand_Editable');me.from_pydata(vv,[],[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]);me.materials.append(bpy.data.materials['THK13_PlateBacking']);ob=bpy.data.objects.new('THK_RearPlate_VerticalStand',me);co.objects.link(ob);ob.parent=bpy.data.objects['THK_Root']
r['driving_pose']=1;r['mask_on']=False;r.location=(0,.4,0);r.update_tag();s.frame_set(97);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(T/'Thunderhawk_V13.blend'),compress=True)
print('V13_EYES_LIP_TINT_NECK_PATCHES_AND_PLATE_MOUNT_CORRECTED')
