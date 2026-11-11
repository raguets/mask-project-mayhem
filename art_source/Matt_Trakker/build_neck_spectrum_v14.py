"""V14: shorter clean neck, lower helmet and shoulder-fitted flared collar.

Works from the existing V13 character, same rig/head/suit. Helmet geometry uses
the inspected user replica photos. Neck and flexible skirt are interpretations.
"""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from math import sin,cos,pi,sqrt,exp
P=Path('G:/DEV/mask-project-mayhem');T=P/'art_source/Thunderhawk';s=bpy.context.scene;r=bpy.data.objects['MattTrakker_Rig'];head=bpy.data.objects['MT_Head_AnatomicalSurface'];char=bpy.data.collections['MT11_Character'];mask=bpy.data.collections['Spectrum11_Asset']
assert s.get('THK_Version')=='V13','Start from the saved V13 assembly, not an already-refined scene.'
backup=T/'Thunderhawk_V14_before_work.blend'
if not backup.exists():bpy.ops.wm.save_as_mainfile(filepath=str(backup),copy=True,compress=True)
for screen in bpy.data.screens:
    for ar in screen.areas:
        if ar.type=='VIEW_3D':ar.spaces.active.shading.type='SOLID'
r['driving_pose']=0;r['mask_on']=False;r.location=(0,0,0);r.update_tag();s.frame_set(1);bpy.context.view_layer.update()
head_pointer=head.as_pointer();suit=bpy.data.objects['MT_ContinuousFlightSuit'];suit_pointer=suit.as_pointer();DROP=.035
def smooth(t):
    t=max(0,min(1,t));return t*t*(3-2*t)
def profile(z,rows):
    for j,((a,x),(b,y)) in enumerate(zip(rows,rows[1:])):
        if z<=b:
            t=max(0,min(1,(z-a)/(b-a)));d=(y-x)/(b-a);m0=d if j==0 else (y-rows[j-1][1])/(b-rows[j-1][0]);m1=d if j+2==len(rows) else (rows[j+2][1]-x)/(rows[j+2][0]-a)
            return (2*t**3-3*t*t+1)*x+(t**3-2*t*t+t)*(b-a)*m0+(-2*t**3+3*t*t)*y+(t**3-t*t)*(b-a)*m1
    return rows[-1][1]
# Recover the unclamped anatomical neck coordinates, preserving current face data.
before=set(bpy.data.objects)
with bpy.data.libraries.load(str(P/'art_source/AnatomyBase/bundle/human_base_meshes_bundle.blend'),link=False) as (src,dst):dst.objects=['GEO-head_animation_realistic']
donor=dst.objects[0]
if not donor.users_collection:s.collection.objects.link(donor)
donor.hide_render=True
ev=donor.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();original=[]
for v in me.vertices:
    p=ev.matrix_world@v.co;x=-p.y-.035;y=p.x-1.46257198;z=p.z+.93930
    y*=1+.065*exp(-((z-1.600)/.024)**2);x+=.003*exp(-((z-1.60)/.021)**2-(y/.034)**2);original.append(Vector((x,y,z)))
ev.to_mesh_clear();assert len(original)==len(head.data.vertices),'Donor topology no longer matches; do not guess vertex correspondence.'
sections=[]
for j in range(71):
    z=1.475+j*.002;near=[v for v in original if abs(v.z-z)<.004]
    if near:
        xmin=min(p.x for p in near);xmax=max(p.x for p in near);yr=max(abs(p.y) for p in near)
        sections.append((z,(xmin+xmax)/2,max(.012,(xmax-xmin)/2),max(.012,yr)))
def section(z,k):return profile(z,[(p[0],p[k]) for p in sections])
for v,clean in zip(head.data.vertices,original):
    old=v.co.copy();z=clean.z
    if z<1.585:
        w=1-smooth((z-1.548)/.037)
        rx=profile(z,[(1.475,.045),(1.495,.044),(1.53,.037),(1.56,.040),(1.585,.045)])
        ry=profile(z,[(1.475,.046),(1.495,.045),(1.53,.039),(1.56,.041),(1.585,.045)])
        cx=profile(z,[(1.475,-.012),(1.53,-.017),(1.585,-.021)])
        target=Vector((cx+(clean.x-section(z,1))*rx/section(z,2),clean.y*ry/section(z,3),z))
        v.co=old.lerp(target,w)
    v.co.z-=DROP*smooth((v.co.z-1.492)/.105)
head.vertex_groups.clear();gh=head.vertex_groups.new(name='head');gn=head.vertex_groups.new(name='neck')
for v in head.data.vertices:
    w=smooth((v.co.z-1.497)/.052)
    if w:gh.add([v.index],w,'REPLACE')
    if w<1:gn.add([v.index],1-w,'REPLACE')
for f in head.data.polygons:f.use_smooth=True
head.data.update()
for ob in list(bpy.data.objects):
    if ob not in before:bpy.data.objects.remove(ob,do_unlink=True)
# All facial attachments move with this same head; the collar on the shirt stays.
for ob in char.objects:
    if ob.type=='MESH' and ob!=head and ob.name.startswith(('MT_Hair','MT_Eye','MT_Iris','MT_Brow','MT_Cornea','MT_Pupil')):
        for v in ob.data.vertices:v.co.z-=DROP
        ob.data.update()
