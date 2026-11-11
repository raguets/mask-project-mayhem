import bpy,bmesh,math,re
from mathutils import Vector
from math import sin,cos,pi,sqrt
CURRENT=None;PARENT=None;GROUP='structure'
def collection(name):
    c=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(c);return c
def material(name,color,metal=0,rough=.4):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1);p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
def attach(o,root):
    if root:o.parent=root;o.matrix_parent_inverse=root.matrix_world.inverted()
    return o
def empty(name,pos=(0,0,0),parent=None,co=None):
    o=bpy.data.objects.new(name,None);(co or CURRENT).objects.link(o);o.location=pos;o.empty_display_size=.10;attach(o,parent);bpy.context.view_layer.update();return o
def mesh(name,verts,faces,mat,root=None,smooth=False,bevel=0,orient=None):
    me=bpy.data.meshes.new(name+'_Editable');me.from_pydata(verts,[],faces);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    if orient and sum(f.normal.dot(Vector(orient))*f.calc_area() for f in bm.faces)<0:bmesh.ops.reverse_faces(bm,faces=bm.faces)
    bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);CURRENT.objects.link(o);o['HU_group']=GROUP
    if mat:me.materials.append(mat)
    for p in me.polygons:p.use_smooth=smooth
    attach(o,root if root is not None else PARENT)
    if bevel:
        b=o.modifiers.new('ManufacturedEdges','BEVEL');b.width=bevel;b.segments=3;n=o.modifiers.new('WeightedNormals','WEIGHTED_NORMAL');n.keep_sharp=True
    return o
def box(name,p,d,mat,bevel=.015,root=None):
    x,y,z=p;dx,dy,dz=[v/2 for v in d];v=[(x+a,y+b,z+c) for a in [-dx,dx] for b in [-dy,dy] for c in [-dz,dz]];f=[(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)];return mesh(name,v,f,mat,root,bevel=bevel)
def tube(name,a,b,r,mat,r2=None,N=40,root=None,caps=True):
    a,b=Vector(a),Vector(b);q=(b-a).to_track_quat('Z','Y');v=[]
    for center,rr in [(a,r),(b,r if r2 is None else r2)]:v.extend(tuple(center+q@Vector((rr*cos(i*2*pi/N),rr*sin(i*2*pi/N),0))) for i in range(N))
    f=[(i,(i+1)%N,N+(i+1)%N,N+i) for i in range(N)]
    if caps:f.extend([tuple(reversed(range(N))),tuple(range(N,2*N))])
    return mesh(name,v,f,mat,root,smooth=True)
def path(name,points,r,mat,root=None):
    cu=bpy.data.curves.new(name+'_Editable','CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=3;sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
    for p,xyz in zip(sp.points,points):p.co=(*xyz,1)
    o=bpy.data.objects.new(name,cu);CURRENT.objects.link(o);cu.materials.append(mat);o['HU_group']=GROUP;attach(o,root if root is not None else PARENT);return o
def patch(name,us,vs,fn,mat,root=None,thick=.003,sub=1,orient=None,skip=None):
    v=[fn(u,t) for u in us for t in vs];N=len(vs);f=[]
    for i in range(len(us)-1):
        for j in range(N-1):
            if skip and skip((us[i]+us[i+1])/2,(vs[j]+vs[j+1])/2):continue
            f.append((i*N+j,(i+1)*N+j,(i+1)*N+j+1,i*N+j+1))
    used=sorted({k for face in f for k in face});remap={k:i for i,k in enumerate(used)};o=mesh(name,[v[k] for k in used],[tuple(remap[k] for k in face) for face in f],mat,root,True,orient=orient)
    if sub:
        counts={}
        for p in o.data.polygons:
            for e in p.edge_keys:counts[tuple(sorted(e))]=counts.get(tuple(sorted(e)),0)+1
        crease=o.data.attributes.new('crease_edge','FLOAT','EDGE')
        for e in o.data.edges:
            if counts[tuple(sorted(e.vertices))]==1:crease.data[e.index].value=1
        m=o.modifiers.new('BodySurfaceRefinement','SUBSURF');m.levels=sub;m.render_levels=sub
    if thick:m=o.modifiers.new('PanelThickness','SOLIDIFY');m.thickness=thick;m.offset=-1
    return o
def drive(o,prop,index,expr,variables):
    f=o.driver_add(prop,index) if index is not None else o.driver_add(prop);d=f.driver
    while d.variables:d.variables.remove(d.variables[0])
    for name,owner,key in variables:
        v=d.variables.new();v.name=name;v.type='SINGLE_PROP';v.targets[0].id=owner;v.targets[0].data_path='["'+key+'"]'
    expr=re.sub(r'(?<![A-Za-z0-9_])\.(\d)',r'0.\1',expr);assert len(expr)<245,(o.name,len(expr));d.expression=expr;return f
def text(name,body,p,size,mat,rot=(0,0,0),root=None):
    cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.size=size;cu.align_x='CENTER';cu.extrude=.0005;o=bpy.data.objects.new(name,cu);CURRENT.objects.link(o);o.location=p;o.rotation_euler=rot;cu.materials.append(mat);attach(o,root if root is not None else PARENT);return o
def profile(x,keys):
    if x<=keys[0][0]:return keys[0][1]
    for (a,v),(b,w) in zip(keys,keys[1:]):
        if x<=b:
            t=(x-a)/(b-a);t=t*t*(3-2*t);return v+(w-v)*t
    return keys[-1][1]
def seq(n,a=0,b=1):return [a+(b-a)*i/n for i in range(n+1)]
