"""Repair actual garment continuity, neck rig length and photographed helmet fit."""
import bpy,bmesh,ast,json,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from math import sin,cos,pi,sqrt
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Hurricane';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Session_before_Hondo_surface_v2.blend'),copy=True,compress=True)
exec(compile((A/'scripts/geometry.py').read_text(),'<geometry>','exec'))
R=bpy.data.objects['HondoMacLean_Rig'];C=bpy.data.collections['HMC_Character'];CURRENT=C;PARENT=None;GROUP='hondo_body';MASTER=bpy.data.objects['Hurricane_Control'];R.driver_remove('["gunner_pose"]');R.driver_remove('["vehicle_lift"]');R['gunner_pose']=0;R['vehicle_lift']=0;R['driving_pose']=0;R['in_vehicle']=0;R.update_tag();S.frame_set(1);bpy.context.view_layer.update()
PURPLE=bpy.data.materials['HMC_DeepPurpleFabric'];YELLOW=bpy.data.materials['HMC_GoldenArmor'];CYAN=bpy.data.materials['HMC_MaskTurquoise'];MRED=bpy.data.materials['HMC_MaskRed'];suit=bpy.data.objects['HMC_ContinuousFlightSuit']
for name in ['HMC_KneePatch_L','HMC_KneePatch_R','HMC_FittedShoulder_L','HMC_FittedShoulder_R']:
    o=bpy.data.objects.get(name)
    if o:bpy.data.objects.remove(o,do_unlink=True)
# Join bridging fabric into the same suit mesh and transfer normalized original weights.
vv=[v.co.copy() for v in suit.data.vertices];ff=[tuple(f.vertices) for f in suit.data.polygons];ww=[{suit.vertex_groups[g.group].name:g.weight for g in v.groups} for v in suit.data.vertices]
for sg,label in [(1,'L'),(-1,'R')]:
    off=len(vv);N=64;H=32
    for j in range(H):
        z=.43+.24*j/(H-1);radius=profile(z,[(.43,.076),(.49,.081),(.54,.086),(.61,.090),(.67,.092)])
        u=max(0,min(1,(z-.485)/.12));u=u*u*(3-2*u)
        for i in range(N):
            a=2*pi*i/N;vv.append(Vector((.012+radius*cos(a),sg*.11+radius*sin(a),z)));ww.append({'thigh.'+label:u,'shin.'+label:1-u})
    for j in range(H-1):ff.extend((off+j*N+i,off+j*N+(i+1)%N,off+(j+1)*N+(i+1)%N,off+(j+1)*N+i) for i in range(N))
    ff.extend([tuple(off+i for i in reversed(range(N))),tuple(off+(H-1)*N+i for i in range(N))])
weighttree=BVHTree.FromPolygons(vv,ff);me=bpy.data.meshes.new('HMC_ClothRepairInput');me.from_pydata(vv,[],ff);me.update();temp=bpy.data.objects.new('HMC_ClothRepairWork',me);C.objects.link(temp)
m=temp.modifiers.new('ContinuousKneeUnion','REMESH');m.mode='VOXEL';m.voxel_size=.0035;m.use_smooth_shade=True;m=temp.modifiers.new('RelaxCloth','SMOOTH');m.factor=.60;m.iterations=4
dg=bpy.context.evaluated_depsgraph_get();new=bpy.data.meshes.new_from_object(temp.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg);new.name='HMC_ContinuousSuit_Repaired';suit.data=new;suit.vertex_groups.clear();new.materials.clear();new.materials.append(PURPLE)
groups={name:suit.vertex_groups.new(name=name) for name in {k for w in ww for k in w}}
for v in new.vertices:
    p,n,idx,dist=weighttree.find_nearest(v.co);amounts={};total=0
    for k in ff[idx]:
        a=1/max(.0003,(vv[k]-p).length);total+=a
        for name,w in ww[k].items():amounts[name]=amounts.get(name,0)+w*a
    for name,w in amounts.items():
        if w/total>.0001:groups[name].add([v.index],w/total,'REPLACE')
for f in new.polygons:f.use_smooth=True
bpy.data.objects.remove(temp,do_unlink=True)
# Newly fitted small knee pads, on the same continuous garment.
sv=suit.data.vertices;sf=suit.data.polygons;tree=BVHTree.FromPolygons([v.co for v in sv],[list(f.vertices) for f in sf])
def skinbind(o,weights):
    for i,items in enumerate(weights):
        total=sum(items.values()) or 1
        for name,w in items.items():
            vg=o.vertex_groups.get(name) or o.vertex_groups.new(name=name);vg.add([i],w/total,'REPLACE')
    arm=o.modifiers.new('HondoSkin','ARMATURE');arm.object=R;arm.use_deform_preserve_volume=True;o.parent=R;return o
