"""Thunderhawk V9: exterior surfacing rebuild, metres, +X forward, +Z up.

Original procedural geometry observed from user photographs. Not a certified
cartoon replica or final AAA asset. No cockpit. Run in Blender, including via
the installed Blender MCP execute_code command. Set THK_V9_SCRIPT before exec
when __file__ is unavailable. Rebuilds only the active scene and saves V9.
"""
import bpy, bmesh, math, json, os
from pathlib import Path
from mathutils import Vector
from math import sin, cos, pi, sqrt

ROOT=Path('G:/DEV/mask-project-mayhem/art_source/Thunderhawk')
OUT=ROOT/'renders'/'v9'; OUT.mkdir(parents=True,exist_ok=True)
S=bpy.context.scene
# The live V8 is separately preserved before this script is executed via MCP.
for ob in list(S.objects): bpy.data.objects.remove(ob,do_unlink=True)
for coll in list(bpy.data.collections):
    if coll.name.startswith(('Reference_Study','THK9_')): bpy.data.collections.remove(coll)
S.name='THK_V9_Exterior_Study'
if 'THK9_dimension_calibrated' in S:del S['THK9_dimension_calibrated']
S.unit_settings.system='METRIC'; S.unit_settings.scale_length=1
S.render.fps=24; S.frame_start=1; S.frame_end=193; S.frame_set(1)
C=bpy.data.collections.new('THK9_Exterior'); S.collection.children.link(C)
STUDIO=bpy.data.collections.new('THK9_Review'); S.collection.children.link(STUDIO)
REF=bpy.data.collections.new('THK9_Reference'); S.collection.children.link(REF)
REF.hide_render=True; REF.hide_viewport=True

