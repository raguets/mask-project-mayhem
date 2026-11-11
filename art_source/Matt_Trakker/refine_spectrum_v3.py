"""Rebuild the attached mask from inspected replica photographs, not a cylinder.

Separate mask parts remain bound to the existing character's head bone.
Dimensions/hidden construction are estimates. Run on live V13 via Blender MCP.
"""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
from math import sin,cos,pi,sqrt
P=Path('G:/DEV/mask-project-mayhem');T=P/'art_source/Thunderhawk';s=bpy.context.scene;r=bpy.data.objects['MattTrakker_Rig'];co=bpy.data.collections['Spectrum11_Asset']
for ob in list(co.objects):bpy.data.objects.remove(ob,do_unlink=True)
def mat(n,col,metal,rough):
    m=bpy.data.materials.get(n) or bpy.data.materials.new(n);m.use_nodes=True;m.diffuse_color=(*col,1);p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value=(*col,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
silver=mat('Spectrum3_BrushedSilver',(.40,.46,.49),.86,.29);red=mat('Spectrum3_DeepRedLacquer',(.38,.009,.014),.12,.27)
black=mat('Spectrum3_Rubber',(.005,.007,.009),0,.74);visor=mat('Spectrum3_SmokedVisor',(.004,.014,.025),0,.095)
bs=next(n for n in visor.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['IOR'].default_value=1.52;bs.inputs['Coat Weight'].default_value=.45;bs.inputs['Transmission Weight'].default_value=.12
steel=mat('Spectrum3_VentMetal',(.24,.29,.31),.8,.33)
def mesh(name,vv,ff,material,sub=0,thick=0,bevel=0,smooth=True):
    me=bpy.data.meshes.new(name+'_Editable');me.from_pydata(vv,[],ff);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0000001);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);co.objects.link(ob);me.materials.append(material)
    for f in me.polygons:f.use_smooth=smooth
    if sub:mod=ob.modifiers.new('SurfaceFlow','SUBSURF');mod.levels=sub;mod.render_levels=sub
    if thick:mod=ob.modifiers.new('ShellThickness','SOLIDIFY');mod.thickness=thick
    if bevel:mod=ob.modifiers.new('SoftManufacturedEdges','BEVEL');mod.width=bevel;mod.segments=3
    ob.vertex_groups.new(name='head').add(list(range(len(vv))),1,'REPLACE');mod=ob.modifiers.new('SameMattHeadAttachment','ARMATURE');mod.object=r;ob.parent=r
    for prop in ['hide_render','hide_viewport']:
        d=ob.driver_add(prop).driver;v=d.variables.new();v.name='helmet';v.type='SINGLE_PROP';v.targets[0].id=r;v.targets[0].data_path='["mask_on"]';d.expression='not helmet'
    ob['reference']='Supplied helmet replica photographs images (1).jpg and images (2).jpg, inspected; hidden geometry and dimensions estimated.'
    return ob
def tube(name,pts,rad,material):
    vv=[];ff=[];NN=12
    for j,p in enumerate(pts):
        p=Vector(p);direction=Vector(pts[min(j+1,len(pts)-1)])-Vector(pts[max(0,j-1)]);q=direction.to_track_quat('Z','Y')
        for i in range(NN):vv.append(tuple(p+q@Vector((rad*cos(2*pi*i/NN),rad*sin(2*pi*i/NN),0))))
    for j in range(len(pts)-1):
        for i in range(NN):ff.append((j*NN+i,j*NN+(i+1)%NN,(j+1)*NN+(i+1)%NN,(j+1)*NN+i))
    return mesh(name,vv,ff,material)
def lerp_profile(z,rows,col):
    for j,(a,b) in enumerate(zip(rows,rows[1:])):
        if z<=b[0]:
            t=max(0,min(1,(z-a[0])/(b[0]-a[0])));d=(b[col]-a[col])/(b[0]-a[0]);m0=d if j==0 else (b[col]-rows[j-1][col])/(b[0]-rows[j-1][0]);m1=d if j+2==len(rows) else (rows[j+2][col]-a[col])/(rows[j+2][0]-a[0])
            return (2*t**3-3*t*t+1)*a[col]+(t**3-2*t*t+t)*(b[0]-a[0])*m0+(-2*t**3+3*t*t)*b[col]+(t**3-t*t)*(b[0]-a[0])*m1
    return rows[-1][col]
