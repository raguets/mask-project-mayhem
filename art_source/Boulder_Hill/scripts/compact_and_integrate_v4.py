import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector,noise
from math import sin,cos,pi
P=Path('G:/DEV/mask-project-mayhem');S=bpy.context.scene;R=bpy.data.objects['BoulderHill_Control']
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
S.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(P/'art_source/Boulder_Hill/Session_before_compact_v4.blend'),copy=True,compress=True)
# Preserve the approved mountain form, reduce the distant mass around the unchanged base opening.
for ob in [o for o in S.objects if o.name.startswith(('BH_SandstoneRoof','BH_SandstoneCliff_'))]:
    for v in ob.data.vertices:
        x,y,z=v.co
        if x<-14:x=-14+(x+14)*.60
        elif x>15:x=15+(x-15)*.60
        if y>10:y=10+(y-10)*.60
        if z>8.5:z=8.5+(z-8.5)*.62
        if ob.name=='BH_SandstoneCliff_front' and -14<x<15 and z<7:z-=.13*(1-max(0,(z-6.68)/2))
        v.co=(x,y,z)
    ob.data.update()
# A rear-connected asymmetric buttress replaces the isolated terraced column.
ob=bpy.data.objects['BH_RockColumnOuter'];N=128;H=49
for j in range(H):
    t=j/(H-1);z=7.20+t*4.82;base=2.55+3.6*(1-t)**1.25;cy=6+1.8*(1-t)
    for i in range(N):
        a=i*2*pi/N;envelope=sin(pi*t);pert=.44*noise.noise(Vector((cos(a)*2.8,sin(a)*2.8,t*2)))+.10*noise.noise(Vector((cos(a)*10,sin(a)*10,t*4)))
        r=base+pert*envelope;rear=6.5*max(0,sin(a))*(1-t)**1.2
        ob.data.vertices[j*N+i].co=(7+r*cos(a),cy+r*sin(a)+rear,z+.025*sin(a*5+t))
ob.data.update()
# A rectangular slab close to the building sides; pumps remain clear of the prism's sweep.
ob=bpy.data.objects['BH_StationSlab'];corners=[(-10.7,-19.8),(13.5,-19.8),(13.5,.7),(-10.7,.7)]
for i,v in enumerate(ob.data.vertices):x,y=corners[i%4];v.co.x=x;v.co.y=y
for ob in bpy.data.collections['BH_Pumps'].all_objects:
    if ob.parent==R:ob.location.y+=1.
# Near-flush surrounding terrain avoids a 30cm step in front of the compact slab.
for v in bpy.data.objects['BH_DesertGround'].data.vertices:v.co.z+=.30
co=bpy.data.collections['BH_Rock'];stone=bpy.data.materials['BH_Sandstone']
def mesh(name,v,f,parent,group,material):
    me=bpy.data.meshes.new(name+'_Editable');me.from_pydata(v,[],f);me.materials.append(material);me.update();o=bpy.data.objects.new(name,me);co.objects.link(o);o.parent=parent;o.matrix_parent_inverse=parent.matrix_world.inverted();o['BH_module']='rock' if group=='rock_static' else 'garage';o['BH_group']=group
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();return o
# Rock returns close the open side slots at the shop and the garage jamb.
for label,poly in [('Left',[(-12.9,-.1),(-10.05,-.1),(-10.05,1.4),(-13.8,2.0)]),('Right',[(12.36,-.1),(14.7,.3),(15.4,2.2),(12.36,1.6)])]:
    vv=[(x,y,z) for z in [-.03,6.76] for x,y in poly];ff=[(3,2,1,0),(4,5,6,7)]+[(i,(i+1)%4,4+(i+1)%4,4+i) for i in range(4)]
    o=mesh('BH_RockFrontReturn_'+label,vv,ff,R,'rock_static',stone);be=o.modifiers.new('BrokenRockEdges','BEVEL');be.width=.07;be.segments=2
# Moving transom closes the strip above the original rectangular shutter.
co=bpy.data.collections['BH_QuarterGarage'];g=bpy.data.objects['BH_GarageQuarterPivot'];vv=[(x,y,z) for x in [.30,12.10] for y in [.02,.18] for z in [6.,6.26]];ff=[(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)]
mesh('BH_StationGarageTransom',vv,ff,g,'garage_shell',bpy.data.materials['BH_StationPaint'])
# Move hinge axes out of the curved wall and provide small side relief to the door leaves.
half=math.asin(3/12)
for idx,angle in [(1,pi/4-half),(2,pi/4+half)]:
    hinge=bpy.data.objects['BH_ExitGateHinge_'+str(idx)];children=list(hinge.children);hinge.location.x=.2+12.30*cos(angle);hinge.location.y=12.30*sin(angle);bpy.context.view_layer.update()
    for child in children:
        child.matrix_parent_inverse=hinge.matrix_world.inverted()
        points=child.data.vertices if child.type=='MESH' else [p for sp in child.data.splines for p in sp.points] if child.type=='CURVE' else []
        for point in points:
            x,y,z=point.co[:3];r=math.hypot(x-.2,y);a=math.atan2(y,x-.2)
            if idx==1:a=angle+.003+(a-angle)*(half-.003)/half
            else:a=angle-.003-(angle-a)*(half-.003)/half
            point.co.x=.2+r*cos(a);point.co.y=r*sin(a)
for ob in S.objects:
    if ob.animation_data:
        for fc in ob.animation_data.drivers:fc.driver.expression=fc.driver.expression.replace(' + 0.0','')+' + 0.0'
    ob.update_tag()
S.name='BoulderHill_V4_Assembly';S['BoulderVersion']='V4';S['mountain_note']='Approved mountain form retained, reduced to about 32m high; turret promontory integrated as an asymmetric rear-connected buttress.';S['forecourt_note']='Compact rectangular slab 24.2 x 20.5m, no road; rock returns close building side slots.'
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P/'art_source/Boulder_Hill/BoulderHill_V4_Assembly.blend'),compress=True)
print('COMPACT_INTEGRATED_V4',max(v.co.z for v in bpy.data.objects['BH_SandstoneRoof'].data.vertices))
