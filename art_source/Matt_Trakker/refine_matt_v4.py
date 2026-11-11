"""Human interpretation of the supplied portrait, authorized 2026-11-02.

Edits the existing character, head object and skinned suit. No pose variants or
replacement character instances are created. Run on the V13 assembly via MCP.
"""
import bpy,bmesh,math,random,json
from pathlib import Path
from mathutils import Vector
from math import sin,cos,pi,exp,sqrt
P=Path('G:/DEV/mask-project-mayhem');T=P/'art_source/Thunderhawk';A=P/'art_source/Matt_Trakker'
s=bpy.context.scene;r=bpy.data.objects['MattTrakker_Rig'];char=bpy.data.collections['MT11_Character']
backup=T/'Thunderhawk_V13_before_character_refinement.blend'
if not backup.exists():bpy.ops.wm.save_as_mainfile(filepath=str(backup),copy=True,compress=True)
r['driving_pose']=0;r['mask_on']=False;r.location=(0,0,0);r.update_tag();s.frame_set(1);bpy.context.view_layer.update()
head=bpy.data.objects['MT_Head_AnatomicalSurface'];original_head_pointer=head.as_pointer();suit=bpy.data.objects['MT_ContinuousFlightSuit'];suit_pointer=suit.as_pointer()
for ob in list(char.objects):
    if ob==head:continue
    if ob.name.startswith(('MT_Eye','MT_Iris','MT_Pupil','MT_Brow','MT_Ear','MT_Concha','MT_Nostril','MT_Nasolabial','MT_Lip_','MT_Mouth','MT_Philtrum','MT_Hair','MT_Sideburn','MT_Lash','MT_Cornea')) or ob.name=='MT_Neck':
        bpy.data.objects.remove(ob,do_unlink=True)

def mat(name,col,rough=.5):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*col,1)
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough
    return m