def mat(name,color,metal=0,rough=.35):
    m=bpy.data.materials.new('M_THK9_'+name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'); p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    return m
RED=mat('Red',(.48,.009,.014),.15,.30)
BLACK=mat('Black',(.009,.012,.015),.1,.40)
GLASS=mat('Glass',(.026,.055,.070),.25,.22)
RUBBER=mat('Rubber',(.013,.014,.016),0,.65)
ALU=mat('Alloy',(.47,.51,.54),.75,.27)
DARKMETAL=mat('Mechanism',(.065,.078,.086),.65,.32)
LENS=mat('Headlamp',(.66,.72,.73),.25,.22)
TAIL=mat('TailRed',(.42,.007,.012),.12,.26)
AMBER=mat('Amber',(.8,.20,.009),.10,.28)
WHITE=mat('Reverse',(.60,.64,.65),.10,.28)
PURPLE=mat('Purple',(.19,.032,.25),.05,.4)
YELLOW=mat('Yellow',(.96,.70,.015),.05,.4)
FLOOR=mat('ReviewFloor',(.065,.077,.09),0,.6)
# Original procedural grid in UV coordinates: paint detail, not raised strips.
GRID=PURPLE.copy(); GRID.name='M_THK9_PaintedGrid'
n=GRID.node_tree.nodes; l=GRID.node_tree.links
uv=n.new('ShaderNodeTexCoord'); sep=n.new('ShaderNodeSeparateXYZ');l.new(uv.outputs['UV'],sep.inputs[0])
tests=[]
for channel,count in [('X',13),('Y',4)]:
    a=n.new('ShaderNodeMath');a.operation='MULTIPLY';a.inputs[1].default_value=count;l.new(sep.outputs[channel],a.inputs[0])
    b=n.new('ShaderNodeMath');b.operation='FRACT';l.new(a.outputs[0],b.inputs[0])
    c=n.new('ShaderNodeMath');c.operation='LESS_THAN';c.inputs[1].default_value=.035;l.new(b.outputs[0],c.inputs[0]);tests.append(c)
mx=n.new('ShaderNodeMath');mx.operation='MAXIMUM';l.new(tests[0].outputs[0],mx.inputs[0]);l.new(tests[1].outputs[0],mx.inputs[1])
mix=n.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(.19,.032,.25,1);mix.inputs[2].default_value=(.037,.011,.055,1)
l.new(mx.outputs[0],mix.inputs[0]);l.new(mix.outputs[0],next(nd for nd in n if nd.type=='BSDF_PRINCIPLED').inputs['Base Color'])

def link(ob,coll=C): coll.objects.link(ob); return ob
def empty(name,loc=(0,0,0),parent=None):
    ob=link(bpy.data.objects.new(name,None));ob.location=loc;ob.empty_display_size=.08
    if parent: parent_keep(ob,parent)
    return ob
def parent_keep(ob,parent):
    bpy.context.view_layer.update();mw=ob.matrix_world.copy();ob.parent=parent
    ob.matrix_world=mw; bpy.context.view_layer.update();return ob
ROOT_OB=empty('THK_Root'); ROOT_OB['asset_version']='V9 surfacing study'; ROOT_OB['dimensions_estimated']=True
def mesh(name,verts,faces,material=RED,parent=ROOT_OB,orient=None):
    me=bpy.data.meshes.new(name+'_Control');me.from_pydata(verts,[],faces);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    if orient:
        # Orient complete connected components. Flipping individual faces can
        # create inconsistent winding on curved return flanges.
        unseen=set(bm.faces)
        while unseen:
            first=unseen.pop();component=[first];stack=[first]
            while stack:
                f=stack.pop()
                for e in f.edges:
                    for other in e.link_faces:
                        if other in unseen:unseen.remove(other);component.append(other);stack.append(other)
            score=0
            for f in component:
                c=f.calc_center_median();v=Vector(orient) if not isinstance(orient,str) else Vector((0,c.y,c.z-.62))
                score+=f.normal.dot(v)*f.calc_area()
            if score<0:bmesh.ops.reverse_faces(bm,faces=component)
    bm.to_mesh(me);bm.free();me.update()
    ob=link(bpy.data.objects.new(name,me));me.materials.append(material)
    if parent:parent_keep(ob,parent)
    for p in me.polygons:p.use_smooth=True
    return ob
def shell(ob,thick=.0025,sub=1,bevel=0):
    if sub:
        # Boundary crease maintains designed panel outlines and true openings.
        counts={}
        for p in ob.data.polygons:
            for ek in p.edge_keys: counts[tuple(sorted(ek))]=counts.get(tuple(sorted(ek)),0)+1
        cr=ob.data.attributes.new('crease_edge','FLOAT','EDGE')
        for e in ob.data.edges:
            if counts.get(tuple(sorted(e.vertices)),0)==1:cr.data[e.index].value=1
        m=ob.modifiers.new('Surface_refinement','SUBSURF');m.levels=sub;m.render_levels=sub
    if thick:
        m=ob.modifiers.new('Sheet_metal_thickness','SOLIDIFY');m.thickness=thick;m.offset=-1;m.use_even_offset=True
    if bevel:
        m=ob.modifiers.new('Edge_radius','BEVEL');m.width=bevel;m.segments=2
    return ob
def patch(name,us,vs,fn,material=RED,parent=ROOT_OB,orient=(0,0,1),sub=1,thick=.0025,skip=None):
    verts=[fn(u,v) for u in us for v in vs]; nv=len(vs);faces=[];uvs=[]
    for i in range(len(us)-1):
        for j in range(nv-1):
            if skip and skip((us[i]+us[i+1])/2,(vs[j]+vs[j+1])/2):continue
            faces.append((i*nv+j,(i+1)*nv+j,(i+1)*nv+j+1,i*nv+j+1))
    # Unused grid points inside openings must not remain as loose vertices.
    used=sorted(set(k for f in faces for k in f));remap={k:i for i,k in enumerate(used)}
    ob=mesh(name,[verts[k] for k in used],[tuple(remap[k] for k in f) for f in faces],material,parent,orient)
    uv=ob.data.uv_layers.new(name='SurfaceUV')
    for p in ob.data.polygons:
        for li in p.loop_indices:
            k=used[ob.data.loops[li].vertex_index]; uv.data[li].uv=(us[k//nv],vs[k%nv])
    return shell(ob,thick,sub)
def seq(n):return [i/n for i in range(n+1)]
EDGE=[0,.015,.05,.12,.22,.35,.5,.65,.78,.88,.95,.985,1]
def lerp(a,b,t):return a+(b-a)*t
def profile(t,keys):
    if t<=keys[0][0]:return keys[0][1]
    slopes=[(b[1]-a[1])/(b[0]-a[0]) for a,b in zip(keys,keys[1:])]
    tangents=[slopes[0]]
    for i in range(1,len(keys)-1):
        d0,d1=slopes[i-1],slopes[i]
        tangents.append(0 if d0*d1<=0 else 2*d0*d1/(d0+d1))
    tangents.append(slopes[-1])
    for i,((a,x),(b,y)) in enumerate(zip(keys,keys[1:])):
        if t<=b:
            f=(t-a)/(b-a);h=b-a
            return (2*f**3-3*f*f+1)*x+(f**3-2*f*f+f)*h*tangents[i]+(-2*f**3+3*f*f)*y+(f**3-f*f)*h*tangents[i+1]
    return keys[-1][1]
def box(name,loc,size,material=RED,parent=ROOT_OB,bevel=.003):
    x,y,z=[v/2 for v in size]
    ob=mesh(name,[(-x,-y,-z),(-x,-y,z),(-x,y,-z),(-x,y,z),(x,-y,-z),(x,-y,z),(x,y,-z),(x,y,z)],[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],material,None)
    ob.location=loc
    if parent:parent_keep(ob,parent)
    for p in ob.data.polygons:p.use_smooth=False
    if bevel:
        m=ob.modifiers.new('Manufactured_edge_radius','BEVEL');m.width=bevel;m.segments=3
        m=ob.modifiers.new('Face_weighted_normals','WEIGHTED_NORMAL');m.keep_sharp=True
    return ob
def tube(name,a,b,r,material=ALU,parent=ROOT_OB,n=32):
    d=Vector(b)-Vector(a);q=d.to_track_quat('Z','Y');verts=[]
    for p in (Vector(a),Vector(b)):
        verts.extend([p+q@Vector((r*cos(2*pi*i/n),r*sin(2*pi*i/n),0)) for i in range(n)])
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    ob=mesh(name,verts,faces,material,parent)
    for p in ob.data.polygons:p.use_smooth=len(p.vertices)==4
    return ob
def ring_surface(name,fn,outer=(0,1,0,1),inner=(.045,.955,.055,.945),material=RED,parent=ROOT_OB,sub=1):
    # Four connected quad strips, no opaque face behind the glass.
    def outline(rect):
        a,b,c,d=rect;return [(a,c),(b,c),(b,d),(a,d)]
    oo=outline(outer);ii=outline(inner);verts=[fn(*p) for p in oo+ii]
    ob=mesh(name,verts,[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)],material,parent,'radial')
    return shell(ob,.004,sub)
def conform_polygon(name,points,fn,material,parent=ROOT_OB,orient=(0,0,1)):
    from mathutils.geometry import tessellate_polygon
    polygon=[Vector((u,v,0)) for u,v in points]
    triangles=[[p if hasattr(p,'x') else polygon[int(p)] for p in tri] for tri in tessellate_polygon([polygon])]
    verts=[];faces=[];lookup={};nn=12
    def vertex(p):
        key=(round(p.x,9),round(p.y,9))
        if key not in lookup:
            lookup[key]=len(verts);verts.append(fn(p.x,p.y))
        return lookup[key]
    for a,b,c in triangles:
        ids={}
        for i in range(nn+1):
            for j in range(nn+1-i):ids[i,j]=vertex(a+(b-a)*(i/nn)+(c-a)*(j/nn))
        for i in range(nn):
            for j in range(nn-i):
                faces.append((ids[i,j],ids[i+1,j],ids[i,j+1]))
                if i+j<nn-1:faces.append((ids[i+1,j],ids[i+1,j+1],ids[i,j+1]))
    return mesh(name,verts,faces,material,parent,orient)

# Master dimensions and support curves, estimated from photographs.
WC=[-1.42,1.40]; R=.328; ARCH=.369
def width(x):return profile(x,[(-2.41,.858),(-2.27,.90),(-1.70,.925),(-1,.923),(.90,.925),(1.5,.931),(2.13,.893),(2.40,.806)])
def belt(x):return profile(x,[(-2.40,.794),(-2.20,.824),(-1.70,.86),(-1,.88),(.90,.88),(1.4,.868),(2,.795),(2.40,.697)])
def nose_x(y,z):return 2.405-.065*(abs(y)/.85)**5-.065*((z-.44)/.30)
def hood_z(x,y):
    t=(x-.94)/(2.31-.94); yn=abs(y)/.748
    return lerp(.868,.701,t)+.023*(1-yn*yn)+.013*sin(pi*min(1,max(0,t)))+ .013*math.exp(-((yn/.25)**4))*sin(pi*min(1,max(0,t)))
def hood_fn(u,v):
    x=lerp(.944,2.306,u);y=lerp(-.739,.739,v)
    return (x,y,hood_z(x,y))
hood=patch('THK_Hood',EDGE,EDGE,hood_fn,sub=2)
hood['construction']='Crowned quad surface; independent panel, not stacked plates'
for sign,side in [(1,'L'),(-1,'R')]:
    # Front/rear fenders each have a curved shoulder and a quad arch-following side.
    for kind,a,b,wc in [('Front',.894,2.39,1.40),('Rear',-2.38,-.978,-1.42)]:
        xs=sorted(set([a,b]+[lerp(a,b,t) for t in EDGE]+[wc+ARCH*cos(pi*i/28) for i in range(29) if a<wc+ARCH*cos(pi*i/28)<b]))
        def topfn(u,v,a=a,b=b,kind=kind,sign=sign):
            x=lerp(a,b,u);wy=width(x);inner=.747 if kind=='Front' else profile(x,[(-2.4,.842),(-1.745,.788),(-.98,.855)])
            y=lerp(inner,wy,v)
            base=hood_z(min(2.31,max(.94,x)),inner) if kind=='Front' else profile(x,[(-2.4,.797),(-1.745,.845),(-.98,.886)])
            z=lerp(base,belt(x)-.022,v)+.036*sin(pi*v)
            if kind=='Front':
                x+=(1-u)**8*(lerp(.944,.892,v)-a)
                if x>1.85:x=lerp(1.85,nose_x(sign*y,z),(x-1.85)/(b-1.85))
            return(x,sign*y,z)
        patch('THK_'+kind+'FenderCrown_'+side,[((x-a)/(b-a)) for x in xs],[0,.025,.12,.28,.5,.72,.9,.975,1],topfn,orient=(0,0,1),sub=1)
        def sidefn(u,v,a=a,b=b,wc=wc,sign=sign,kind=kind):
            x=lerp(a,b,u);dx=x-wc
            lower=.327+sqrt(max(0,ARCH*ARCH-dx*dx)) if abs(dx)<ARCH else .325
            upper=belt(x)-.022;z=lerp(lower,upper,v)
            y=width(x)-.014*(1-v)+.006*sin(pi*v)
            if kind=='Front':
                edge=profile(z,[(.325,.868),(.435,.855),(.596,.865),(.846,.889),(.908,.891)])
                x+=(1-u)**8*(edge-a)
                if x>1.85:x=lerp(1.85,nose_x(sign*y,z),(x-1.85)/(b-1.85))
            return(x,sign*y,z)
        patch('THK_'+kind+'QuarterSkin_'+side,[(x-a)/(b-a) for x in xs],[0,.025,.10,.3,.55,.8,.97,1],sidefn,orient=(0,sign,0),sub=1)
        def archfn(u,v,wc=wc,sign=sign):
            ang=pi*u;r=ARCH+v*.014;x=wc+r*cos(ang);z=.327+r*sin(ang)
            return(x,sign*(width(x)-.013+.008*sin(pi*v)),z)
        patch('THK_'+kind+'ArchLip_'+side,seq(40),[0,.15,.5,.85,1],archfn,orient=(0,sign,0),sub=0,thick=.002)
        # Inner wheelhouse masks are exterior arch liners, not an interior cockpit.
        def linerfn(u,v,wc=wc,sign=sign):
            ang=pi*u;r=ARCH+.010;return(wc+r*cos(ang),sign*lerp(.78,.913,v),.327+r*sin(ang))
        patch('THK_'+kind+'Wheelhouse_'+side,seq(36),[0,1],linerfn,BLACK,orient=(0,sign,0),sub=0,thick=.002)
    box('THK_Rocker_'+side,(-.03,sign*.882,.352),(1.93,.077,.105),RED,bevel=.018)
    box('THK_RockerRubStrip_'+side,(-.03,sign*.927,.351),(1.91,.009,.026),BLACK,bevel=.004)

# Bent gull-wing door cage, continuous roof -> glazed frame -> belt -> skin.
DQ=[0,.025,.12,.20,.25,.28,.30,.36,.44,.52,.57,.60,.625,.65,.69,.77,.88,.97,1]
DU=[0,.018,.055,.075,.18,.32,.5,.68,.82,.925,.945,.982,1]
def door_point(u,q,sign):
    y=profile(q,[(0,.127),(.20,.55),(.25,.619),(.30,.656),(.57,.838),(.60,.866),(.65,.910),(.69,.925),(.88,.921),(1,.887)])
    z=profile(q,[(0,1.300),(.20,1.293),(.25,1.270),(.30,1.228),(.57,.949),(.60,.908),(.65,.872),(.69,.846),(.88,.596),(1,.435)])
    xr=profile(q,[(0,-.786),(.25,-.805),(.60,-.965),(1,-.965)])
    xf=profile(q,[(0,.328),(.25,.346),(.60,.887),(1,.851)])
    x=lerp(xr,xf,u)
    y+=.003*sin(pi*u)*sin(pi*q)
    return(x,sign*y,z)
hinges={};deploys={};guides=[]
for sign,side in [(1,'L'),(-1,'R')]:
    hinge=empty('THK_Wing_Hinge_'+side,(0,sign*.127,1.300),ROOT_OB);hinges[side]=hinge
    skin=patch('THK_DoorShell_'+side,DU,DQ,lambda u,q,sg=sign:door_point(u,q,sg),RED,hinge,'radial',sub=1,thick=.0024,
               skip=lambda u,q:.055<u<.945 and .30<q<.57)
    skin['construction']='Continuous bent quad cage with actual window aperture'
    def glassfn(u,v,sg=sign):
        x,y,z=door_point(lerp(.058,.942,u),lerp(.302,.568,v),sg)
        return(x,y-sg*.005,z-.001)
    patch('THK_DoorGlass_'+side,EDGE,EDGE,glassfn,GLASS,hinge,'radial',sub=1,thick=.003)
    # Roof insert follows the crown; side trim follows the real body surface.
    def roofglass(u,v,sg=sign):
        x,y,z=door_point(lerp(.095,.905,u),lerp(.025,.185,v),sg);return(x,y,z+.0006)
    patch('THK_DoorRoofInset_'+side,EDGE,EDGE,roofglass,GLASS,hinge,(0,0,1),sub=1,thick=.001)
    # Door-edge returns are explicit folded metal, below the external skin.
    for end,u in [('Front',1),('Rear',0)]:
        def returnfn(q,v,u=u,sg=sign):
            x,y,z=door_point(u,q,sg);return(x+(.004 if u==0 else -.004),y-sg*.020*v,z-.006*v)
        patch('THK_DoorReturn'+end+'_'+side,DQ,[0,1],returnfn,DARKMETAL,hinge,'radial',sub=0,thick=.0015)
    box('THK_DoorSeal_'+side,(-.05,sign*.866,.432),(1.80,.012,.018),BLACK,hinge,.003)
    box('THK_DoorHandleRecess_'+side,(-.67,sign*.925,.813),(.13,.006,.035),BLACK,hinge,.001)
    box('THK_DoorHandle_'+side,(-.67,sign*.933,.817),(.09,.012,.010),DARKMETAL,hinge,.003)
    # Mirror housing: closed tapered volume rather than a plain cube.
    vv=[]
    for x,w,z0,z1 in [(.67,.032,.995,1.055),(.81,.054,.980,1.051)]:
        for y,z in [(sign*.94-w,z0),(sign*.94+w,z0),(sign*.94+w,z1),(sign*.94-w,z1)]:vv.append((x,y,z))
    mi=mesh('THK_MirrorHousing_'+side,vv,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],RED,hinge)
    mod=mi.modifiers.new('Housing_radius','BEVEL');mod.width=.012;mod.segments=3
    box('THK_MirrorGlass_'+side,(.670,sign*.944,1.024),(.003,.067,.039),ALU,hinge,.0005)
    tube('THK_MirrorStalk_'+side,(.72,sign*.854,.946),(.744,sign*.924,1.005),.012,DARKMETAL,hinge)
    # Separate fixed rail and retracting weapon: the gun truly deploys in flight.
    box('THK_CannonMountRail_'+side,(-.05,sign*.936,.507),(1.77,.040,.050),ALU,hinge,.010)
    dep=empty('THK_CannonDeploy_'+side,(0,0,0),hinge);deploys[side]=dep
    tube('THK_DoorCannon_'+side,(-.71,sign*.963,.500),(.78,sign*.963,.500),.024,ALU,dep,48)
    tube('THK_CannonSleeve_'+side,(.26,sign*.963,.500),(.62,sign*.963,.500),.039,ALU,dep,48)
    # Annular muzzle with genuine bore and a recessed back face.
    verts=[];nseg=40
    for xx,rr in [(.78,.035),(.82,.033),(.82,.022),(.74,.022)]:
        verts.extend([(xx,sign*.963+rr*cos(2*pi*i/nseg),.5+rr*sin(2*pi*i/nseg)) for i in range(nseg)])
    ff=[]
    for k in range(3): ff += [(k*nseg+i,k*nseg+(i+1)%nseg,(k+1)*nseg+(i+1)%nseg,(k+1)*nseg+i) for i in range(nseg)]
    muzzle=mesh('THK_CannonMuzzle_'+side,verts,ff,ALU,dep)
    tube('THK_CannonBoreBack_'+side,(.736,sign*.963,.500),(.738,sign*.963,.500),.022,BLACK,dep,40)
    for xx in (-.53,.15):box('THK_CannonSlide_'+side+('_Rear' if xx<0 else '_Front'),(xx,sign*.949,.511),(.11,.065,.050),DARKMETAL,dep,.007)
    # Sliding guides retain physical attachment while the cannon extends.
    for xx in (-.53,.15):
        ob=box('THK_CannonGuide_'+side+('_Rear' if xx<0 else '_Front'),(xx,sign*.949,.5092),(.018,.018,.180),DARKMETAL,hinge,.002)
        guides.append((ob,ob.location.copy()))

# Fixed central roof spine, cowl and compound-curved glazing.
patch('THK_RoofSpine',EDGE,EDGE,lambda u,v:(lerp(-.79,.33,u),lerp(-.122,.122,v),1.302+.004*sin(pi*u)*sin(pi*v)),sub=1,thick=.003)
def wind(u,v):
    x=lerp(.927,.341,v)+.021*sin(pi*v)*(1-(2*u-1)**2)
    w=lerp(.841,.614,v);return(x,(2*u-1)*w,lerp(.891,1.296,v)+.006*sin(pi*u)*sin(pi*v))
ring_surface('THK_WindshieldFrame',wind,inner=(.030,.970,.045,.955),sub=0)
patch('THK_Windshield',EDGE,EDGE,lambda u,v:tuple(Vector(wind(lerp(.032,.968,u),lerp(.047,.953,v)))+Vector((-.003,0,-.001))),GLASS,orient=(1,0,1),sub=1,thick=.003)
for sign,side in [(1,'L'),(-1,'R')]:
    def door_aframe(u,v,sg=sign):
        q=lerp(.25,.615,u);a=Vector(door_point(1,q,sg))
        wv=max(0,min(1,(a.z-.891)/.405));b=Vector(wind(1 if sg==1 else 0,wv));b.x-=.012;b.y+=sg*.006
        return tuple(a.lerp(b,v))
    patch('THK_DoorAFrame_'+side,EDGE,[0,.10,.90,1],door_aframe,RED,hinges[side],(0,sign,1),sub=1,thick=.002)
    for a,b in [(-.65,-.49),(.08,.24)]:
        tube('THK_RoofHinge_'+side+('_Rear' if a<0 else '_Front'),(a,sign*.127,1.294),(b,sign*.127,1.294),.015,DARKMETAL,ROOT_OB,24)
patch('THK_Cowl',EDGE,[0,.1,.9,1],lambda u,v:(lerp(.927,.940,v),lerp(-.84,.84,u),lerp(.891,.870,v)),BLACK,orient=(0,0,1),sub=1,thick=.003)
patch('THK_FrontRoofHeader',EDGE,[0,.1,.9,1],lambda u,v:(lerp(.375,.399,v),lerp(-.621,.621,u),lerp(1.286,1.267,v)-.020*abs(2*u-1)**6),RED,orient=(0,0,1),sub=1,thick=.004)
def rear_glass(u,v):
    w=lerp(.785,.614,v);y=(2*u-1)*w;x=lerp(-1.738,-.827,v)-.025*sin(pi*v)*(1-(2*u-1)**2)
    z=lerp(.847,1.286,v)+.012*sin(pi*u)*sin(pi*v);return(x,y,z)
ring_surface('THK_HatchFrame',rear_glass,inner=(.035,.965,.045,.95),sub=0)
patch('THK_RearGlass',EDGE,EDGE,lambda u,v:tuple(Vector(rear_glass(lerp(.038,.962,u),lerp(.05,.947,v)))+Vector((.002,0,-.001))),GLASS,orient=(-1,0,1),sub=1,thick=.003)
patch('THK_RearRoofHeader',EDGE,[0,.1,.9,1],lambda u,v:(lerp(-.815,-.854,v),lerp(-.621,.621,u),lerp(1.291,1.271,v)-.018*abs(2*u-1)**6),RED,orient=(0,0,1),sub=1,thick=.004)
for sign,side in [(1,'L'),(-1,'R')]:
    # Curved front edge follows the actual closed door, with an explicit 7 mm
    # longitudinal clearance. A straight triangular frame intersected the door.
    def quarterfn(u,v,sg=sign):
        q=lerp(.25,.615,u);front=Vector(door_point(0,q,sg));front.x-=.007;front.y+=sg*.001
        rear=Vector((lerp(-.832,-1.738,u),sg*lerp(.622,.785,u),lerp(1.275,.847,u)))
        return tuple(front.lerp(rear,v))
    station=[0,.025,.10,.16,.25,.42,.60,.78,.90,.97,1]
    patch('THK_C_Pillar_'+side,station,[0,.04,.17,.32,.5,.68,.83,.96,1],quarterfn,RED,ROOT_OB,(0,sign,0),sub=1,thick=.003,
          skip=lambda u,v:.16<u<.90 and .17<v<.83)
    patch('THK_QuarterGlass_'+side,EDGE,EDGE,lambda u,v,fn=quarterfn,sg=sign:tuple(Vector(fn(lerp(.162,.898,u),lerp(.172,.828,v)))+Vector((0,-sg*.003,0))),GLASS,orient=(0,sign,0),sub=1,thick=.002)
    # Fine belt molding is a real strip, kept close to the skin.
    tube('THK_QuarterBeltTrim_'+side,(-1.70,sign*.802,.852),(-.980,sign*.877,.890),.005,BLACK,ROOT_OB,12)

# Sculpted nose assembled around recessed four-lamp apertures.
# Front surface is raked and curves back into the fenders at its corners.
def nose_x(y,z):
    return 2.405-.065*(abs(y)/.85)**5-.065*((z-.44)/.30)
def nose_fn(u,v):
    y=lerp(-.849,.849,u);z=lerp(.355,.708,v)
    return(nose_x(y,z),y,z)
# Coordinate stations explicitly border lamp and lower intake openings.
ys=[-.849,-.81,-.77,-.45,-.405,-.25,0,.25,.405,.45,.77,.81,.849]
zs=[.355,.375,.405,.475,.5,.565,.675,.695,.708]
def opening(y,z):
    return (.45<abs(y)<.77 and .565<z<.675) or (.25<abs(y)<.405 and .405<z<.475)
patch('THK_NoseFascia',[(y+.849)/1.698 for y in ys],[(z-.355)/.353 for z in zs],nose_fn,orient=(1,0,0),sub=0,thick=.004,
      skip=lambda u,v:opening(lerp(-.849,.849,u),lerp(.355,.708,v)))
def nose_header(u,v):
    y=lerp(-.744,.744,u);innerz=hood_z(2.306,y)
    return(lerp(2.298,nose_x(y,.708),v),y,lerp(innerz-.002,.708,v))
patch('THK_NoseUpperBridge',EDGE,[0,.12,.88,1],nose_header,orient=(0,0,1),sub=1,thick=.003)
for sign,side in [(1,'L'),(-1,'R')]:
    for kind,ya,yb,za,zb,depth in [('Headlamp',.45,.77,.565,.675,.105),('Intake',.25,.405,.405,.475,.10)]:
        ya,yb=sorted((sign*ya,sign*yb));corners=[(ya,za),(yb,za),(yb,zb),(ya,zb)]
        front=[(nose_x(y,z),y,z) for y,z in corners]
        back=[(x-depth,y,z) for x,y,z in front]
        ob=mesh('THK_'+kind+'Recess_'+side,front+back,[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)],BLACK)
        for p in ob.data.polygons:p.use_smooth=False
        mesh('THK_'+kind+'Back_'+side,back,[(0,1,2,3)],BLACK,orient=(1,0,0))
        if kind=='Headlamp':
            for j in range(2):
                cy=lerp(ya,yb,(j+.5)/2);cx=nose_x(cy,.62)-.078
                box('THK_HeadlampHousing_'+side+str(j),(cx-.012,cy,.618),(.035,.147,.088),DARKMETAL,bevel=.005)
                box('THK_HeadlampLens_'+side+str(j),(cx+.010,cy,.618),(.009,.136,.077),LENS,bevel=.004)
                # Lens ribs are subtle, integrated optical geometry inside the recess.
                for k in range(1,7):box('THK_LensFlute_'+side+str(j)+'_'+str(k),(cx+.015,cy-.068+k*.019,.618),(.0015,.001,.067),LENS,bevel=0)
        else:
            for k in range(3):box('THK_IntakeVane_'+side+str(k),(2.31,(ya+yb)/2,lerp(za,zb,(k+1)/4)),(.045,yb-ya-.008,.005),DARKMETAL,bevel=.001)
    box('THK_FrontSideMarker_'+side,(1.98,sign*(width(1.98)+.001),.562),(.145,.009,.038),AMBER,bevel=.005)
