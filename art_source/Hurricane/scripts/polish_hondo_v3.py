import bpy,bmesh,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from math import sin,cos,pi,sqrt,atan2
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Hurricane';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((A/'scripts/geometry.py').read_text(),'<geometry>','exec'))
R=bpy.data.objects['HondoMacLean_Rig'];MASTER=bpy.data.objects['Hurricane_Control'];R.driver_remove('["gunner_pose"]');R.driver_remove('["vehicle_lift"]');R['gunner_pose']=0;R['vehicle_lift']=0;R['in_vehicle']=0;R['driving_pose']=0;R.update_tag();S.frame_set(1);bpy.context.view_layer.update()
CURRENT=bpy.data.collections['HMC_Character'];PARENT=None;GROUP='hondo_body';suit=bpy.data.objects['HMC_ContinuousFlightSuit'];YELLOW=bpy.data.materials['HMC_GoldenArmor']
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
# Blend the repair into the actual calf/thigh profiles instead of leaving a tubular cuff.
for v in suit.data.vertices:
    z=v.co.z
    if not .40<z<.73:continue
    sg=1 if v.co.y>0 else -1;cx=.012;cy=sg*profile(z,[(.4,.110),(.54,.110),(.73,.103)])
    if abs(v.co.y-cy)>.13:continue
    a=atan2(v.co.y-cy,v.co.x-cx);rx=profile(z,[(.40,.059),(.50,.064),(.60,.071),(.73,.079)]);ry=profile(z,[(.40,.066),(.50,.071),(.60,.078),(.73,.085)]);w=min(smooth((z-.40)/.025),smooth((.73-z)/.025));target=Vector((cx+rx*cos(a),cy+ry*sin(a),z));v.co=v.co.lerp(target,w)
suit.data.update();tree=BVHTree.FromPolygons([v.co for v in suit.data.vertices],[list(f.vertices) for f in suit.data.polygons])
def bind(o,bone='chest'):
    o.vertex_groups.new(name=bone).add(list(range(len(o.data.vertices))),1,'REPLACE');m=o.modifiers.new('HondoSkin','ARMATURE');m.object=R;m.use_deform_preserve_volume=True;o.parent=R;return o
for name in ['HMC_FormedShoulder_L','HMC_FormedShoulder_R','HMC_UpperChestArmor_L','HMC_UpperChestArmor_R']:
    o=bpy.data.objects.get(name)
    if o:bpy.data.objects.remove(o,do_unlink=True)
for sg,label in [(1,'L'),(-1,'R')]:
    # Thin smooth protective pauldrons over the continuous cloth, not spherical joints.
    vv=[];ff=[];N=56;H=18
    for j in range(H):
        t=.008+1.32*j/(H-1)
        for i in range(N):
            a=i*2*pi/N;vv.append((-.005+.105*sin(t)*cos(a),sg*.19+.115*sin(t)*sin(a),1.395+.09*cos(t)))
    for j in range(H-1):ff.extend((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i) for i in range(N))
    o=bind(mesh('HMC_SculptedPauldron_'+label,vv,ff,YELLOW,smooth=True),'upper_arm.'+label);m=o.modifiers.new('ArmorWall','SOLIDIFY');m.thickness=.004
    vv=[];ff=[];N=20;H=18
    for i in range(N):
        u=i/(N-1);y=sg*(.025+.155*u);low=1.333+.028*u;high=1.463-.015*u
        for j in range(H):
            z=low+(high-low)*j/(H-1);x=.105-.050*((z-1.36)/.13)-.18*y*y;vv.append((x,y,z))
    for i in range(N-1):ff.extend((i*H+j,(i+1)*H+j,(i+1)*H+j+1,i*H+j+1) for j in range(H-1))
    o=bind(mesh('HMC_FormedChestYoke_'+label,vv,ff,YELLOW,smooth=True));m=o.modifiers.new('ArmorWall','SOLIDIFY');m.thickness=.004
    # Refit the pads to the newly blended cloth.
    o=bpy.data.objects['HMC_FittedKneeGuard_'+label]
    for v in o.data.vertices:
        y,z=v.co.y,v.co.z;hit=tree.ray_cast(Vector((.25,y,z)),Vector((-1,0,0)),.4)
        if hit[0]:v.co.x=hit[0].x+.008
# Red brow now tessellated along the dome, not a planar chord buried inside it.
CURRENT=bpy.data.collections['HMC_Mask'];GROUP='hondo_mask';MRED=bpy.data.materials['HMC_MaskRed'];old=bpy.data.objects['HMC_MaskRedBrow'];bpy.data.objects.remove(old,do_unlink=True)
vv=[];ff=[];N=48;H=7
for i in range(N):
    y=-.116+.232*i/(N-1);f=abs(y)/.116;lo=1.772*(1-f)+1.736*f;hi=1.796*(1-f)+1.758*f
    for j in range(H):
        z=lo+(hi-lo)*j/(H-1);x=-.015+.139*sqrt(max(.003,1-(y/.130)**2-((z-1.725)/.095)**2))+.003;vv.append((x,y,z))
for i in range(N-1):ff.extend((i*H+j,(i+1)*H+j,(i+1)*H+j+1,i*H+j+1) for j in range(H-1))
o=bind(mesh('HMC_FittedRedBrow',vv,ff,MRED,smooth=True),'head')
for prop in ['hide_render','hide_viewport']:drive(o,prop,None,'1-m',[('m',R,'mask_on')])
apron=bpy.data.objects['HMC_FlaredRearHelmetApron'];rows=[(1.492,.165,.190),(1.54,.153,.174),(1.62,.134,.146),(1.705,.131,.131)];N=64
for j,(z,rx,ry) in enumerate(rows):
    for i in range(N):
        a=pi/2+.48+(pi-.96)*i/(N-1);apron.data.vertices[j*N+i].co=(-.015+rx*cos(a),ry*sin(a),z)
drive(R,'["gunner_pose"]',None,'p',[('p',MASTER,'_roofgun')]);drive(R,'["vehicle_lift"]',None,'l',[('l',MASTER,'_lift')]);R['in_vehicle']=1;R['driving_pose']=1
for o in S.objects:
    if o.animation_data:
        for f in o.animation_data.drivers:f.driver.expression=f.driver.expression.replace(' + 0.0','')+' + 0.0'
    o.update_tag()
S.frame_set(151);S.frame_set(1);bpy.context.view_layer.update();S['Hondo_Version']='V2, cloth continuity and smooth molded armor, neck refit, fitted brow.'
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Hurricane_V3_Assembly.blend'),compress=True);print('HONDO_POLISHED_V3')
