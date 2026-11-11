"""Replace only the defective lower neck with a continuous stitched surface."""
import bpy,bmesh,math
from pathlib import Path
from mathutils import Vector,Matrix
P=Path('G:/DEV/mask-project-mayhem');T=P/'art_source/Thunderhawk';s=bpy.context.scene;r=bpy.data.objects['MattTrakker_Rig'];head=bpy.data.objects['MT_Head_AnatomicalSurface']
if not (T/'Thunderhawk_V14_first_review.blend').exists():bpy.ops.wm.save_as_mainfile(filepath=str(T/'Thunderhawk_V14_first_review.blend'),copy=True,compress=True)
r['driving_pose']=0;r['mask_on']=False;r.location=(0,0,0);r.update_tag();s.frame_set(1);bpy.context.view_layer.update()
bm=bmesh.new();bm.from_mesh(head.data);normal=Vector((.30,0,1)).normalized();origin=Vector((0,0,1.557))
bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=origin,plane_no=normal,clear_inner=True,clear_outer=False)
loose=[v for v in bm.verts if not v.link_faces]
if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
edges=[e for e in bm.edges if e.is_boundary and all(abs((v.co-origin).dot(normal))<.0001 for v in e.verts)]
assert len(edges)>16,'Neck cut failed; do not construct a guessed bridge.'
adj={}
for e in edges:
    a,b=e.verts;adj.setdefault(a,[]).append(b);adj.setdefault(b,[]).append(a)
assert all(len(v)==2 for v in adj.values()),'Neck boundary is not a simple loop.'
start=min(adj,key=lambda v:v.co.y);loop=[];prev=None;cur=start
while True:
    loop.append(cur);nxt=next(v for v in adj[cur] if v!=prev)
    if nxt==start:break
    prev,cur=cur,nxt
    assert len(loop)<=len(adj),'Neck boundary traversal failed.'
assert len(loop)==len(adj),'More than one cut loop found.'
color=bm.verts.layers.float_color.get('MattSkinTint');rings=[];N=len(loop);R=23
for j in range(R-1):
    t=j/(R-1);row=[]
    for top in loop:
        a=math.atan2(top.co.y/.045,(top.co.x+.012)/.042)
        base=Vector((-.012+.042*math.cos(a),.044*math.sin(a),1.479))
        p=base.lerp(top.co,t);p.x-=.0020*math.sin(math.pi*t)*math.cos(a);p.y-=.0020*math.sin(math.pi*t)*math.sin(a)
        v=bm.verts.new(p)
        if color:v[color]=(.57,.338,.228,1)
        row.append(v)
    rings.append(row)
rings.append(loop)
for j in range(R-1):
    for i in range(N):bm.faces.new((rings[j][i],rings[j][(i+1)%N],rings[j+1][(i+1)%N],rings[j+1][i]))
bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(head.data);bm.free();head.data.update()
head.vertex_groups.clear();gh=head.vertex_groups.new(name='head');gn=head.vertex_groups.new(name='neck')
for v in head.data.vertices:
    t=max(0,min(1,(v.co.z-1.491)/.078));w=t*t*(3-2*t)
    if w:gh.add([v.index],w,'REPLACE')
    if w<1:gn.add([v.index],1-w,'REPLACE')
for f in head.data.polygons:f.use_smooth=True
# Remove the excessive seated neck-axis compression, keeping the same control.
for name in ['neck','head']:
    pb=r.pose.bones[name]
    for prop in ['location','rotation_quaternion','scale']:
        try:pb.driver_remove(prop)
        except Exception:pass
    pb.location=(0,0,0);pb.rotation_mode='QUATERNION';pb.rotation_quaternion=(1,0,0,0);pb.scale=(1,1,1)
bpy.context.view_layer.update();standing={n:(tuple(r.pose.bones[n].location),tuple(r.pose.bones[n].rotation_quaternion),tuple(r.pose.bones[n].scale)) for n in ['neck','head']}
r['driving_pose']=1;r.update_tag();s.frame_set(97);bpy.context.view_layer.update()
targets={'neck':((-.58,0,.94),(-.60,0,1.015)),'head':((-.60,0,1.015),(-.60,0,1.245))}
for name in ['neck','head']:
    pb=r.pose.bones[name];bone=r.data.bones[name];a,b=map(Vector,targets[name]);ra=bone.head_local;rb=bone.tail_local
    q=(rb-ra).rotation_difference(b-a)@bone.matrix_local.to_quaternion();scale=Vector((1,(b-a).length/(rb-ra).length,1));pb.matrix=Matrix.LocRotScale(a,q,scale);bpy.context.view_layer.update()
driving={n:(tuple(r.pose.bones[n].location),tuple(r.pose.bones[n].rotation_quaternion),tuple(r.pose.bones[n].scale)) for n in ['neck','head']}
for name in ['neck','head']:
    pb=r.pose.bones[name]
    for k,prop in enumerate(['location','rotation_quaternion','scale']):
        lo=standing[name][k];hi=list(driving[name][k])
        if prop=='rotation_quaternion' and sum(x*y for x,y in zip(lo,hi))<0:hi=[-v for v in hi]
        for i,(a,b) in enumerate(zip(lo,hi)):
            d=pb.driver_add(prop,i).driver;v=d.variables.new();v.name='pose';v.type='SINGLE_PROP';v.targets[0].id=r;v.targets[0].data_path='["driving_pose"]';d.expression=f'{a:.12g}+pose*({b-a:.12g})'
# The helmet was sitting high on the face: lower its rigid parts another 10 mm.
for ob in bpy.data.collections['Spectrum11_Asset'].objects:
    if ob.name.startswith(('Spectrum_NeckSealConnectingBody','Spectrum_DoubleRedNeckSeal')):continue
    if ob.type=='MESH':
        for v in ob.data.vertices:v.co.z-=.010
        ob.data.update()
r['driving_pose']=1;r['mask_on']=False;r.location=(0,.4,0);r.update_tag();s.frame_set(97);bpy.context.view_layer.update()
s['V14_NeckCorrection']='Lower neck rebuilt as a continuous stitched surface; seated neck no longer strongly compressed; head driving height adjusted +30 mm relative to first V14 pass. Estimated anatomy.'
bpy.ops.wm.save_as_mainfile(filepath=str(T/'Thunderhawk_V14.blend'),compress=True)
print('V14_CONTINUOUS_NECK_AND_POSE_CORRECTION_SAVED')