# Lower valance and bumper follow the curved nose, rather than a straight bar.
patch('THK_FrontBumper',EDGE,[0,.08,.25,.75,.92,1],lambda u,v:(nose_x(lerp(-.861,.861,u),lerp(.362,.399,v))+.008,lerp(-.861,.861,u),lerp(.362,.399,v)),ALU,orient=(1,0,0),sub=1,thick=.012)
patch('THK_FrontAirDam',EDGE,[0,.1,.85,1],lambda u,v:(2.38-.06*(abs(2*u-1)**5)-.03*(1-v),lerp(-.84,.84,u),lerp(.298,.356,v)),RED,orient=(1,0,0),sub=1,thick=.004)

# Rear deck and enveloping fixed tail band.
patch('THK_RearDeck',EDGE,EDGE,lambda u,v:(lerp(-2.367,-1.745,u),lerp(-.84,.84,v),lerp(.797,.845,u)+.012*sin(pi*v)),sub=1,thick=.003)
def tail_point(u,v):
    y=lerp(-.857,.857,u);z=lerp(.605,.797,v);return(-2.362+.055*(abs(y)/.857)**5,y,z)
patch('THK_FixedTailBand',EDGE,[0,.04,.15,.5,.85,.96,1],tail_point,orient=(-1,0,0),sub=1,thick=.004)
for sign,side in [(1,'L'),(-1,'R')]:
    box('THK_TailLampBezel_'+side,(-2.367,sign*.512,.700),(.024,.636,.139),BLACK,bevel=.011)
    for j in range(4):
        for k in range(2):
            yy=sign*(.225+j*.150);zz=.666+k*.063
            material=TAIL if j in (2,3) or k==1 else (WHITE if j==0 else AMBER)
            box('THK_TailLens_'+side+str(j)+str(k),(-2.384,yy,zz),(.010,.141,.055),material,bevel=.005)
    # Side wrapping portion of the light assembly follows the rounded quarter.
    box('THK_TailSideLens_'+side,(-2.27,sign*.866,.703),(.115,.010,.090),TAIL,bevel=.007)
