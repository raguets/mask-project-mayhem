"""Adapt generic CC0 anatomy to the existing Matt rig and character objects.

Human interpretation authorized by user 2026-11-02, no specific-person likeness.
Head source: Blender Human Base Meshes animation head. Hands: Dan Ulrich CC0.
The same Matt head object, suit, armature and two controls are retained.
"""
import bpy,bmesh,math,random,json
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
from mathutils.bvhtree import BVHTree
from math import sin,cos,pi,sqrt
P=Path('G:/DEV/mask-project-mayhem');T=P/'art_source/Thunderhawk';A=P/'art_source/Matt_Trakker'
s=bpy.context.scene;r=bpy.data.objects['MattTrakker_Rig'];char=bpy.data.collections['MT11_Character'];head=bpy.data.objects['MT_Head_AnatomicalSurface']
backup=T/'Thunderhawk_V13_before_anatomical_fit.blend'
if not backup.exists():bpy.ops.wm.save_as_mainfile(filepath=str(backup),copy=True,compress=True)
r['driving_pose']=0;r['mask_on']=False;r.location=(0,0,0);r.update_tag();s.frame_set(1);bpy.context.view_layer.update()
def geo(ob):
    ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();vv=[ev.matrix_world@v.co for v in me.vertices];ff=[tuple(f.vertices) for f in me.polygons];ev.to_mesh_clear();return vv,ff
def transform(p):
    x=-p.y-.035;y=p.x-1.46257198;z=p.z+.93930
    y*=1+.065*math.exp(-((z-1.600)/.024)**2)
    x+=.003*math.exp(-((z-1.60)/.021)**2-(y/.034)**2)
    return Vector((x,y,z))
def install(ob,vv,ff,material,bone='head',neck=False):
    for m in list(ob.modifiers):ob.modifiers.remove(m)
    ob.vertex_groups.clear();me=ob.data;me.clear_geometry();me.from_pydata(vv,[],ff);me.update();me.materials.clear();me.materials.append(material)
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
    for f in me.polygons:f.use_smooth=True
    if neck:
        ghead=ob.vertex_groups.new(name='head');gn=ob.vertex_groups.new(name='neck')
        for v in me.vertices:
            w=max(0,min(1,(v.co.z-1.535)/.065));w=w*w*(3-2*w)
            if w>0:ghead.add([v.index],w,'REPLACE')
            if w<1:gn.add([v.index],1-w,'REPLACE')
    else:ob.vertex_groups.new(name=bone).add(list(range(len(vv))),1,'REPLACE')
    mod=ob.modifiers.new('AnatomicalSurface','SUBSURF');mod.levels=1;mod.render_levels=1
    mod=ob.modifiers.new('SameMattRig','ARMATURE');mod.object=r;mod.use_deform_preserve_volume=True;ob.parent=r
def newmesh(name,vv,ff,mat,bone):
    me=bpy.data.meshes.new(name+'_Editable');ob=bpy.data.objects.new(name,me);char.objects.link(ob);install(ob,vv,ff,mat,bone);return ob
src=bpy.data.objects['GEO-head_animation_realistic'];vv,ff=geo(src);vv=[transform(v) for v in vv]
# The source neck is integrated into this same head mesh; lower boundary tucks into collar.
ff=[f for f in ff if all(vv[i].z>1.473 for i in f)]
old_pointer=head.as_pointer();install(head,vv,ff,bpy.data.materials['MT4_Skin'],neck=True);assert head.as_pointer()==old_pointer
head['anatomy_source']='Blender Human Base Meshes v1.2.0 animation head, CC0; adapted proportions, jaw and portrait styling. Source bundle retained.'
for ob in list(char.objects):
    if ob==head:continue
    if ob.name.startswith(('MT_Eye','MT_Iris','MT_Pupil','MT_Cornea','MT_Brow','MT_Ear','MT_Concha','MT_Nostril','MT_Nasolabial','MT_Lip_','MT_Mouth','MT_Philtrum')) or ob.name=='MT_Neck':bpy.data.objects.remove(ob,do_unlink=True)