for sg,label in [(1,'L'),(-1,'R')]:
    pv=[];pf=[];pw=[];N=20;H=18
    for j in range(H):
        z=.485+.11*j/(H-1)
        for i in range(N):
            y=sg*.11+(.050*sin(-pi/2+pi*i/(N-1)));hit=tree.ray_cast(Vector((.25,y,z)),Vector((-1,0,0)),.4)
            if hit[0] is None:hit=tree.find_nearest(Vector((.08,y,z)))
            p,n,idx,dist=hit;p=Vector((p.x+.009,y,z));pv.append(tuple(p));u=max(0,min(1,(z-.51)/.09));pw.append({'shin.'+label:1-u*.45,'thigh.'+label:u*.45})
    for j in range(H-1):pf.extend((j*N+i,j*N+i+1,(j+1)*N+i+1,(j+1)*N+i) for i in range(N-1))
    o=skinbind(mesh('HMC_FittedKneeGuard_'+label,pv,pf,YELLOW,smooth=True),pw);solid=o.modifiers.new('GuardThickness','SOLIDIFY');solid.thickness=.003
# Formed shallow shoulder plates follow the surface; avoid jagged extracted edges or ball joints.
for sg,label in [(1,'L'),(-1,'R')]:
    pv=[];pf=[];pw=[];N=22;H=18
    for i,x in enumerate(seq(N-1,-.095,.095)):
        for j,y0 in enumerate(seq(H-1,.13,.29)):
            y=sg*y0;hit=tree.ray_cast(Vector((x,y,1.65)),Vector((0,0,-1)),.4)
            if hit[0] is None:hit=tree.find_nearest(Vector((x,y,1.43)))
            p,n,idx,dist=hit;pv.append((x,y,p.z+.010));face=sf[idx];v=min((sv[k] for k in face.vertices),key=lambda v:(v.co-p).length_squared);pw.append({suit.vertex_groups[g.group].name:g.weight for g in v.groups})
    for i in range(N-1):pf.extend((i*H+j,(i+1)*H+j,(i+1)*H+j+1,i*H+j+1) for j in range(H-1))
    o=skinbind(mesh('HMC_FormedShoulder_'+label,pv,pf,YELLOW,smooth=True),pw);sm=o.modifiers.new('ArmorSmoothing','SMOOTH');sm.factor=.55;sm.iterations=8;o.modifiers.move(len(o.modifiers)-1,0);solid=o.modifiers.new('ShoulderPlateWall','SOLIDIFY');solid.thickness=.004
for o in C.all_objects:
    if o.name.startswith('HMC_UpperChestArmor_'):
        sm=o.modifiers.new('SmoothArmorSurface','SMOOTH');sm.factor=.65;sm.iterations=10;o.modifiers.move(len(o.modifiers)-1,0)
# Refit the neck and head transforms together in all three poses, preserving head shape.
states=[]
for d,g in [(0,0),(1,0),(0,1)]:
    R['driving_pose']=d;R['gunner_pose']=g;R.update_tag();bpy.context.view_layer.update();states.append({pb.name:{p:tuple(getattr(pb,p)) for p in ['location','rotation_quaternion','scale']} for pb in R.pose.bones})
for f in list(R.animation_data.drivers):
    if f.data_path.startswith('pose.bones['):R.animation_data.drivers.remove(f)
refined=[]
for state in states:
    for name,values in state.items():
        for prop,value in values.items():setattr(R.pose.bones[name],prop,value)
    bpy.context.view_layer.update();neck=R.pose.bones['neck'];head=R.pose.bones['head'];hm=head.matrix.copy();headtarget=hm.translation-Vector((0,0,.020));a=neck.head.copy();b=headtarget;q=(neck.tail-neck.head).rotation_difference(b-a)@neck.matrix.to_quaternion();oldscale=neck.matrix.to_scale();newscale=Vector((oldscale.x,(b-a).length/R.data.bones['neck'].length,oldscale.z));neck.matrix=Matrix.LocRotScale(a,q,newscale);bpy.context.view_layer.update();hm.translation=headtarget;head.matrix=hm;bpy.context.view_layer.update();refined.append({pb.name:{p:tuple(getattr(pb,p)) for p in ['location','rotation_quaternion','scale']} for pb in R.pose.bones})