box('THK_RearPlateRecess',(-2.369,0,.695),(.014,.337,.133),BLACK,bevel=.009)
box('THK_RearPlate',(-2.380,0,.692),(.004,.258,.095),ALU,bevel=.0006)
rear_lift=empty('THK_RearPanel_Lift',parent=ROOT_OB)
def rear_bumper(u,v):
    y=lerp(-.873,.873,u);z=lerp(.313,.572,v)
    x=-2.420+.080*(abs(y)/.873)**5-.008*sin(pi*v)
    return(x,y,z)
patch('THK_RearPanel',EDGE,[0,.035,.10,.27,.50,.75,.9,.965,1],rear_bumper,RED,rear_lift,(-1,0,0),sub=1,thick=.012)
patch('THK_RearBumperRubStrip',EDGE,[0,1],lambda u,v:(rear_bumper(u,.19+v*.055)[0]-.001,lerp(-.873,.873,u),lerp(.362,.376,v)),BLACK,rear_lift,(-1,0,0),sub=1,thick=.002)
for sign,side in [(1,'L'),(-1,'R')]:
    patch('THK_RearBumperReturn_'+side,EDGE,[0,.1,.9,1],lambda u,v,sg=sign:(lerp(-2.36,-2.22,u),sg*(.873+.005*sin(pi*u)),lerp(.319,.567,v)),RED,rear_lift,(0,sign,0),sub=1,thick=.006)