for sd in ['L','R']:
    for part,newname,mat in [('sclera','MT_Eyeball_',bpy.data.materials['MT4_Sclera']),('iris','MT_Iris_',bpy.data.materials['MT4_IrisFibers'])]:
        source=bpy.data.objects['GEO-head_animation_realistic.'+part+'.'+sd];vv,ff=geo(source);vv=[transform(v) for v in vv];ob=newmesh(newname+sd,vv,ff,mat,'head')
        if part=='iris':
            me=ob.data;me.materials.append(bpy.data.materials['MT4_Pupil']);center=sum(vv,Vector())/len(vv)
            attr=me.color_attributes.new(name='IrisColor',type='FLOAT_COLOR',domain='POINT')
            maxr=max(sqrt((v.y-center.y)**2+(v.z-center.z)**2) for v in vv)
            for v in me.vertices:
                yy=v.co.y-center.y;zz=v.co.z-center.z;rho=sqrt(yy*yy+zz*zz)/maxr;a=math.atan2(zz,yy);grain=.65+.35*sin(a*53+rho*7)
                attr.data[v.index].color=(.035*grain,.115*grain,.145*grain,1)
            for f in me.polygons:
                centerp=f.center
                if sqrt((centerp.y-center.y)**2+(centerp.z-center.z)**2)<.0022:f.material_index=1
# Natural lip tint follows a narrow mouth region of the anatomical surface.
me=head.data;me.materials.append(bpy.data.materials['MT4_Lips'])
for f in me.polygons:
    p=f.center
    if p.x>.077 and abs(p.y)<.026 and 1.626<p.z<1.644:f.material_index=1

# Build a scalp from ray intersections with the anatomical skull, then regenerate the groom.
ev=head.evaluated_get(bpy.context.evaluated_depsgraph_get());hme=ev.to_mesh();hv=[Vector(v.co) for v in hme.vertices];hf=[tuple(f.vertices) for f in hme.polygons];ev.to_mesh_clear();tree=BVHTree.FromPolygons(hv,hf)
top=max(v.z for v in hv);cap=bpy.data.objects['MT_Hair_NaturalSidePart'];N=128;Z=45
for j in range(Z):
    t=j/(Z-1)
    for i in range(N):
        a=-pi+2*pi*i/N;base=1.707+.052*max(0,cos(a))**2+.006*math.exp(-((abs(a)-.8)/.3)**2)
        z=base+(top+.002-base)*sin(t*pi/2);zs=min(top-.00015,z);origin=Vector((-.012,0,zs));direction=Vector((cos(a),sin(a),0))
        p,normal,idx,dist=tree.ray_cast(origin,direction,.3)
        if p is None:
            p=Vector((-.012,0,zs));p+=direction*.001
        p+=direction*.002;p.z=z
        if t>.98:p.x=-.012+(p.x+.012)*(1-(t-.98)/.02);p.y*=1-(t-.98)/.02
        cap.data.vertices[j*N+i].co=p
cap.data.update()
old=bpy.data.objects.get('MT_Hair_DenseGroom')
if old:bpy.data.objects.remove(old,do_unlink=True)
# Reuse the reviewed dense-groom construction with the new scalp coordinates.
source=(A/'correct_matt_v4_review.py').read_text();groom=source[source.index('def scalp(t,a):'):source.index("r['driving_pose']=1")];me=cap.data;exec(groom)

# Combined eyebrow fibers are fitted to the anatomical brow surface.
vv=[];ff=[];random.seed(316)
for sg in [1,-1]:
    for k in range(170):
        u=random.random();y=sg*(.012+.039*u);z=1.723+.003*sin(pi*u)+random.uniform(-.0012,.0012);length=random.uniform(.002,.0037);off=len(vv)
        for j in range(5):
            t=j/4;yy=y+sg*length*.5*t;zz=z+length*(t-.35*t*t);p,normal,idx,d=tree.ray_cast(Vector((.25,yy,zz)),Vector((-1,0,0)),.5)
            if p is None:p=Vector((.06,yy,zz))
            p.x+=.00025
            for q in range(4):
                angle=2*pi*q/4;vv.append(tuple(p+Vector((.000055*cos(angle),.000055*sin(angle),0))))
        for j in range(4):
            for q in range(4):ff.append((off+j*4+q,off+j*4+(q+1)%4,off+(j+1)*4+(q+1)%4,off+(j+1)*4+q))
newmesh('MT_Brow_NaturalFibers',vv,ff,bpy.data.materials['MT4_BrowHair'],'head')

