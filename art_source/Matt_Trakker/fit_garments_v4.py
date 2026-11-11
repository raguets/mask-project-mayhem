"""Cloth silhouette and attached patches on the original weighted suit."""
import bpy,bmesh,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
T=Path('G:/DEV/mask-project-mayhem/art_source/Thunderhawk');s=bpy.context.scene;r=bpy.data.objects['MattTrakker_Rig'];char=bpy.data.collections['MT11_Character'];suit=bpy.data.objects['MT_ContinuousFlightSuit']
r['driving_pose']=0;r['mask_on']=False;r.location=(0,0,0);r.update_tag();s.frame_set(1);bpy.context.view_layer.update()
for v in suit.data.vertices:
    y=abs(v.co.y);z=v.co.z
    if y>.125 and z>1.43:
        blend=max(0,min(1,(y-.125)/.055));limit=1.483-.15*max(0,y-.10)
        if z>limit:v.co.z-=.86*blend*(z-limit)
        w=math.exp(-((y-.20)/.065)**2-((z-1.45)/.065)**2);v.co.x=-.006+(v.co.x+.006)*(1-.10*w)
suit.data.update();bpy.context.view_layer.update();ev=suit.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();vv=[Vector(v.co) for v in me.vertices];ff=[tuple(f.vertices) for f in me.polygons];ev.to_mesh_clear();tree=BVHTree.FromPolygons(vv,ff)
for ob in char.objects:
    if ob.type=='MESH' and ob.name.startswith(('MT_ArmBand_','MT_Cuff_')):
        for v in ob.data.vertices:
            point,normal,idx,dist=tree.find_nearest(v.co)
            if point is not None and dist<.03:v.co=point+normal*.0015
for sg,sd in [(1,'L'),(-1,'R')]:
    ob=bpy.data.objects['MT_KneePatch_'+sd];vv=[];ff=[];N=25;Z=29
    for j in range(Z):
        t=j/(Z-1);z=.496+.088*t
        for i in range(N):
            u=-1+2*i/(N-1);y=sg*.11+.041*u*(.88+.12*math.sin(math.pi*t));point,normal,idx,dist=tree.ray_cast(Vector((.30,y,z)),Vector((-1,0,0)),.5)
            if point is None:point=Vector((.075,y,z));normal=Vector((1,0,0))
            vv.append(tuple(point+normal*.0017))
    for j in range(Z-1):
        for i in range(N-1):ff.append((j*N+i,j*N+i+1,(j+1)*N+i+1,(j+1)*N+i))
    for m in list(ob.modifiers):ob.modifiers.remove(m)
    ob.data.clear_geometry();ob.data.from_pydata(vv,[],ff);ob.data.update();ob.vertex_groups.clear();th=ob.vertex_groups.new(name='thigh.'+sd);sh=ob.vertex_groups.new(name='shin.'+sd)
    for v in ob.data.vertices:
        w=max(0,min(1,(v.co.z-.507)/.065));th.add([v.index],w,'REPLACE');sh.add([v.index],1-w,'REPLACE')
    wall=ob.modifiers.new('ClothPatchThickness','SOLIDIFY');wall.thickness=.0012
    mod=ob.modifiers.new('SameMattKneeSkin','ARMATURE');mod.object=r;mod.use_deform_preserve_volume=True
    for f in ob.data.polygons:f.use_smooth=True
r['driving_pose']=1;r['mask_on']=False;r.location=(0,.4,0);r.update_tag();s.frame_set(97);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(T/'Thunderhawk_V13.blend'),compress=True)
print('MATT_V4_GARMENT_SILHOUETTE_AND_PATCHES_FITTED')