box('THK_RearValance',(-2.295,0,.303),(.15,1.65,.055),DARKMETAL,bevel=.010)

def rounded_rect(w,h,r,n=8):
    points=[]
    for cy,cz,start in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
        for i in range(n):
            a=math.radians(start+i*90/n);points.append((cy+r*cos(a),cz+r*sin(a)))
    return points
for sign,side in [(1,'L'),(-1,'R')]:
    loops=[]
    # Rounded oblong bezel, rolled metallic mouth and converging nozzle throat.
    sections=[(-2.332,.548,.239,.092),(-2.355,.535,.227,.087),(-2.365,.507,.204,.079),(-2.351,.464,.166,.064),(-2.192,.404,.134,.050),(-2.151,.404,.134,.050)]
    for x,w,h,r in sections:loops.append([(x,sign*.485+y,.430+z) for y,z in rounded_rect(w,h,r)])
    nv=len(loops[0]);verts=[p for loop in loops for p in loop];faces=[]
    for j in range(len(loops)-1):faces.extend([(j*nv+i,j*nv+(i+1)%nv,(j+1)*nv+(i+1)%nv,(j+1)*nv+i) for i in range(nv)])
    faces.append(tuple(range((len(loops)-1)*nv,len(loops)*nv)))
    nozzle=mesh('THK_Reactor_'+side,verts,faces,ALU)
    for p in nozzle.data.polygons:p.use_smooth=len(p.vertices)==4
    box('THK_ReactorThroat_'+side,(-2.180,sign*.485,.430),(.012,.394,.124),BLACK,bevel=.018)
    for j in range(4):box('THK_ReactorVane_'+side+str(j),(-2.237,sign*.485+(j-1.5)*.080,.430),(.080,.010,.102),DARKMETAL,bevel=.002)
    for edge in (-1,1):
        box('THK_ReactorHousingSide_'+side+str(edge),(-2.18,sign*.485+edge*.277,.428),(.30,.020,.254),DARKMETAL,bevel=.004)
        box('THK_ReactorHousingCap_'+side+str(edge),(-2.18,sign*.485,.428+edge*.121),(.30,.54,.018),DARKMETAL,bevel=.004)

