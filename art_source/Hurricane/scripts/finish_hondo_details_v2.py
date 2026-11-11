import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from math import sin,cos,pi
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Hurricane';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((A/'scripts/geometry.py').read_text(),'<geometry>','exec'))
R=bpy.data.objects['HondoMacLean_Rig'];MASTER=bpy.data.objects['Hurricane_Control'];R.driver_remove('["gunner_pose"]');R.driver_remove('["vehicle_lift"]');R['in_vehicle']=0;R['driving_pose']=0;R['gunner_pose']=0;R['vehicle_lift']=0;R.update_tag();S.frame_set(1);bpy.context.view_layer.update()
CURRENT=bpy.data.collections['HMC_Character'];PARENT=None;GROUP='hondo_body';YELLOW=bpy.data.materials['HMC_GoldenArmor'];suit=bpy.data.objects['HMC_ContinuousFlightSuit'];tree=BVHTree.FromPolygons([v.co for v in suit.data.vertices],[list(f.vertices) for f in suit.data.polygons])
def bind(o,bone):
    vg=o.vertex_groups.new(name=bone);vg.add(list(range(len(o.data.vertices))),1,'REPLACE');mod=o.modifiers.new('HondoSkin','ARMATURE');mod.object=R;mod.use_deform_preserve_volume=True;o.parent=R;return o
# Correct the first pad's folded lateral parametrization without redoing the cloth repair.
for sg,label in [(1,'L'),(-1,'R')]:
    o=bpy.data.objects['HMC_FittedKneeGuard_'+label];N=20;H=18
    for j in range(H):
        z=.485+.11*j/(H-1)
        for i in range(N):
            y=sg*.11+.050*sin(-pi/2+pi*i/(N-1));hit=tree.ray_cast(Vector((.25,y,z)),Vector((-1,0,0)),.4)
            if hit[0] is None:hit=tree.find_nearest(Vector((.08,y,z)))
            o.data.vertices[j*N+i].co=(hit[0].x+.009,y,z)
    # Real fitted forearm cuffs, larger than the inherited narrow wrist band.
    vv=[];ff=[];N=48;H=18
    for j in range(H):
        z=.970+.125*j/(H-1);t=(z-.915)/(1.155-.915);cx=.025+(.005-.025)*t;cy=sg*(.285+(.250-.285)*t)
        for i in range(N):
            a=2*pi*i/N;d=Vector((cos(a),sin(a),0));c=Vector((cx,cy,z));hit=tree.ray_cast(c,d,.15);rad=(hit[0]-c).length if hit[0] else .052;vv.append(tuple(c+d*(rad+.006)))
    for j in range(H-1):ff.extend((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i) for i in range(N))
    o=bind(mesh('HMC_FittedYellowBracer_'+label,vv,ff,YELLOW,smooth=True),'forearm.'+label);m=o.modifiers.new('BracerWall','SOLIDIFY');m.thickness=.003
CURRENT=bpy.data.collections['HMC_Mask'];GROUP='hondo_mask';BLACK=bpy.data.materials['HMC_Recess']
o=patch('HMC_MaskInnerFaceLiner',seq(24,-.102,.102),seq(12,1.555,1.671),lambda y,z:(.137+.012*(1-(y/.105)**2),y,z),BLACK,sub=0,thick=.002,orient=(1,0,0));bind(o,'head')
for prop in ['hide_render','hide_viewport']:drive(o,prop,None,'1-m',[('m',R,'mask_on')])
drive(R,'["gunner_pose"]',None,'p',[('p',MASTER,'_roofgun')]);drive(R,'["vehicle_lift"]',None,'l',[('l',MASTER,'_lift')]);R['in_vehicle']=1;R['driving_pose']=1
for ob in S.objects:
    if ob.animation_data:
        for f in ob.animation_data.drivers:f.driver.expression=f.driver.expression.replace(' + 0.0','')+' + 0.0'
    ob.update_tag()
S.frame_set(151);S.frame_set(1);bpy.context.view_layer.update();S.name='Hurricane_V2_Assembly'
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Hurricane_V2_Assembly.blend'),compress=True);print('HONDO_FITTED_DETAILS_V2')