# Anatomical glove meshes replace disconnected visible finger/palm pieces.
source=bpy.data.objects['Hand  - Realistic'];ev=source.evaluated_get(bpy.context.evaluated_depsgraph_get());handme=ev.to_mesh();baseverts=[v.co.copy() for v in handme.vertices];basefaces=[tuple(f.vertices) for f in handme.polygons];ev.to_mesh_clear()
cages=bpy.data.collections.get('MT_PreviousHandSources') or bpy.data.collections.new('MT_PreviousHandSources')
if cages.name not in char.children:char.children.link(cages)
cages.hide_render=True;cages.hide_viewport=True
for ob in list(char.objects):
    if ob.name.startswith(('MT_Glove','MT_GloveKnuckle')):char.objects.unlink(ob);cages.objects.link(ob)
for sg,sd in [(1,'L'),(-1,'R')]:
    vv=[Vector((.035-v.y*.55,sg*(.290-v.x*.55),.900+v.z*.55)) for v in baseverts]
    ff=[f for f in basefaces if all(vv[i].z<.918 for i in f)]
    ob=newmesh('MT_GloveSkin_'+sd,vv,ff,bpy.data.materials['MT2_RedLeather'],'hand.'+sd)
    ob['anatomy_source']='Dan Ulrich realistic hand, Blender Human Base Meshes, CC0. Adapted into glove on the same Matt rig.'
    ob.shape_key_add(name='Basis');key=ob.shape_key_add(name='DrivingGrip')
    for v in key.data:
        p=v.co.copy();d=max(0,.865-p.z)
        if d:
            angle=min(pi,d/.080*pi);rad=.080/pi;v.co.x=p.x+rad*(1-cos(angle));v.co.z=.865-rad*sin(angle)
    d=key.driver_add('value').driver;v=d.variables.new();v.name='pose';v.type='SINGLE_PROP';v.targets[0].id=r;v.targets[0].data_path='["driving_pose"]';d.expression='pose'
# Forearm/hand roll puts the palms toward the steering rim rather than facing up.
r['driving_pose']=1;r.update_tag();s.frame_set(97);bpy.context.view_layer.update()
for sg,sd in [(1,'L'),(-1,'R')]:
    pb=r.pose.bones['hand.'+sd];matrix=pb.matrix.copy();loc,rot,scale=matrix.decompose();direction=(pb.tail-pb.head).normalized();q=Quaternion(direction,sg*pi/2)@rot
    for i in range(4):pb.driver_remove('rotation_quaternion',i)
    pb.matrix=Matrix.LocRotScale(loc,q,scale);bpy.context.view_layer.update();target=pb.rotation_quaternion.copy()
    if target.w<0:target.negate()
    for i in range(4):
        d=pb.driver_add('rotation_quaternion',i).driver;v=d.variables.new();v.name='pose';v.type='SINGLE_PROP';v.targets[0].id=r;v.targets[0].data_path='["driving_pose"]';start=1 if i==0 else 0;d.expression=f'{start}+pose*({target[i]-start:.12g})'

# Remove temporary library objects after adapting their geometry; no second head remains.
for ob in list(bpy.data.objects):
    if ob.name.startswith(('GEO-head_animation_realistic','realistic_head_','realistic_hand')) or ob.name=='Hand  - Realistic':bpy.data.objects.remove(ob,do_unlink=True)
assert sum(o.type=='ARMATURE' for o in char.all_objects)==1
assert sum(o.name=='MT_Head_AnatomicalSurface' for o in char.all_objects)==1
r['driving_pose']=1;r['mask_on']=False;r.location=(0,.4,0);r.update_tag();s.frame_set(97);bpy.context.view_layer.update()
s['Matt_AnatomySource']='Blender Human Base Meshes v1.2.0 CC0. Anatomical head adapted to portrait interpretation; realistic hand by Dan Ulrich. Same rig and original head object/suit retained.'
bpy.ops.wm.save_as_mainfile(filepath=str(T/'Thunderhawk_V13.blend'),compress=True)
(A/'anatomy_provenance_v4.json').write_text(json.dumps({'bundle_url':'https://download.blender.org/demo/asset-bundles/human-base-meshes/human-base-meshes-bundle-v1.2.0.zip','license':'CC0','hand_author':'Dan Ulrich','purpose':'Generic anatomy adaptation for user-authorized interpretation, not a specific real-person likeness','existing_head_object_retained':True,'existing_suit_and_rig_retained':True},indent=2))
print('MATT_V4_GENERIC_ANATOMY_FIT_SAVED')
