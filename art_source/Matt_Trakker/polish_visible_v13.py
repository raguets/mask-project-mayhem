import bpy,bmesh,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path('G:/DEV/mask-project-mayhem');T=P/'art_source/Thunderhawk';s=bpy.context.scene;r=bpy.data.objects['MattTrakker_Rig'];head=bpy.data.objects['MT_Head_AnatomicalSurface'];suit=bpy.data.objects['MT_ContinuousFlightSuit']
r['driving_pose']=0;r['mask_on']=False;r.location=(0,0,0);r.update_tag();s.frame_set(1);bpy.context.view_layer.update()
for v in head.data.vertices:
    z=v.co.z
    if z<1.593:
        t=max(0,min(1,(z-1.50)/.093));radius=.038+.020*t*t
        if v.co.x<-.015-radius:v.co.x=-.015-radius
        if v.co.x<0 and abs(v.co.y)>radius:v.co.y=math.copysign(radius,v.co.y)
        if z<1.550 and v.co.x>.030:v.co.x=.030
for f in head.data.polygons:f.use_smooth=True
head.data.update()
tree=BVHTree.FromPolygons([v.co.copy() for v in suit.data.vertices],[tuple(f.vertices) for f in suit.data.polygons])
for sg,sd in [(1,'L'),(-1,'R')]:
    ob=bpy.data.objects['MT_KneePatch_'+sd];vv=[];ff=[];N=19;Z=23
    for j in range(Z):
        z=.498+.082*j/(Z-1)
        for i in range(N):
            u=-1+2*i/(N-1);y=sg*.11+.039*u*(.9+.1*math.sin(math.pi*j/(Z-1)))
            point,normal,idx,d=tree.ray_cast(Vector((.3,y,z)),Vector((-1,0,0)),.5)
            analytic=.020+.064*math.sqrt(max(0,1-((y-sg*.11)/.062)**2))
            x=max(analytic,point.x if point is not None and point.x>.04 else analytic)+.0028
            vv.append((x,y,z))
    for j in range(Z-1):
        for i in range(N-1):ff.append((j*N+i,j*N+i+1,(j+1)*N+i+1,(j+1)*N+i))
    for mod in list(ob.modifiers):ob.modifiers.remove(mod)
    ob.vertex_groups.clear();ob.data.clear_geometry();ob.data.from_pydata(vv,[],ff);ob.data.update()
    for f in ob.data.polygons:f.use_smooth=True
    mod=ob.modifiers.new('FollowSameClothSurface','SURFACE_DEFORM');mod.target=suit;mod.falloff=6
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
    bpy.ops.object.surfacedeform_bind(modifier=mod.name)
    wall=ob.modifiers.new('ClothPatchThickness','SOLIDIFY');wall.thickness=.001
r['driving_pose']=1;r['mask_on']=False;r.location=(0,.4,0);r.update_tag();s.frame_set(97);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(T/'Thunderhawk_V13.blend'),compress=True)
print('V13_HEAD_NORMALS_NECK_AND_SURFACE_BOUND_KNEE_PATCHES_SAVED')