# Cambered stabilizer, restrained raised tips and independent central lift.
spoiler_lift=empty('THK_Spoiler_Lift',parent=ROOT_OB)
def spoiler_point(u,v):
    y=lerp(-.867,.867,u);x=lerp(-2.17,-1.89,v)+.020*(abs(y)/.867)**5
    z=.968+.012*sin(pi*v)+.018*(abs(y)/.867)**8
    return(x,y,z)
patch('THK_RearStabilizer',EDGE,EDGE,spoiler_point,RED,spoiler_lift,(0,0,1),sub=1,thick=.020)
box('THK_SpoilerBase',(-2.015,0,.849),(.12,.18,.055),BLACK,bevel=.012)
post=box('THK_SpoilerTelescopicPost',(-2.015,0,.900),(.10,.11,.12),DARKMETAL,bevel=.006)
box('THK_SpoilerUpperPost',(-2.015,0,.938),(.085,.10,.075),BLACK,spoiler_lift,.006)

# Tires are closed lathed volumes. Rim apertures are true cutouts.
def lathe_y(name,xc,yc,zc,points,material,parent,n=80):
    verts=[]
    for yy,rr in points:
        verts.extend([(xc+rr*cos(2*pi*i/n),yc+yy,zc+rr*sin(2*pi*i/n)) for i in range(n)])
    faces=[];k=len(points)
    for j in range(k): faces.extend([(j*n+i,j*n+(i+1)%n,((j+1)%k)*n+(i+1)%n,((j+1)%k)*n+i) for i in range(n)])
    return mesh(name,verts,faces,material,parent)
