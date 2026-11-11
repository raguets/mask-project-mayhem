"""Low-profile flared Spectrum collar following the actual shoulder surface."""
import bpy,bmesh,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
s=bpy.context.scene;r=bpy.data.objects['MattTrakker_Rig'];mask=bpy.data.collections['Spectrum11_Asset'];suit=bpy.data.objects['MT_ContinuousFlightSuit']
r['driving_pose']=0;r['mask_on']=False;r.location=(0,0,0);r.update_tag();s.frame_set(1);bpy.context.view_layer.update()
for ob in list(mask.objects):
    if ob.name.startswith(('Spectrum_NeckSealConnectingBody','Spectrum_DoubleRedNeckSeal')):bpy.data.objects.remove(ob,do_unlink=True)
vv=[v.co.copy() for v in suit.data.vertices];ff=[tuple(f.vertices) for f in suit.data.polygons];tree=BVHTree.FromPolygons(vv,ff);N=128;R=23;edge=[];top=[]
for i in range(N):
    a=math.tau*i/N;c=math.cos(a);sn=math.sin(a);x=-.012+(.080 if c>=0 else .065)*c;y=.176*sn
    hit,normal,idx,d=tree.ray_cast(Vector((x,y,1.6)),Vector((0,0,-1)),.3);z=hit.z+.0035 if hit is not None else 1.47
    edge.append(Vector((x,y,z)));top.append(Vector((-.015+(.124 if c>=0 else .081)*c,.151*sn,1.503+.003*max(0,c))))
def point(t,i):
    a=math.tau*i/N;p=top[i].lerp(edge[i],t);b=.0027*math.exp(-((t-.68)/.12)**2)+.0027*math.exp(-((t-.95)/.075)**2);return p+Vector((b*math.cos(a),b*math.sin(a),0))
def make(name,verts,faces,headweights,wall=0):
    me=bpy.data.meshes.new(name+'_Editable');me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);mask.objects.link(ob);me.materials.append(bpy.data.materials['Spectrum3_DeepRedLacquer'])
    for f in me.polygons:f.use_smooth=True
    gh=ob.vertex_groups.new(name='head');gc=ob.vertex_groups.new(name='chest')
    for i,w in enumerate(headweights):
        if w:gh.add([i],w,'REPLACE')
        if w<1:gc.add([i],1-w,'REPLACE')
    if wall:mod=ob.modifiers.new('FlexibleCollarThickness','SOLIDIFY');mod.thickness=wall;mod.offset=-1
    mod=ob.modifiers.new('SameCharacterCollarSkin','ARMATURE');mod.object=r;mod.use_deform_preserve_volume=True;ob.parent=r
    for prop in ['hide_render','hide_viewport']:
        d=ob.driver_add(prop).driver;v=d.variables.new();v.name='helmet';v.type='SINGLE_PROP';v.targets[0].id=r;v.targets[0].data_path='["mask_on"]';d.expression='not helmet'
def weight(t):
    u=max(0,min(1,(t-.1)/.8));return 1-u*u*(3-2*u)
verts=[];faces=[];ww=[]
for j in range(R):
    t=j/(R-1)
    for i in range(N):verts.append(tuple(point(t,i)));ww.append(weight(t))
for j in range(R-1):
    for i in range(N):faces.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
make('Spectrum_NeckSealConnectingBody',verts,faces,ww,.0024)
for label,t in [('Upper',.65),('Lower',.94)]:
    verts=[];faces=[];ww=[];S=10
    for j in range(S):
        b=math.tau*j/S
        for i in range(N):
            a=math.tau*i/N;p=point(t,i)+Vector((.0024*math.cos(b)*math.cos(a),.0024*math.cos(b)*math.sin(a),.0024*math.sin(b)));verts.append(tuple(p));ww.append(weight(t))
    for j in range(S):
        for i in range(N):faces.append((j*N+i,j*N+(i+1)%N,((j+1)%S)*N+(i+1)%N,((j+1)%S)*N+i))
    make('Spectrum_DoubleRedNeckSeal_'+label,verts,faces,ww)
# Use the already tested nearest-garment weight transfer on these new surfaces.
exec(compile(Path('G:/DEV/mask-project-mayhem/art_source/Matt_Trakker/fit_collar_weights_v14.py').read_text(),'fit_collar_weights_v14.py','exec'))
r['driving_pose']=1;r['mask_on']=False;r.location=(0,.4,0);r.update_tag();s.frame_set(97);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath='G:/DEV/mask-project-mayhem/art_source/Thunderhawk/Thunderhawk_V14.blend',compress=True)
print('V14_LOW_PROFILE_FLARED_SHOULDER_COLLAR_SAVED')