for name in refined[0]:
    for prop in ['location','rotation_quaternion','scale']:
        s=refined[0][name][prop];d=list(refined[1][name][prop]);g=list(refined[2][name][prop])
        if prop=='rotation_quaternion':
            if sum(a*b for a,b in zip(s,d))<0:d=[-v for v in d]
            if sum(a*b for a,b in zip(s,g))<0:g=[-v for v in g]
        for i,(a,b,c) in enumerate(zip(s,d,g)):drive(R.pose.bones[name],prop,i,f'{a:.10g}+({b-a:.10g})*d*(1-g)+({c-a:.10g})*g',[('d',R,'driving_pose'),('g',R,'gunner_pose')])
# Bring the dome and red brow onto the actual forehead instead of floating in front of it.
crown=bpy.data.objects['HMC_MaskDomedCrown']
for v in crown.data.vertices:v.co.z=1.725+(v.co.z-1.735)*(.095/.120)
brow=bpy.data.objects['HMC_MaskRedBrow']
for v in brow.data.vertices:v.co.x=-.015+.139*sqrt(max(.005,1-(v.co.y/.130)**2-((v.co.z-1.725)/.095)**2))+.003
for o in bpy.data.collections['HMC_Mask'].all_objects:
    if o.name.startswith('HMC_RedCrestSegment_'):
        cx=sum(v.co.x for v in o.data.vertices)/len(o.data.vertices);old=1.735+.12*sqrt(max(0,1-((cx+.015)/.139)**2))+.008;newz=1.725+.095*sqrt(max(0,1-((cx+.015)/.139)**2))+.008
        for v in o.data.vertices:v.co.z+=newz-old
CURRENT=bpy.data.collections['HMC_Mask'];GROUP='hondo_mask';N=48;pv=[];pf=[]
for row in [0,1]:
    for i in range(N):
        a=-pi/2+pi*i/(N-1)
        if row==0:pv.append((-.015+.139*cos(a),.130*sin(a),1.728))
        else:pv.append((.128+.017*cos(a),.115*sin(a),1.709))
pf=[(i,i+1,N+i+1,N+i) for i in range(N-1)];o=mesh('HMC_FittedBrowTransition',pv,pf,CYAN,smooth=True);vg=o.vertex_groups.new(name='head');vg.add(list(range(len(pv))),1,'REPLACE');mod=o.modifiers.new('HeadBind','ARMATURE');mod.object=R;o.parent=R
for prop in ['hide_render','hide_viewport']:drive(o,prop,None,'1-m',[('m',R,'mask_on')])
# Restore the assembly bridges only; independent export removes these two explicit paths.
drive(R,'["gunner_pose"]',None,'p',[('p',MASTER,'_roofgun')]);drive(R,'["vehicle_lift"]',None,'l',[('l',MASTER,'_lift')]);R['driving_pose']=1;R['in_vehicle']=1
# Close the hood/front-fender junctions using matching boundary heights.
for o in S.objects:
    if o.name.startswith('HU_FrontFenderCrown_'):
        for v in o.data.vertices:
            x,y,z=v.co;w=profile(x,[(-2.62,.88),(-2.38,.97),(-1.4,.97),(0,.98),(1.5,.94),(2.27,.94),(2.55,.85)]);t=(abs(y)-.64)/(w-.64);base=profile(x,[(.89,1.145),(1.45,1.13),(2.37,1.045)])+.055*(1-(.64/.68)**2);belt=profile(x,[(-2.62,1.28),(-2.28,1.22),(-1.25,1.12),(.15,1.13),(.85,1.12),(1.8,1.10),(2.55,1.12)]);v.co.z=base*(1-t)+belt*t+.06*sin(pi*t)
lip=bpy.data.objects['HU_HoodFrontLip']
for v in lip.data.vertices:
    t=(v.co.x-2.34)/.17;v.co.z=(1-t)*(1.047+.055*(1-(v.co.y/.68)**2))+t*1.04
for o in S.objects:
    if o.animation_data:
        for f in o.animation_data.drivers:f.driver.expression=f.driver.expression.replace(' + 0.0','')+' + 0.0'
    o.update_tag()
S.frame_set(151);S.frame_set(1);bpy.context.view_layer.update();S['Hondo_refinement']='Continuous repaired knees; fitted shallow shoulder plates; neck and head rig reposed together in three states; crown/brow joined.'
(A/'hondo_refinement_v2.json').write_text(json.dumps({'same_suit_object':suit.name,'suit_vertices':len(suit.data.vertices),'neck_rig_refit':True,'head_shape_preserved':True,'helmet_forehead_refit':True},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Hurricane_V2_Assembly.blend'),compress=True);print('HONDO_SURFACES_AND_RIG_REFINED')