# Lower the rigid helmet with the face, and flare the silver lower shell.
for ob in list(mask.objects):
    if ob.name.startswith('Spectrum_DoubleRedNeckSeal') or ob.name=='Spectrum_NeckSealConnectingBody':
        bpy.data.objects.remove(ob,do_unlink=True);continue
    if ob.type!='MESH':continue
    for v in ob.data.vertices:
        z=v.co.z
        if ob.name=='Spectrum_SilverHelmetShell' and z<1.70:
            oldw=profile(z,[(1.548,.099),(1.57,.107),(1.61,.115),(1.65,.119),(1.70,.120)])
            neww=profile(z,[(1.548,.153),(1.57,.151),(1.61,.139),(1.65,.121),(1.70,.120)])
            v.co.y*=neww/oldw
            if v.co.x<-.015:v.co.x=-.015+(v.co.x+.015)*(1-.17*(1-smooth((z-1.548)/.10)))
        v.co.z-=DROP
    ob.data.update()
# A shoulder-contoured flexible skirt, not a stack of floating circular rings.
ev=suit.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();suit_v=[v.co.copy() for v in me.vertices];suit_f=[tuple(f.vertices) for f in me.polygons];ev.to_mesh_clear();tree=BVHTree.FromPolygons(suit_v,suit_f)
N=128;R=25;edge=[];tops=[];report=[]
for i in range(N):
    a=2*pi*i/N;c=cos(a);sn=sin(a)
    bx=-.012+(.111 if c>=0 else .084)*c;by=.176*sn
    hit,normal,idx,dist=tree.ray_cast(Vector((bx,by,1.60)),Vector((0,0,-1)),.35)
    bz=hit.z+.0035 if hit is not None else 1.468-.025*max(0,c)
    bz=max(1.425,min(1.492,bz));edge.append(Vector((bx,by,bz)))
    tops.append(Vector((-.015+(.124 if c>=0 else .096)*c,.151*sn,1.513+.003*max(0,c))))
    report.append({'angle':a,'shoulder_ray_hit':hit is not None,'edge_z':bz})
def point(t,i):
    a=2*pi*i/N;v=tops[i].lerp(edge[i],t)
    band=.0033*exp(-((t-.68)/.10)**2)+.0030*exp(-((t-.94)/.075)**2)
    v.x+=band*cos(a);v.y+=band*sin(a);return v
red=bpy.data.materials['Spectrum3_DeepRedLacquer']
def make(name,vv,ff,weights,thick=0):
    me=bpy.data.meshes.new(name+'_Editable');me.from_pydata(vv,[],ff);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);mask.objects.link(ob);me.materials.append(red)
    for f in me.polygons:f.use_smooth=True
    groups={n:ob.vertex_groups.new(name=n) for n in ['head','chest']}
    for i,w in enumerate(weights):
        if w>0:groups['head'].add([i],w,'REPLACE')
        if w<1:groups['chest'].add([i],1-w,'REPLACE')
    if thick:mod=ob.modifiers.new('FlexibleCollarThickness','SOLIDIFY');mod.thickness=thick;mod.offset=-1
    mod=ob.modifiers.new('SameCharacterCollarSkin','ARMATURE');mod.object=r;mod.use_deform_preserve_volume=True;ob.parent=r
    for prop in ['hide_render','hide_viewport']:
        d=ob.driver_add(prop).driver;v=d.variables.new();v.name='helmet';v.type='SINGLE_PROP';v.targets[0].id=r;v.targets[0].data_path='["mask_on"]';d.expression='not helmet'
    ob['geometry_note']='Shoulder-flared collar interpreted from inspected replica photos; flexible chest/head weighting is inferred to fit the same two poses.'
    return ob
vv=[];ff=[];weights=[]
for j in range(R):
    t=j/(R-1)
    for i in range(N):vv.append(tuple(point(t,i)));weights.append(1-smooth((t-.12)/.75))
for j in range(R-1):
    for i in range(N):ff.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
make('Spectrum_NeckSealConnectingBody',vv,ff,weights,.0024)
for name,t in [('Upper',.64),('Lower',.94)]:
    vv=[];ff=[];weights=[];S=10
    for j in range(S):
        b=2*pi*j/S
        for i in range(N):
            a=2*pi*i/N;p=point(t,i)+Vector((.0028*cos(b)*cos(a),.0028*cos(b)*sin(a),.0028*sin(b)))
            vv.append(tuple(p));weights.append(1-smooth((t-.12)/.75))
    for j in range(S):
        for i in range(N):ff.append((j*N+i,j*N+(i+1)%N,((j+1)%S)*N+(i+1)%N,((j+1)%S)*N+i))
    make('Spectrum_DoubleRedNeckSeal_'+name,vv,ff,weights)
assert head.as_pointer()==head_pointer and suit.as_pointer()==suit_pointer
r['asset_version']='Matt Trakker V5 / Spectrum V4';r['neck_refinement']='Head/attachments lowered 35 mm, neck unclamped and smoothly reweighted. Anatomical dimensions estimated.'
s['THK_Version']='V14';s.name='THK_V14_ShortNeck_ShoulderFlaredSpectrum';s['V14_ReferenceReview']='Replica photos images (1),(2); illustrated portraits (5),(7), actually inspected. Collar/neck measurements and flexible construction interpreted.'
r['driving_pose']=1;r['mask_on']=False;r.location=(0,.4,0);r.update_tag();s.frame_set(97);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(T/'Thunderhawk_V14.blend'),compress=True)
(T/'neck_collar_changes_v14.json').write_text(json.dumps({'head_drop_m_estimated':DROP,'collar_base_half_width_m_estimated':.176,'collar_top_half_width_m_estimated':.151,'shoulder_samples':report,'same_head_object_and_suit':True,'reference_categories':'replica photographs and illustrations, not an official human costume scan'},indent=2))
print('V14_SHORTER_NECK_AND_SHOULDER_FLARE_SAVED')