# Head-shaped section varies in depth, width and forehead rake at every level.
rows=[(1.548,.099,.125,.094),(1.57,.107,.146,.107),(1.61,.115,.151,.122),
      (1.65,.119,.139,.134),(1.70,.120,.130,.137),(1.75,.112,.113,.128),
      (1.79,.102,.100,.114),(1.82,.081,.076,.085),(1.844,.053,.045,.052),(1.858,.001,.001,.001)]
vv=[];ff=[];NN=128;RR=81
for j in range(RR):
    z=1.548+.310*j/(RR-1);w=lerp_profile(z,rows,1);front=lerp_profile(z,rows,2);back=lerp_profile(z,rows,3)
    if z>=1.70:
        dome=sqrt(max(0,1-((z-1.690)/.168)**2));w=.120*dome;front=.130*dome;back=.137*dome
    for i in range(NN):
        a=2*pi*i/NN;c=cos(a);x=-.015+(front*c if c>=0 else back*c);vv.append((x,w*sin(a),z))
for j in range(RR-1):
    for i in range(NN):
        a=2*pi*(i+.5)/NN;z=1.548+.310*(j+.5)/(RR-1)
        if cos(a)>.30 and 1.651<z<1.784:continue
        ff.append((j*NN+i,j*NN+(i+1)%NN,(j+1)*NN+(i+1)%NN,(j+1)*NN+i))
mesh('Spectrum_SilverHelmetShell',vv,ff,silver,sub=1,thick=.003)

# Lens is swept across the face with tapered bottom and a raised nose clearance.
vv=[];ff=[];NN=65;RR=25
for j in range(RR):
    t=j/(RR-1)
    for i in range(NN):
        u=-1+2*i/(NN-1);width=.102-.010*(1-t);y=width*u
        bottom=1.655+.029*math.exp(-(u/.30)**2)+.013*abs(u)**3;top=1.784-.010*abs(u)**2
        z=bottom*(1-t)+top*t;x=.144-.059*abs(u)**1.8-.009*t+.002*sin(pi*t)
        vv.append((x,y,z))
for j in range(RR-1):
    for i in range(NN-1):ff.append((j*NN+i,j*NN+i+1,(j+1)*NN+i+1,(j+1)*NN+i))
mesh('Spectrum_WraparoundVisor',vv,ff,visor,sub=1,thick=.002)
for edge in ['top','bottom']:
    pts=[]
    for i in range(65):
        u=-1+2*i/64;t=1 if edge=='top' else 0;width=.102-.010*(1-t)
        bottom=1.655+.029*math.exp(-(u/.30)**2)+.013*abs(u)**3;top=1.784-.010*abs(u)**2
        pts.append((.144-.059*abs(u)**1.8-.009*t+.001,width*u,bottom*(1-t)+top*t))
    tube('Spectrum_VisorGasket_'+edge,pts,.002,black)

# Red brow has a distinct inclined front plane and angular temple returns.
vv=[];ff=[];NN=33
for j in range(4):
    t=j/3
    for i in range(NN):
        u=-1+2*i/(NN-1);vv.append((.158-.072*abs(u)**2-.034*t,(.120-.009*t)*u,1.782+.048*t-.010*abs(u)**2))
for j in range(3):
    for i in range(NN-1):ff.append((j*NN+i,j*NN+i+1,(j+1)*NN+i+1,(j+1)*NN+i))
mesh('Spectrum_RedSweptBrow',vv,ff,red,thick=.007,bevel=.002)
for sg,sd in [(1,'L'),(-1,'R')]:
    outer=[(.052,sg*.111,1.820),(.086,sg*.120,1.782),(.087,sg*.104,1.749),(.083,sg*.104,1.686),(.055,sg*.113,1.648)]
    inner=[(.012,sg*.115,1.795),(.035,sg*.123,1.772),(.025,sg*.122,1.742),(.015,sg*.123,1.691),(.012,sg*.117,1.662)]
    pts=outer+inner
    mesh('Spectrum_TempleGuard_'+sd,pts,[(i,i+1,i+6,i+5) for i in range(4)],red,thick=.006,bevel=.0015,smooth=False)
    # Lower cheeks converge into the respirator rather than parallel cylinder walls.
    vv=[(.040,sg*.111,1.663),(.084,sg*.099,1.656),(.139,sg*.056,1.639),(.151,sg*.046,1.586),(.118,sg*.077,1.565),(.035,sg*.097,1.558),(.003,sg*.108,1.594)]
    # Fan adds a convex pressed surface, avoids a single flat polygon across the jaw.
    center=(.092,sg*.085,1.612);verts=vv+[center];faces=[(i,(i+1)%len(vv),len(vv)) for i in range(len(vv))]
    # The lower cheek is now part of the continuous silver shell: no intersecting overlay.
    # Thin vertical rear vent observed in the side photograph.
    vv=[(-.073,sg*.103,1.565),(-.062,sg*.108,1.567),(-.061,sg*.111,1.608),(-.072,sg*.106,1.607)]
    mesh('Spectrum_RearVent_'+sd,vv,[(0,1,2,3)],black,thick=.001)

