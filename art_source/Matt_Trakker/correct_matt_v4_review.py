"""Correct visible first-review defects: eye corners, skin contrast, groom crown."""
import bpy,bmesh,math,random
from pathlib import Path
from mathutils import Vector
from math import sin,cos,pi,sqrt
P=Path('G:/DEV/mask-project-mayhem');T=P/'art_source/Thunderhawk';s=bpy.context.scene;r=bpy.data.objects['MattTrakker_Rig'];char=bpy.data.collections['MT11_Character']
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.shading.type='SOLID'
r['driving_pose']=0;r['mask_on']=False;r.location=(0,0,0);r.update_tag();s.frame_set(1);bpy.context.view_layer.update()
# Shrink the cut aperture to the sclera; avoid black empty corners beyond the globe.
ob=bpy.data.objects['MT_Head_AnatomicalSurface'];me=ob.data;vv=[tuple(v.co) for v in me.vertices];ff=[];N=192;Z=169
for j in range(Z-1):
    for i in range(N):
        ids=(j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i);mid=sum((Vector(vv[k]) for k in ids),Vector())/4
        if mid.x>.030 and ((abs(mid.y)-.032)/.0118)**2+((mid.z-1.706)/.0044)**2<1:continue
        ff.append(ids)
ff.extend([tuple(range(N-1,-1,-1)),tuple((Z-1)*N+i for i in range(N))])
me.clear_geometry();me.from_pydata(vv,[],ff);me.update();ob.vertex_groups.clear();ob.vertex_groups.new(name='head').add(list(range(len(vv))),1,'REPLACE')
for ob in list(char.objects):
    if ob.name.startswith('MT_EyelidCrease_'):bpy.data.objects.remove(ob,do_unlink=True)
    elif ob.name.startswith('MT_EyelidSkin_'):
        count=len(ob.data.vertices)//7
        for v in ob.data.vertices:
            ring=v.index//count
            if ring>=4:v.co.x-=.0015*((ring-3)/3)**2
    elif ob.name.startswith('MT_EarTragus_'):
        center=sum((v.co for v in ob.data.vertices),Vector())/len(ob.data.vertices)
        for v in ob.data.vertices:v.co=center+(v.co-center)*.60
skin=bpy.data.materials['MT4_Skin'];bs=next(n for n in skin.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
for node in skin.node_tree.nodes:
    if node.type=='VALTORGB':
        node.color_ramp.elements[0].color=(.545,.320,.216,1);node.color_ramp.elements[1].color=(.592,.355,.242,1)
    if node.type=='BUMP':node.inputs['Distance'].default_value=.00005;node.inputs['Strength'].default_value=.13

# Keep a scalp below a dense, irregular fine-fiber mesh; no point or metal-like cap.
cap=bpy.data.objects['MT_Hair_NaturalSidePart'];me=cap.data
for v in me.vertices:
    if v.co.z>1.803:
        t=max(0,min(1,(v.co.z-1.803)/.018));v.co.z=1.803+(v.co.z-1.803)*.68
        v.co.x=-.008+(v.co.x+.008)*(1-t**8);v.co.y*=1-t**8
for name in ['MT4_NaturalBlond','MT4_BlondVariation']:
    m=bpy.data.materials[name];p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Roughness'].default_value=.78;p.inputs['Specular IOR Level'].default_value=.18
for ob in list(char.objects):
    if ob.name.startswith('MT_HairFiber_'):bpy.data.objects.remove(ob,do_unlink=True)
def scalp(t,a):
    f=max(0,min(43.999,t*44));j=int(f);tj=f-j;f=((a+pi)/(2*pi)*128)%128;i=int(f);ti=f-i
    def ring(j):return me.vertices[j*128+i].co.lerp(me.vertices[j*128+(i+1)%128].co,ti)
    return ring(j).lerp(ring(j+1),tj)
random.seed(174);vv=[];ff=[];mids=[];SIDES=4;STEPS=8
for k in range(7000):
    a=random.uniform(-pi,pi);root=random.uniform(.003,.94);length=random.uniform(.045,.19);rad=random.uniform(.000035,.000065);off=len(vv)
    for j in range(STEPS):
        u=j/(STEPS-1);t=min(.985,root+length*u);angle=a+.20*sin(pi*t)*u
        p=scalp(t,angle);normal=Vector((cos(angle),sin(angle),.4+1.3*t)).normalized();p+=normal*(.00018+.00032*sin(pi*u))
        for q in range(SIDES):
            b=2*pi*q/SIDES;vv.append(tuple(p+Vector((rad*cos(b),rad*sin(b),rad*.45*sin(b)))))
    for j in range(STEPS-1):
        for q in range(SIDES):ff.append((off+j*SIDES+q,off+j*SIDES+(q+1)%SIDES,off+(j+1)*SIDES+(q+1)%SIDES,off+(j+1)*SIDES+q));mids.append(k%7==0)
data=bpy.data.meshes.new('MT_Hair_DenseGroom_Editable');data.from_pydata(vv,[],ff);data.update();ob=bpy.data.objects.new('MT_Hair_DenseGroom',data);char.objects.link(ob)
data.materials.append(bpy.data.materials['MT4_NaturalBlond']);data.materials.append(bpy.data.materials['MT4_BlondVariation'])
for f,idx in zip(data.polygons,mids):f.material_index=int(idx);f.use_smooth=True
ob.vertex_groups.new(name='head').add(list(range(len(vv))),1,'REPLACE');mod=ob.modifiers.new('SameMattHeadSkin','ARMATURE');mod.object=r;ob.parent=r
for prop in ['hide_render','hide_viewport']:
    d=ob.driver_add(prop).driver;v=d.variables.new();v.name='helmet';v.type='SINGLE_PROP';v.targets[0].id=r;v.targets[0].data_path='["mask_on"]';d.expression='helmet'
r['driving_pose']=1;r['mask_on']=False;r.location=(0,.4,0);r.update_tag();s.frame_set(97);bpy.context.view_layer.update()
s['V13_ReviewCorrections']='Smaller eye apertures with embedded lid edges; subtler skin variation; dense low-profile groom without crown point.'
bpy.ops.wm.save_as_mainfile(filepath=str(T/'Thunderhawk_V13.blend'),compress=True)
print('MATT_V4_FIRST_REVIEW_DEFECTS_CORRECTED')