def bool_diff(ob,cutter):
    bpy.context.view_layer.objects.active=ob
    m=ob.modifiers.new('Manufactured_aperture','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cutter
    bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cutter,do_unlink=True)
for xc,ax in [(1.40,'F'),(-1.42,'R')]:
    for sign,side in [(1,'L'),(-1,'R')]:
        yy=sign*.818;zc=.328;wheel=empty('THK_WheelPivot_'+ax+side,(xc,yy,zc),ROOT_OB)
        pts=[(-.116,.215),(-.120,.264),(-.110,.295),(-.090,.319),(-.06,.327),(-.03,.328),(.03,.328),(.06,.327),(.09,.319),(.11,.295),(.12,.264),(.116,.215),(.08,.205),(-.08,.205)]
        lathe_y('THK_Tire_'+ax+side,xc,yy,zc,pts,RUBBER,wheel)
        out=yy+sign*.116
        rim=tube('THK_Rim_'+ax+side,(xc,out-sign*.044,zc),(xc,out,zc),.225,ALU,wheel,80)
        for j in range(5):
            a=2*pi*j/5+pi/2;xx=xc+.137*cos(a);zz=zc+.137*sin(a)
            cutter=tube('TEMP_RimOpening',(xx,out-.08,zz),(xx,out+.08,zz),.049,BLACK,None,32)
            bool_diff(rim,cutter)
        m=rim.modifiers.new('Aperture_edge_radius','BEVEL');m.width=.002;m.segments=3
        m=rim.modifiers.new('Machined_face_normals','WEIGHTED_NORMAL');m.keep_sharp=True
        for p in rim.data.polygons:p.use_smooth=len(p.vertices)==4
        # Bright rolled rim lip and recessed dark brake are real surfaces.
        lathe_y('THK_RimLip_'+ax+side,xc,out,zc,[(-.006,.212),(0,.226),(.004,.228),(.008,.223),(.008,.214)],ALU,wheel)
        tube('THK_BrakeDisc_'+ax+side,(xc,out-sign*.060,zc),(xc,out-sign*.055,zc),.190,DARKMETAL,wheel,64)
        tube('THK_Hub_'+ax+side,(xc,out,zc),(xc,out+sign*.017,zc),.065,ALU,wheel,40)
        for j in range(5):
            a=2*pi*j/5;xx=xc+.043*cos(a);zz=zc+.043*sin(a)
            tube('THK_Lug_'+ax+side+str(j),(xx,out+sign*.017,zz),(xx,out+sign*.022,zz),.007,DARKMETAL,wheel,6)
        lathe_y('THK_SidewallBead_'+ax+side,xc,yy,zc,[(sign*.117,.266),(sign*.119,.267),(sign*.118,.270),(sign*.116,.269)],RUBBER,wheel)

# Original livery conforms to the new surfaces; no stacked decorative plates.
for sign,side in [(1,'L'),(-1,'R')]:
    def hoodpaint(u,v,sg=sign):
        x=lerp(1.04,2.20,u);y=sg*lerp(.415,.632,v);return(x,y,hood_z(x,y)+.0020)
    patch('THK_HoodPaint_'+side,EDGE,EDGE,hoodpaint,GRID,orient=(0,0,1),sub=1,thick=0)
    # Lightning polygon authored in patch UV, projected onto the actual crown.
    bolt=[(.03,.67),(.34,.15),(.34,.47),(.64,.08),(.62,.48),(.96,.20),(.53,.90),(.54,.55),(.27,.94),(.28,.61)]
    conform_polygon('THK_HoodLightning_'+side,bolt,lambda u,v:tuple(Vector(hoodpaint(u,v))+Vector((0,0,.0005))),YELLOW)
    def doorpaint(u,v,sg=sign):
        x,y,z=door_point(lerp(.085,.915,u),lerp(.745,.855,v),sg);return(x,y+sg*.0007,z)
    patch('THK_DoorPaint_'+side,EDGE,[0,.1,.9,1],doorpaint,PURPLE,hinges[side],(0,sign,0),sub=1,thick=0)
    bolt2=[(.1,.40),(.42,.12),(.40,.42),(.90,.20),(.61,.77),(.64,.48),(.28,.77),(.31,.48)]
    conform_polygon('THK_DoorLightning_'+side,bolt2,lambda u,v:tuple(Vector(doorpaint(u,v))+Vector((0,sign*.0007,0))),YELLOW,hinges[side],(0,sign,0))
patch('THK_HoodPaintCentre',EDGE,EDGE,lambda u,v:(lerp(1.03,2.20,u),lerp(-.13,.13,v),hood_z(lerp(1.03,2.20,u),lerp(-.13,.13,v))+.0020),GRID,orient=(0,0,1),sub=1,thick=0)
patch('THK_SpoilerPaint',EDGE,EDGE,lambda u,v:tuple(Vector(spoiler_point(lerp(.015,.985,u),lerp(.045,.955,v)))+Vector((0,0,.0007))),GRID,spoiler_lift,(0,0,1),sub=1,thick=0)

# Exterior-only underbody cover; cabin is deliberately not modeled.
box('THK_ExteriorBlackout',(-.07,0,.395),(1.96,1.64,.045),BLACK,bevel=.012)
box('THK_Undertray',(-.05,0,.284),(3.9,1.56,.025),BLACK,bevel=.015)
box('THK_FrontBulkhead',(.905,0,.609),(.012,1.65,.420),BLACK,bevel=.003)
box('THK_RearBulkhead',(-.988,0,.609),(.012,1.65,.420),BLACK,bevel=.003)
for side,sg in [('L',1),('R',-1)]:empty('SOCKET_Muzzle_'+side,(.82,sg*.963,.5),deploys[side])
for name,loc in [('SOCKET_Reactor_L',(-2.36,.485,.43)),('SOCKET_Reactor_R',(-2.36,-.485,.43))]:empty(name,loc,ROOT_OB)