skin=mat('MT4_Skin',(.57,.345,.235),.46);lip=mat('MT4_Lips',(.34,.16,.12),.47)
crease=mat('MT4_SoftCreases',(.18,.075,.045),.65);hair=mat('MT4_NaturalBlond',(.20,.105,.027),.55)
hairlight=mat('MT4_BlondVariation',(.32,.185,.055),.58);browmat=mat('MT4_BrowHair',(.105,.052,.014),.7)
white=mat('MT4_Sclera',(.58,.61,.59),.22);pupil=mat('MT4_Pupil',(.0006,.001,.0012),.18)
iris=mat('MT4_IrisFibers',(.035,.105,.13),.3)
for material in [skin,lip]:
    p=next(n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Subsurface Weight'].default_value=.13;p.inputs['Subsurface Scale'].default_value=.003;p.inputs['Subsurface Radius'].default_value=(1,.45,.25)
ns=skin.node_tree.nodes;ls=skin.node_tree.links;bs=next(n for n in ns if n.type=='BSDF_PRINCIPLED')
noise=ns.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=210;noise.inputs['Detail'].default_value=3
bump=ns.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.00018;bump.inputs['Strength'].default_value=.18;ls.new(noise.outputs['Fac'],bump.inputs['Height']);ls.new(bump.outputs[0],bs.inputs['Normal'])
colornoise=ns.new('ShaderNodeTexNoise');colornoise.inputs['Scale'].default_value=32;colornoise.inputs['Detail'].default_value=2
ramp=ns.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.18;ramp.color_ramp.elements[0].color=(.46,.255,.17,1);ramp.color_ramp.elements[1].position=.82;ramp.color_ramp.elements[1].color=(.62,.38,.265,1)
ls.new(colornoise.outputs['Fac'],ramp.inputs[0]);ls.new(ramp.outputs[0],bs.inputs['Base Color'])
attribute=iris.node_tree.nodes.new('ShaderNodeVertexColor');attribute.layer_name='IrisColor';iris.node_tree.links.new(attribute.outputs['Color'],next(n for n in iris.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'])
cornea=bpy.data.materials.new('MT4_ClearCornea');cornea.use_nodes=True;cornea.node_tree.nodes.clear();g=cornea.node_tree.nodes.new('ShaderNodeBsdfGlass');g.inputs['IOR'].default_value=1.376;g.inputs['Roughness'].default_value=.012;o=cornea.node_tree.nodes.new('ShaderNodeOutputMaterial');cornea.node_tree.links.new(g.outputs[0],o.inputs['Surface'])

def mesh(name,vv,ff,material,bone='head',sub=0,reuse=None,weights=None):
    if reuse:
        ob=reuse;me=ob.data;me.clear_geometry();ob.vertex_groups.clear()
        for m in list(ob.modifiers):ob.modifiers.remove(m)
    else:
        me=bpy.data.meshes.new(name+'_Editable');ob=bpy.data.objects.new(name,me);char.objects.link(ob)
    me.from_pydata(vv,[],ff);me.update();me.materials.clear();me.materials.append(material)
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
    for f in me.polygons:f.use_smooth=True
    if sub:mod=ob.modifiers.new('AnatomicalSurface','SUBSURF');mod.levels=sub;mod.render_levels=sub
    if weights:
        groups={name:ob.vertex_groups.new(name=name) for name in set(k for w in weights for k in w)}
        for i,w in enumerate(weights):
            for k,val in w.items():
                if val>1e-5:groups[k].add([i],val,'REPLACE')
    else:ob.vertex_groups.new(name=bone).add(list(range(len(vv))),1,'REPLACE')
    mod=ob.modifiers.new('SameMattSkin','ARMATURE');mod.object=r;mod.use_deform_preserve_volume=True;ob.parent=r
    return ob
def curve(name,pts,radius,material,bone='head'):
    data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.bevel_depth=radius;data.bevel_resolution=2;data.resolution_u=2
    spl=data.splines.new('POLY');spl.points.add(len(pts)-1)
    for p,co in zip(spl.points,pts):p.co=(*co,1)
    ob=bpy.data.objects.new(name,data);char.objects.link(ob);data.materials.append(material)
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH');ob=bpy.context.object
    ob.vertex_groups.new(name=bone).add(list(range(len(ob.data.vertices))),1,'REPLACE');mod=ob.modifiers.new('SameMattSkin','ARMATURE');mod.object=r;ob.parent=r;return ob
def ell(name,center,rad,material,bone='head'):
    vv=[];ff=[];N=48;Z=25
    for j in range(Z):
        a=-pi/2+pi*j/(Z-1)
        for i in range(N):
            b=2*pi*i/N;vv.append((center[0]+rad[0]*cos(a)*cos(b),center[1]+rad[1]*cos(a)*sin(b),center[2]+rad[2]*sin(a)))
    for j in range(Z-1):
        for i in range(N):ff.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
    return mesh(name,vv,ff,material,bone)
def profile(z,table):
    if z<=table[0][0]:return table[0][1]
    for j,((a,x),(b,y)) in enumerate(zip(table,table[1:])):
        if z<=b:
            t=(z-a)/(b-a);d=(y-x)/(b-a);m0=d if j==0 else (y-table[j-1][1])/(b-table[j-1][0]);m1=d if j+2==len(table) else (table[j+2][1]-x)/(table[j+2][0]-a)
            return (2*t**3-3*t*t+1)*x+(t**3-2*t*t+t)*(b-a)*m0+(-2*t**3+3*t*t)*y+(t**3-t*t)*(b-a)*m1
    return table[-1][1]
WT=[(1.574,.014),(1.585,.040),(1.602,.059),(1.623,.069),(1.653,.073),(1.684,.075),(1.713,.071),(1.75,.073),(1.78,.063),(1.8,.039),(1.817,.001)]
FT=[(1.574,.025),(1.585,.061),(1.603,.073),(1.627,.064),(1.652,.062),(1.681,.063),(1.703,.068),(1.724,.075),(1.754,.073),(1.785,.057),(1.805,.033),(1.817,.001)]
BT=[(1.574,.029),(1.60,.048),(1.64,.079),(1.69,.091),(1.73,.089),(1.76,.079),(1.80,.046),(1.817,.001)]
def headpoint(z,a):
    ca=cos(a);yy=profile(z,WT)*sin(a);x=-.008+(profile(z,FT)*max(0,ca)**.70 if ca>=0 else profile(z,BT)*ca)
    front=max(0,ca)**6
    detail=.030*exp(-((z-1.669)/.010)**2-(yy/.0095)**2)+.017*exp(-((z-1.698)/.027)**2-(yy/.008)**2)
    detail+=.010*exp(-((z-1.664)/.006)**2-((abs(yy)-.0115)/.006)**2)
    detail-=.008*exp(-((z-1.706)/.012)**2-((abs(yy)-.032)/.016)**2)
    detail+=.006*exp(-((z-1.720)/.008)**2-((abs(yy)-.031)/.022)**2)
    detail+=.009*exp(-((z-1.681)/.013)**2-((abs(yy)-.046)/.017)**2)
    detail-=.004*exp(-((z-1.649)/.019)**2-((abs(yy)-.050)/.018)**2)
    detail+=.004*exp(-((z-1.614)/.014)**2-((abs(yy)-.059)/.014)**2)
    detail+=.0025*exp(-((z-1.593)/.010)**2-(yy/.025)**2)
    detail-=.0020*exp(-((z-1.648)/.009)**2-(yy/.003)**2)
    return (x+detail*front+.00022*sin(yy*93+z*31)*front,yy,z)
def face_at(y,z):return headpoint(z,math.asin(max(-.999,min(.999,y/max(.001,profile(z,WT))))))[0]
vv=[];ff=[];N=192;Z=169
for j in range(Z):
    z=1.574+(1.817-1.574)*j/(Z-1)
    for i in range(N):vv.append(headpoint(z,2*pi*i/N))
for j in range(Z-1):
    for i in range(N):
        ids=(j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i);mid=sum((Vector(vv[k]) for k in ids),Vector())/4
        # Real apertures allow the spherical eyes/corneas to sit inside the head.
        if mid.x>.030 and ((abs(mid.y)-.032)/.0138)**2+((mid.z-1.706)/.0048)**2<1:continue
        ff.append(ids)
ff.append(tuple(range(N-1,-1,-1)));ff.append(tuple((Z-1)*N+i for i in range(N)))
mesh('MT_Head_AnatomicalSurface',vv,ff,skin,reuse=head,sub=1)

random.seed(404)
for sg,sd in [(1,'L'),(-1,'R')]:
    ey=sg*.032;ez=1.706;re=.0135;ex=face_at(ey,ez)-.0108
    ell('MT_Eyeball_'+sd,(ex,ey,ez),(re,re,re),white)
    for label,rad,material,offset in [('Iris',.0055,iris,.00012),('Pupil',.00215,pupil,.00019),('Cornea',.0065,cornea,.00045)]:
        vv=[];ff=[];NN=96;RR=13
        for j in range(RR):
            rho=rad*j/(RR-1)
            for i in range(NN):
                a=2*pi*i/NN;xx=ex+sqrt(max(0,re*re-rho*rho))+offset
                if label=='Cornea':xx+=.00055*(1-(rho/rad)**2)
                vv.append((xx,ey+rho*cos(a),ez+rho*sin(a)))
        for j in range(RR-1):
            for i in range(NN):ff.append((j*NN+i,j*NN+(i+1)%NN,(j+1)*NN+(i+1)%NN,(j+1)*NN+i))
        ob=mesh('MT_'+label+'_'+sd,vv,ff,material)
        if label=='Iris':
            attr=ob.data.color_attributes.new(name='IrisColor',type='FLOAT_COLOR',domain='POINT')
            for i,v in enumerate(ob.data.vertices):
                yy=v.co.y-ey;zz=v.co.z-ez;rho=sqrt(yy*yy+zz*zz)/rad;a=math.atan2(zz,yy);grain=.5+.5*sin(a*67+sin(a*17)*2+rho*7)
                edge=max(0,min(1,(1-rho)*9));val=(.45+.55*grain)*(.4+.6*edge)
                attr.data[i].color=(.035*val,.115*val,.14*val,1)
    contour=[]
    for upper in [True,False]:
        us=[-1+2*i/64 for i in range(65)] if upper else [1-2*i/64 for i in range(1,64)]
        for u in us:
            contour.append((u,(.0054 if upper else -.0041)*max(0,1-u*u)**.65+.0007*u*sg))
    vv=[];ff=[];NN=len(contour)
    for j in range(7):
        t=j/6
        for u,dz in contour:
            yy=ey+.014*u*(1+.42*t);zz=ez+dz*(1+1.25*t)+(.0015*t if dz>0 else -.0008*t)
            rr=(.014*u)**2+dz*dz;xx=ex+sqrt(max(.0000001,re*re-rr))+.00025
            corner=abs(u)**8;xx=xx*(1-corner)+(face_at(ey+.014*u,ez+dz)+.0002)*corner
            xx=xx*(1-t)+(face_at(yy,zz)+.00015)*t+.00045*sin(pi*t)
            vv.append((xx,yy,zz))
    for j in range(6):
        for i in range(NN):ff.append((j*NN+i,j*NN+(i+1)%NN,(j+1)*NN+(i+1)%NN,(j+1)*NN+i))
    mesh('MT_EyelidSkin_'+sd,vv,ff,skin,sub=1)
    pts=[]
    for j in range(41):
        u=-.93+1.86*j/40;yy=ey+.0148*u;zz=ez+.0090*sqrt(max(0,1-u*u))+.001
        pts.append((face_at(yy,zz)+.0003,yy,zz))
    curve('MT_EyelidCrease_'+sd,pts,.00016,lip)
    for k in range(130):
        u=random.random();yy=ey+(-.021+.042*u);zz=1.720+.0038*sin(pi*u)+random.uniform(-.0013,.0013);length=random.uniform(.002,.004)
        pts=[]
        for j in range(4):
            t=j/3;y=yy+sg*length*.55*t;z=zz+length*(t-.35*t*t);pts.append((face_at(y,z)+.00018+.00012*sin(pi*t),y,z))
        curve('MT_BrowFiber_'+sd+str(k),pts,random.uniform(.00007,.00012),browmat)
    # Ear pinna has a skin surface with a recessed concha, not wire loops.
    vv=[];ff=[];NN=64;RR=13
    for j in range(RR):
        rho=j/(RR-1)
        for i in range(NN):
            a=2*pi*i/NN;xx=-.019+.013*cos(a)*rho+.003*sin(a);zz=1.676+.027*sin(a)*rho
            ridge=.006*exp(-((rho-.82)/.15)**2);yy=sg*(.076+.003*rho+ridge-.002*(1-rho))
            vv.append((xx,yy,zz))
    for j in range(RR-1):
        for i in range(NN):ff.append((j*NN+i,j*NN+(i+1)%NN,(j+1)*NN+(i+1)%NN,(j+1)*NN+i))
    ob=mesh('MT_EarPinna_'+sd,vv,ff,skin,sub=1);wall=ob.modifiers.new('PinnaThickness','SOLIDIFY');wall.thickness=.002
    ell('MT_EarTragus_'+sd,(-.007,sg*.079,1.674),(.004,.004,.007),skin)
    x=face_at(sg*.0105,1.660)
    ell('MT_Nostril_'+sd,(x+.0004,sg*.0105,1.661),(.0016,.0026,.0010),crease)

# Lips blend back into the actual face surface at their outer border.
for upper in [True,False]:
    vv=[];ff=[];NN=81;RR=9
    for j in range(RR):
        t=j/(RR-1)
        for i in range(NN):
            u=-1+2*i/(NN-1);yy=.024*u;mid=1.636+.0009*cos(pi*u)-.0011*exp(-(u/.2)**2)
            height=(.0033 if upper else -.0048)*max(0,1-u*u)**.7;z=mid+height*t
            swell=(.0018 if upper else .0028)*sin(pi*t)*max(0,1-u*u)
            x=face_at(yy,z)+.0003+swell+.0010*(1-t)*(1-u*u);vv.append((x,yy,z))
    for j in range(RR-1):
        for i in range(NN-1):ff.append((j*NN+i,j*NN+i+1,(j+1)*NN+i+1,(j+1)*NN+i))
    mesh('MT_Lip_'+str(upper),vv,ff,lip,sub=1)
pts=[]
for i in range(65):
    u=-1+2*i/64;y=.024*u;z=1.636+.0009*cos(pi*u)-.0011*exp(-(u/.2)**2);pts.append((face_at(y,z)+.00055+.001*(1-u*u),y,z))
curve('MT_MouthCrease',pts,.00022,crease)

# Continuous neck with tendon mass flowing into jaw and cloth collar.
vv=[];ff=[];ww=[];NN=96;RR=41
for j in range(RR):
    z=1.468+.129*j/(RR-1);t=j/(RR-1);rad=profile(z,[(1.468,.046),(1.49,.043),(1.535,.035),(1.575,.037),(1.597,.043)])
    for i in range(NN):
        a=2*pi*i/NN;tendon=.0022*exp(-((abs(sin(a))-.55)/.2)**2)*sin(pi*t)
        vv.append((-.015+(rad+tendon)*cos(a),rad*sin(a),z));h=max(0,min(.85,(z-1.545)/.061));ww.append({'neck':1-h,'head':h})
for j in range(RR-1):
    for i in range(NN):ff.append((j*NN+i,j*NN+(i+1)%NN,(j+1)*NN+(i+1)%NN,(j+1)*NN+i))
mesh('MT_Neck',vv,ff,skin,sub=1,weights=ww)

# Groom follows the new head and has irregular roots and short directional fibers.
def hairbase(a):
    front=max(0,cos(a));temple=exp(-((abs(a)-.8)/.30)**2)
    return 1.700+.059*front**2+.008*temple+.0008*sin(a*13)
def hairpt(t,a):
    z=hairbase(a)+(1.820-hairbase(a))*sin(t*pi/2);x,y,_=headpoint(min(z,1.8165),a)
    off=.0022+.0018*sin(pi*t);return(x+off*cos(a),y+off*sin(a),z+.0008*sin(a)*sin(pi*t))
vv=[];ff=[];NN=128;RR=45
for j in range(RR):
    for i in range(NN):vv.append(hairpt(j/(RR-1),-pi+2*pi*i/NN))
for j in range(RR-1):
    for i in range(NN):ff.append((j*NN+i,j*NN+(i+1)%NN,(j+1)*NN+(i+1)%NN,(j+1)*NN+i))
cap=mesh('MT_Hair_NaturalSidePart',vv,ff,hair,sub=1)
for k in range(520):
    a=random.uniform(-pi,pi);root=random.uniform(.005,.7);length=random.uniform(.10,.32);pts=[]
    for j in range(9):
        t=min(.96,root+length*j/8);sweep=.23*sin(pi*t)*(-1 if sin(a)<-.25 else 1);x,y,z=hairpt(t,a+sweep)
        pts.append((x+.00014*cos(a),y+.00014*sin(a),z+.00015))
    curve('MT_HairFiber_'+str(k),pts,random.uniform(.00007,.00014),hairlight if k%5==0 else hair)
for ob in char.objects:
    if ob.name.startswith('MT_Hair'):
        for prop in ['hide_render','hide_viewport']:
            d=ob.driver_add(prop).driver;v=d.variables.new();v.name='helmet';v.type='SINGLE_PROP';v.targets[0].id=r;v.targets[0].data_path='["mask_on"]';d.expression='helmet'

# Refine the same weighted cloth sculpt: soften shoulder-ball silhouettes and
# introduce restrained localized cloth compression instead of uniform tubes.
bone_names={g.index:g.name for g in suit.vertex_groups}
for v in suit.data.vertices:
    p=v.co.copy();y=abs(p.y);shoulder=exp(-((y-.195)/.068)**2-((p.z-1.439)/.065)**2)
    if p.z>1.395 and y>.125:v.co.z-=.019*shoulder;v.co.x*=1-.10*shoulder
    if y<.16 and p.x>0:
        chest=.007*exp(-((p.z-1.355)/.055)**2-((y-.085)/.07)**2)
        waist=.004*exp(-((p.z-1.16)/.08)**2);v.co.x+=chest-waist
    group=max(v.groups,key=lambda g:g.weight) if v.groups else None
    name=bone_names.get(group.group,'') if group else ''
    if name.startswith(('upper_arm.','forearm.','thigh.','shin.')):
        b=r.data.bones[name];a=b.head_local;direction=b.tail_local-a;u=max(0,min(1,(p-a).dot(direction)/direction.length_squared));center=a+direction*u;off=p-center
        if off.length>1e-6:
            if name.startswith('upper_arm'):shrink=.05*exp(-((u-.1)/.3)**2)+.07*exp(-((u-.95)/.19)**2)
            elif name.startswith('forearm'):shrink=.055*exp(-((u-.05)/.19)**2)
            else:shrink=0
            wrinkle=.0008*sin(u*42+math.atan2(off.y,off.x)*2)*exp(-((u-.15)/.23)**2)
            v.co+=off.normalized()*(wrinkle-off.length*shrink)
suit.data.update()
# Reduce hard accessory-block thickness, retaining the original weighted pieces.
for ob in char.objects:
    if ob.type=='MESH' and ob.name.startswith(('MT_KneePatch_','MT_CargoPocket_','MT_PocketFlap_')):
        xs=[v.co.x for v in ob.data.vertices];base=min(xs)
        for v in ob.data.vertices:v.co.x=base+(v.co.x-base)*(.28 if 'Knee' in ob.name else .60)
    if ob.name.startswith(('MT_ArmBand_','MT_Cuff_')):
        for v in ob.data.vertices:
            sd='L' if v.co.y>0 else 'R';bn='upper_arm.'+sd if 'ArmBand' in ob.name else 'forearm.'+sd;b=r.data.bones[bn]
            q=b.tail_local-b.head_local;u=(v.co-b.head_local).dot(q)/q.length_squared;c=b.head_local+q*u;v.co=c+(v.co-c)*.95
assert head.as_pointer()==original_head_pointer and suit.as_pointer()==suit_pointer
r['asset_version']='Matt Trakker V4 / Spectrum V3';r['reference_fidelity']='Human interpretation of supplied illustrated portrait explicitly authorized 2026-11-02. No likeness to a specific real person.'
r['driving_pose']=1;r['mask_on']=False;r.location=(0,.4,0);r.update_tag();s.frame_set(97);bpy.context.view_layer.update()
s['Matt_Realism_Authorization']='2026-11-02: realistic human interpretation of supplied cartoon portrait, no particular real person.'
bpy.ops.wm.save_as_mainfile(filepath=str(T/'Thunderhawk_V13.blend'),compress=True)
print('MATT_V4_SAME_HEAD_AND_SUIT_REFINED')