# Raised rounded-triangular respirator with a nose ridge and inset vent slats.
outline=[(0,1.713),(-.017,1.691),(-.038,1.643),(-.048,1.593),(-.042,1.576),
         (-.025,1.570),(.025,1.570),(.042,1.576),(.048,1.593),(.038,1.643),(.017,1.691)]
vv=[];ff=[];NN=len(outline)
for scale,depth in [(1.08,.129),(1.0,.151),(.91,.174),(.80,.181)]:
    for y,z in outline:
        # Forward ridge is most prominent around the nose, raking back at chin.
        x=depth+.009*math.exp(-((z-1.667)/.043)**2)-.010*max(0,(1.60-z)/.04)
        vv.append((x,y*scale,1.635+(z-1.635)*scale))
for j in range(3):
    for i in range(NN):ff.append((j*NN+i,j*NN+(i+1)%NN,(j+1)*NN+(i+1)%NN,(j+1)*NN+i))
ff.append(tuple(3*NN+i for i in range(NN)))
mesh('Spectrum_RespiratorHousing',vv,ff,silver,sub=1)
# Grille is a tapered inset, not a rectangular block stuck on the mask.
vv=[(.183,-.030,1.583),(.183,.030,1.583),(.191,.023,1.641),(.191,-.023,1.641)]
mesh('Spectrum_RespiratorDarkGrille',vv,[(0,1,2,3)],black,thick=.001,bevel=.002)
for i in range(8):
    z=1.588+i*.0066;width=.029-.006*(i/7);x=.184+(z-1.583)/.058*.008
    tube('Spectrum_GrilleLouver_'+str(i),[(x+.001,-width,z),(x+.002,0,z+.0003),(x+.001,width,z)],.0011,steel)

# Broad oval double lip follows a tapered collar instead of a round cylinder.
for label,base,rx,ry in [('Lower',1.528,.120,.127),('Upper',1.548,.113,.120)]:
    vv=[];ff=[];NN=128;RR=12
    for j in range(RR):
        b=2*pi*j/RR
        for i in range(NN):
            a=2*pi*i/NN;rad=.012*cos(b);vv.append((-.015+(rx+rad)*cos(a),(ry+rad)*sin(a),base+.012*sin(b)+.004*max(0,cos(a))))
    for j in range(RR):
        for i in range(NN):ff.append((j*NN+i,j*NN+(i+1)%NN,((j+1)%RR)*NN+(i+1)%NN,((j+1)%RR)*NN+i))
    mesh('Spectrum_DoubleRedNeckSeal_'+label,vv,ff,red)
vv=[];ff=[];NN=128
for j in range(9):
    t=j/8
    for i in range(NN):
        a=2*pi*i/NN;vv.append((-.015+(.120-.014*t)*cos(a),(.127-.019*t)*sin(a),1.526+.035*t+.004*max(0,cos(a))))
for j in range(8):
    for i in range(NN):ff.append((j*NN+i,j*NN+(i+1)%NN,(j+1)*NN+(i+1)%NN,(j+1)*NN+i))
mesh('Spectrum_NeckSealConnectingBody',vv,ff,red,thick=.003)
r['mask_on']=True;r['driving_pose']=1;r.location=(0,.4,0);r.update_tag();s.frame_set(97);bpy.context.view_layer.update()
s['Spectrum_V3']='Head-shaped domed shell; raked brow; tapered cheeks; triangular respirator. From supplied replica photographs; unshown geometry estimated.'
bpy.ops.wm.save_as_mainfile(filepath=str(T/'Thunderhawk_V13.blend'),compress=True)
print('SPECTRUM_V3_PHOTO_SHAPES_SAVED',len(co.objects))