def keys(ob,channel,values):
    for fr,val in values:
        setattr(ob,channel,val);ob.keyframe_insert(data_path=channel,frame=fr)
    if ob.animation_data and ob.animation_data.action:
        action=ob.animation_data.action
        curves=list(getattr(action,'fcurves',[]))
        for layer in getattr(action,'layers',[]):
            for strip in layer.strips:
                for bag in getattr(strip,'channelbags',[]):curves.extend(bag.fcurves)
        for fc in curves:
            for k in fc.keyframe_points:k.interpolation='BEZIER';k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'
for side,sg in [('L',1),('R',-1)]:
    keys(hinges[side],'rotation_euler',[(1,(0,0,0)),(25,(0,0,0)),(97,(math.radians(sg*79),0,0)),(121,(math.radians(sg*79),0,0)),(193,(0,0,0))])
    dep=deploys[side];base=dep.location.copy()
    keys(dep,'location',[(1,tuple(base)),(65,tuple(base)),(97,tuple(base+Vector((0,0,-.18)))),(121,tuple(base+Vector((0,0,-.18)))),(151,tuple(base)),(193,tuple(base))])
keys(rear_lift,'location',[(1,(0,0,0)),(45,(0,0,0)),(85,(0,0,.215)),(121,(0,0,.215)),(161,(0,0,0)),(193,(0,0,0))])
keys(spoiler_lift,'location',[(1,(0,0,0)),(25,(0,0,0)),(55,(0,0,.175)),(165,(0,0,.175)),(193,(0,0,0))])
keys(post,'scale',[(1,(1,1,1)),(25,(1,1,1)),(55,(1,1,2.46)),(165,(1,1,2.46)),(193,(1,1,1))])
keys(post,'location',[(1,(-2.015,0,.9)),(25,(-2.015,0,.9)),(55,(-2.015,0,.9875)),(165,(-2.015,0,.9875)),(193,(-2.015,0,.9))])
for ob,base in guides:
    keys(ob,'scale',[(1,(1,1,.02)),(65,(1,1,.02)),(97,(1,1,1)),(121,(1,1,1)),(151,(1,1,.02)),(193,(1,1,.02))])
    extended=tuple(base+Vector((0,0,-.0882)))
    keys(ob,'location',[(1,tuple(base)),(65,tuple(base)),(97,extended),(121,extended),(151,tuple(base)),(193,tuple(base))])
S.timeline_markers.clear()
for name,fr in [('THK_RoadIdle',1),('THK_RoadToFlight',25),('THK_FlightIdle',97),('THK_FlightToRoad',121),('THK_RoadIdle_End',193)]:S.timeline_markers.new(name,frame=fr)
S.frame_set(1)

# Linked original references, kept outside exports and render visibility.
for i,p in enumerate(sorted((ROOT/'Images reference').glob('*.jpg'))):
    im=bpy.data.images.load(str(p),check_existing=True)
    im.filepath='//Images reference/'+p.name
    ob=bpy.data.objects.new('REF9_'+p.stem,None);REF.objects.link(ob);ob.empty_display_type='IMAGE';ob.data=im;ob.empty_display_size=2
    ob.location=(i%4*2.6-4,-5-i//4*2,1)

# Fixed review setup, kept deliberately neutral across all views.
floor=box('Review_Floor',(0,0,-.06),(200,200,.10),FLOOR,None,.001)
C.objects.unlink(floor);STUDIO.objects.link(floor)
world=bpy.data.worlds.new('THK9_NeutralWorld');S.world=world;world.use_nodes=True
background=next(nd for nd in world.node_tree.nodes if nd.type=='BACKGROUND')
background.inputs['Color'].default_value=(.16,.19,.23,1)
background.inputs['Strength'].default_value=.45
def area(name,loc,power,size):
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
    ob=bpy.data.objects.new(name,data);STUDIO.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector((0,0,.6))-ob.location).to_track_quat('-Z','Y').to_euler()
area('Review_Key',(2,-4,6),1000,5);area('Review_Fill',(-3,3,4),850,4);area('Review_Rim',(-4,-1,5),650,3)
data=bpy.data.cameras.new('THK9_ReviewCamera');camera=bpy.data.objects.new('THK9_ReviewCamera',data);STUDIO.objects.link(camera);S.camera=camera
camera.location=(6,-6,3.6);camera.rotation_euler=(Vector((0,0,.65))-camera.location).to_track_quat('-Z','Y').to_euler();data.lens=55
S.render.engine='CYCLES';S.cycles.samples=32;S.cycles.use_denoising=True
S.render.resolution_x=1400;S.render.resolution_y=1000;S.render.resolution_percentage=100
S.render.image_settings.file_format='PNG';S.view_settings.view_transform='AgX'
for ob in S.objects:ob.select_set(False)
hood.select_set(True);bpy.context.view_layer.objects.active=hood
for screen in bpy.data.screens:
    for ar in screen.areas:
        if ar.type=='VIEW_3D':
            ar.spaces.active.region_3d.view_distance=7.4
            ar.spaces.active.region_3d.view_location=(0,0,.65)
            ar.spaces.active.shading.type='SOLID';ar.spaces.active.shading.color_type='MATERIAL'
S['THK_Version']='V9';S['THK_Stage']='Exterior surfacing rebuild; not final Hero'
S['THK_ReferencePolicy']='Cartoon design primary but not yet visually validated. Supplied Camaro and toy photos inspected.'
bpy.context.view_layer.update()
exec((ROOT/'scripts'/'calibrate_v9_dimensions.py').read_text(encoding='utf-8'),{'calibration_save':False})
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Thunderhawk_V9.blend'),compress=True)
print('THK_V9_BUILD_COMPLETE '+json.dumps({'file':str(ROOT/'Thunderhawk_V9.blend'),'mesh_objects':sum(o.type=='MESH' for o in C.objects),'cockpit':False}))
