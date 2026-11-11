"""Live Blender MCP: compact lifting reactor cassette and coherent body seams."""
import bpy,math,json,datetime
from pathlib import Path
from mathutils import Vector,Matrix
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Raven';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
assert not (A/'Raven_V12_Assembly.blend').exists(),'Preserve completed iteration'
backup=A/('Session_before_V12_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.blend')
bpy.ops.wm.save_as_mainfile(filepath=str(backup),copy=True,compress=True)
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(encoding='utf-8'),'<geometry>','exec'))
tau=2*pi;root=bpy.data.objects['Raven_Control'];R=bpy.data.objects['CalhounBurns_Rig'];root['hover_height']=0.;root['disc_launch']=0.;S.frame_set(1);R['in_vehicle']=0.;R['driving_pose']=0.;R['mask_on']=False;R.update_tag();bpy.context.view_layer.update()
BODY=bpy.data.collections['RV_Body'];INSIDE=bpy.data.collections['RV_Interior'];GEAR=bpy.data.collections['RV_RunningGear'];offset=bpy.data.objects['RV_PresentationOffset'];clip=bpy.data.objects['RV_CompleteFront_LongitudinalPivot'];hood=bpy.data.objects['RV_HoodSkin_FixedInFrontUnit']
PAINT=bpy.data.materials['RV_Obsidian_Clearcoat'];TRIM=bpy.data.materials['RV_BlackRubberTrim'];DARK=bpy.data.materials['RV_Gunmetal'];GLASS=bpy.data.materials['RV_TintedGlass'];ALLOY=bpy.data.materials['RV_BrushedAlloy']
CURRENT=BODY;PARENT=None;GROUP='surface_v12'
def remove(name):
    ob=bpy.data.objects.get(name)
    if ob:bpy.data.objects.remove(ob,do_unlink=True)
def width(x):return profile(x,[(-2.225,.77),(-1.93,.88),(-1.24,.915),(-.45,.87),(.40,.85),(1.22,.905),(1.9,.86),(2.225,.76)])
def rear_top(x):return profile(x,[(-2.225,.67),(-1.8,.79),(-1.15,.86),(-.6,.82),(.35,.77)])
def front_top(x):
    s=max(0,min(1,(x-.45)/1.775));return .77-.03*s-.28*s**4
def hood_z(x,y):return front_top(x)+.008*(1-(y/.6785)**2)
def lower_arch(x,ax):return .335+math.sqrt(max(0,.365**2-(x-ax)**2)) if abs(x-ax)<.365 else .22
# One clean hood surface; no recessed border or oscillating section heights.
for name in ['RV_Hood_OuterSkin','RV_Hood_ReverseArmor','RV_FrontUpperShoulder_L','RV_FrontUpperShoulder_R','RV_FrontFender_L','RV_FrontFender_R','RV_NoseFascia']:remove(name)
newhood=patch('RV_Hood_OuterSkin',seq(120,.455,2.215),seq(48,-1,1),lambda x,u:(x,.6785*u,hood_z(x,.6785*u)),PAINT,root=hood,sub=0,thick=.016,orient=(0,0,1))
newhood['user_spec']='Smooth monotone longitudinal profile; edge level matches front shoulder. Entire piece remains rigid in the rolling front unit.'
patch('RV_Hood_ReverseArmor',seq(80,.458,2.212),seq(36,-1,1),lambda x,u:(x,.677*u,hood_z(x,.677*u)-.020),DARK,root=hood,sub=0,thick=.006,orient=(0,0,-1))
for ob in list(bpy.data.objects):
    if ob.name.startswith('RV_HoodReverseRib_'):
        for sp in ob.data.splines:
            for p in sp.points:p.co.z=hood_z(p.co.x,p.co.y)-.036
    elif ob.name.startswith('RV_HoodPinstripe_'):
        for sp in ob.data.splines:
            for p in sp.points:p.co.z=hood_z(p.co.x,p.co.y)+.0025
    elif ob.name.startswith('RV_HeadlightLid_'):
        for v in ob.data.vertices:v.co.z=hood_z(v.co.x,v.co.y)+.001
        ob.data.update()
for sg,side in [(1,'L'),(-1,'R')]:
    patch('RV_FrontUpperShoulder_'+side,seq(120,.45,2.215),seq(18),lambda x,t,sg=sg:(x,sg*(.6815+(width(x)-.6815)*t),front_top(x)-.035*t*t),PAINT,root=clip,sub=0,thick=.012,orient=(0,0,1))
    cuts=sorted(set([.45,2.215,1.22-.365,1.22+.365]+seq(170,.45,2.215)))
    patch('RV_FrontFender_'+side,cuts,seq(16),lambda x,t,sg=sg:(x,sg*(width(x)-.020*(1-t)),lower_arch(x,1.22)+(front_top(x)-.035-lower_arch(x,1.22))*t),PAINT,root=clip,sub=0,thick=.012,orient=(0,sg,0))
    # Backed panel joint retains a narrow seam, not an open slit.
    path('RV_HoodEdgeGasket_'+side,[(x,sg*.680,front_top(x)-.004) for x in seq(120,.455,2.215)],.0035,TRIM,root=clip)
def nose_top(u):
    y=abs(u)*width(2.215)
    return hood_z(2.215,y) if y<=.68 else front_top(2.215)-.035*((y-.68)/(width(2.215)-.68))**2
patch('RV_NoseFascia',seq(64,-1,1),seq(14),lambda u,t:(2.235-.020*u*u,width(2.215)*u,.225+(nose_top(u)-.225)*t),PAINT,root=clip,sub=0,thick=.012,orient=(1,0,0))
patch('RV_NoseUpperReturn',seq(64,-1,1),seq(5),lambda u,t:(2.215+.020*(1-u*u)*t,width(2.215)*u,nose_top(u)),PAINT,root=clip,sub=0,thick=.006,orient=(0,0,1))
for sg in [-1,1]:
    lamp=bpy.data.objects['RV_FrontDrivingLamp_'+str(sg)];lamp.location.x+=.025
# Remove the fixed projecting cowl; the replacement stays inside the cabin.
remove('RV_Dashboard')
CURRENT=INSIDE;GROUP='interior_v12'
box('RV_Dashboard',(.333,0,.732),(.178,1.36,.104),TRIM,.018,root=offset)
for name,limit in [('RV_CabinFloor',.425),('RV_TransmissionTunnel',.405)]:
    ob=bpy.data.objects[name]
    for v in ob.data.vertices:v.co.x=min(v.co.x,limit-ob.location.x)
    ob.data.update();ob['user_spec']='Fixed cabin ends before rolling front unit; no slab projecting below the nose.'
remove('RV_SteeringColumn')
tube('RV_SteeringColumn',(.414,.37,.66),(.37,.37,.70),.029,DARK,N=32,root=offset)
for ob in INSIDE.objects:
    if ob.name.startswith('RV_Instrument_'):ob.location.x-=.10
    elif ob.name.startswith('RV_Pedal_'):ob.location.x-=.33
# A bent driving-leg pose fits the shortened fixed footwell on the same rig.
def capture():return {b.name:{p:tuple(getattr(b,p)) for p in ['location','rotation_quaternion','scale']} for b in R.pose.bones}
R['driving_pose']=0.;R.update_tag();bpy.context.view_layer.update();stand=capture()
R['driving_pose']=1.;R.update_tag();bpy.context.view_layer.update();drivepose=capture()
legnames=[part+'.'+side for side in ['L','R'] for part in ['thigh','shin','foot']]
for f in list(R.animation_data.drivers):
    if any(f.data_path.startswith('pose.bones["'+name+'"]') for name in legnames):R.animation_data.drivers.remove(f)
def setbone(name,a,b):
    bone=R.data.bones[name];a,b=Vector(a),Vector(b);q=(bone.tail_local-bone.head_local).rotation_difference(b-a)@bone.matrix_local.to_quaternion();R.pose.bones[name].matrix=Matrix.LocRotScale(a,q,Vector((1,(b-a).length/bone.length,1)));bpy.context.view_layer.update()
for sg,side in [(1,'L'),(-1,'R')]:
    hip=R.pose.bones['thigh.'+side].head.copy();knee=Vector((-.05,sg*.115,.76));ankle=Vector((.02,sg*.115,.36));toe=Vector((.16,sg*.115,.34))
    setbone('thigh.'+side,hip,knee);setbone('shin.'+side,knee,ankle);setbone('foot.'+side,ankle,toe)
seated=capture()
for name in legnames:
    pb=R.pose.bones[name]
    for prop in ['location','rotation_quaternion','scale']:
        aa=stand[name][prop];dd=list(seated[name][prop])
        if prop=='rotation_quaternion' and sum(x*y for x,y in zip(aa,dd))<0:dd=[-x for x in dd]
        for i,(a,d) in enumerate(zip(aa,dd)):drive(pb,prop,i,f'{a:.10g}+({d-a:.10g})*d',[('d',R,'driving_pose')])
# C1 longitudinal canopy: all three panels sample the same profile and normals.
nodes=[(-1.32,.85,.55),(-.72,1.17,.18),(-.52,1.205,0),(-.24,1.195,-.12),(.438,.79,-.85)]
def hermite(x):
    for (a,za,ma),(b,zb,mb) in zip(nodes,nodes[1:]):
        if x<=b:
            t=max(0,min(1,(x-a)/(b-a)));return (2*t**3-3*t*t+1)*za+(t**3-2*t*t+t)*(b-a)*ma+(-2*t**3+3*t*t)*zb+(t**3-t*t)*(b-a)*mb
    return nodes[-1][1]
def canopy_width(x):return profile(x,[(-1.32,.748),(-.72,.704),(-.24,.692),(.438,.790)])
def canopy(x,u):return Vector((x,canopy_width(x)*u,hermite(x)+.018*(1-u*u)))
CURRENT=BODY;GROUP='canopy_v12'
for name in ['RV_Windshield','RV_RoofTarga','RV_RearHatchGlass','RV_A_Pillar_-1','RV_A_Pillar_1','RV_RearWindowFrame_-1','RV_RearWindowFrame_1']:remove(name)
for name,a,b,mat in [('RV_Windshield',-.24,.438,GLASS),('RV_RoofTarga',-.72,-.24,PAINT),('RV_RearHatchGlass',-1.32,-.72,GLASS)]:
    ob=patch(name,seq(90,a,b),seq(44,-1,1),canopy,mat,root=offset,sub=0,thick=.006 if mat==GLASS else .018,orient=(0,0,1))
    normals=[]
    for v in ob.data.vertices:
        x,y,z=v.co;u=y/canopy_width(x);dx=canopy(x+.0001,u)-canopy(x-.0001,u);du=canopy(x,u+.0001)-canopy(x,u-.0001);normals.append(tuple(dx.cross(du).normalized()))
    if hasattr(ob.data,'normals_split_custom_set_from_vertices'):ob.data.normals_split_custom_set_from_vertices(normals)
    ob['user_spec']='Shared smooth C1 windshield/roof/hatch profile; not independent flat angled panels.'
for sg in [-1,1]:
    path('RV_A_Pillar_'+str(sg),[tuple(canopy(x,sg)) for x in seq(90,.438,-.24)],.017,PAINT,root=offset)
    path('RV_RearWindowFrame_'+str(sg),[tuple(canopy(x,sg)) for x in seq(80,-.72,-1.32)],.016,PAINT,root=offset)
for x,name in [(-.24,'FrontRoofSeal'),(-.72,'RearRoofSeal'),(.438,'WindshieldBaseSeal'),(-1.32,'HatchBaseSeal')]:
    path('RV_'+name,[tuple(canopy(x,u)+Vector((0,0,.001))) for u in seq(64,-1,1)],.006,TRIM,root=offset)
# Curved doors have returned edges and closely fitted jambs instead of open slits.
def belt(x):return profile(x,[(-.676,.823),(.444,.770)])
def door_point(x,t,sg,inside=False):
    u=(x+.676)/1.120;y=width(x)-.003+.065*sin(pi*t)*sin(pi*(.1+.8*u))-(.028 if inside else 0)
    z=.310+(belt(x)-.310)*t+(.002 if inside else 0);return (x,sg*y,z)
for sg,side in [(1,'L'),(-1,'R')]:
    hinge=bpy.data.objects['RV_DoorWing_Hinge_'+side];children=list(hinge.children);matrices={ob:ob.matrix_world.copy() for ob in children};hinge.location.z=.31;bpy.context.view_layer.update()
    for ob,m in matrices.items():ob.matrix_parent_inverse=hinge.matrix_world.inverted();ob.matrix_world=m
    for name in ['RV_DoorWing_Panel_'+side,'RV_DoorWing_InnerSkin_'+side,'RV_DoorWing_Glass_'+side,'RV_DoorWindowEdge_'+side]:remove(name)
    patch('RV_DoorWing_Panel_'+side,seq(56,-.676,.444),seq(22),lambda x,t,sg=sg:door_point(x,t,sg),PAINT,root=hinge,sub=0,thick=.008,orient=(0,sg,0))
    patch('RV_DoorWing_InnerSkin_'+side,seq(56,-.676,.444),seq(22),lambda x,t,sg=sg:door_point(x,t,sg,True),bpy.data.materials['RV_RedLeather'],root=hinge,sub=0,thick=.005,orient=(0,-sg,0))
    boundary=[(x,0) for x in seq(56,-.676,.444)]+[(.444,t) for t in seq(22)]+[(x,1) for x in seq(56,.444,-.676)]+[(-.676,t) for t in seq(22,1,0)]
    vv=[];ff=[]
    for x,t in boundary:vv.extend([door_point(x,t,sg),door_point(x,t,sg,True)])
    for i in range(len(boundary)-1):ff.append((2*i,2*i+1,2*i+3,2*i+2))
    mesh('RV_DoorPanelReturns_'+side,vv,ff,PAINT,root=hinge,smooth=True)
    def sideglass(u,t,sg=sg):
        xb=-.676+1.120*u;xt=-.72+1.158*u;top=canopy(xt,sg);bottom=Vector((xb,sg*(width(xb)-.017),belt(xb)+.008));p=bottom.lerp(top,t);p.y+=sg*.012*sin(pi*u)*sin(pi*t);return p
    patch('RV_DoorWing_Glass_'+side,seq(60),seq(26),sideglass,GLASS,root=hinge,sub=0,thick=.004,orient=(0,sg,0))
    points=[sideglass(0,t) for t in seq(18)]+[sideglass(u,1) for u in seq(90)]+[sideglass(1,t) for t in seq(10,1,0)]+[sideglass(u,0) for u in seq(70,1,0)]
    path('RV_DoorWindowEdge_'+side,points,.012,TRIM,root=hinge)
    for title,x in [('Rear',-.679),('Front',.447)]:
        path('RV_DoorJambSeal_'+side+'_'+title,[(x,sg*(width(x)-.004),.310+(belt(x)-.310)*t) for t in seq(30)],.004,TRIM,root=offset)
    path('RV_DoorLowerSeal_'+side,[door_point(x,0,sg) for x in seq(60,-.676,.444)],.004,TRIM,root=offset)
    handle=bpy.data.objects['RV_DoorHandle_'+side];center=Vector(door_point(-.46,(.69-.310)/(belt(-.46)-.310),sg));handle.location.y=sg*(abs(center.y)+.010)-sg*.829
    tube('RV_MirrorMount_'+side,(.40,sg*(width(.40)-.017),.78),(.40,sg*.927,.78),.012,DARK,N=24,root=hinge)
# Close the former rear deck/shoulder level mismatch and leave a cassette aperture.
CURRENT=BODY;GROUP='rear_body_v12'
remove('RV_RearDeck')
patch('RV_RearDeck',seq(70,-1.844,-1.13),seq(42,-1,1),lambda x,u:(x,.68*u,rear_top(x)+.008*(1-u*u)),PAINT,root=offset,sub=0,thick=.012,orient=(0,0,1))
for sg,side in [(1,'L'),(-1,'R')]:
    remove('RV_RearUpperShoulder_'+side);remove('RV_RearFender_'+side)
    patch('RV_RearUpperShoulder_'+side,seq(80,-1.844,-.68),seq(18),lambda x,t,sg=sg:(x,sg*(.68+(width(x)-.68)*t),rear_top(x)-.035*t*t),PAINT,root=offset,sub=0,thick=.012,orient=(0,0,1))
    cuts=sorted(set([-2.215,-.68,-1.22-.365,-1.22+.365]+seq(160,-2.215,-.68)))
    patch('RV_RearFender_'+side,cuts,seq(18),lambda x,t,sg=sg:(x,sg*(width(x)-.020*(1-t)),lower_arch(x,-1.22)+(rear_top(x)-.035-lower_arch(x,-1.22))*t),PAINT,root=offset,sub=0,thick=.012,orient=(0,sg,0))
    patch('RV_CassetteSideRail_'+side,seq(55,-2.215,-1.844),seq(5),lambda x,t,sg=sg:(x,sg*(width(x)-.018+.018*t),rear_top(x)-.052+.017*t),PAINT,root=offset,sub=0,thick=.008,orient=(0,0,1))
patch('RV_HatchLowerReturn',seq(64,-1,1),seq(5),lambda u,t:(-1.32-.035*t,canopy_width(-1.32)*u,(hermite(-1.32)+.018*(1-u*u))*(1-t)+(rear_top(-1.355)+.008*(1-min(1,abs(canopy_width(-1.32)*u)/.68)**2))*t),TRIM,root=offset,sub=0,thick=.008,orient=(0,0,1))
# The WHOLE reactor cassette rises; black bodywork is just its rounded top/sides.
old=bpy.data.objects['RV_ReactorCover_VerticalSlide']
for ob in list(old.children):bpy.data.objects.remove(ob,do_unlink=True)
bpy.data.objects.remove(old,do_unlink=True)
for ob in list(bpy.data.objects):
    if ob.name.startswith(('RV_ReactorHousing_','RV_ReactorNozzle_','RV_ReactorCore_','RV_ReactorSlideGuide_')):bpy.data.objects.remove(ob,do_unlink=True)
cassette=empty('RV_ReactorBlock_VerticalSlide',(0,0,0),parent=offset)
lift=.207;drive(cassette,'location',2,f'{lift}*t',[('t',root,'transform')]);cassette['user_spec']='One four-reactor cassette rises just enough; black skin only top and sides, continuously rounded at the corners. No independently raised lid.'
def shell_section(x):
    w=width(x)-.020;z=rear_top(x)+.008;r=.055;points=[]
    points += [(-w,z-.153),(-w,z-r)]
    points += [(-(w-r)-r*sin(a),z-r+r*cos(a)) for a in seq(14,pi/2,0)]
    points += [(y,z+.005*(1-(y/(w-r))**2)) for y in seq(50,-w+r,w-r)]
    points += [((w-r)+r*sin(a),z-r+r*cos(a)) for a in seq(14,0,pi/2)]
    points += [(w,z-.153)];return points
vv=[];ff=[];xs=seq(55,-2.228,-1.85)
for x in xs:vv += [(x,y,z) for y,z in shell_section(x)]
N=len(shell_section(xs[0]))
for i in range(len(xs)-1):
    for j in range(N-1):ff.append((i*N+j,(i+1)*N+j,(i+1)*N+j+1,i*N+j+1))
shell=mesh('RV_ReactorCassette_RoundedTopAndSides',vv,ff,PAINT,root=cassette,smooth=True);shell.modifiers.new('BodySkinThickness','SOLIDIFY').thickness=.008
shell['user_spec']='Single open-bottom/open-front/open-rear black skin; tangent quarter-round roof-to-flank transitions, radius55mm interpreted.'
# Shared metal carrier and a single nozzle-bank object, with four real apertures.
box('RV_ReactorCassette_CommonCarrier',(-2.025,0,.55),(.31,1.25,.19),DARK,.018,root=cassette)
for z in [.449,.651]:box('RV_ReactorCassette_CommonRail_'+str(z),(-2.204,0,z),(.026,1.27,.018),DARK,.004,root=cassette)
bank_v=[];bank_f=[];centers=[-.47,-.157,.157,.47]
for y in centers:
    start=len(bank_v);N=64
    for x,r in [(-2.217,.088),(-2.202,.088),(-2.202,.069),(-2.217,.069)]:
        for i in range(N):a=tau*i/N;bank_v.append((x,y+r*cos(a),.55+r*sin(a)))
    for row in range(4):
        for i in range(N):bank_f.append((start+row*N+i,start+row*N+(i+1)%N,start+((row+1)%4)*N+(i+1)%N,start+((row+1)%4)*N+i))
    tube('RV_ReactorCassette_InnerBore_'+str(y),(-2.202,y,.55),(-2.206,y,.55),.067,TRIM,N=48,root=cassette)
    tube('RV_ReactorCassette_Core_'+str(y),(-2.209,y,.55),(-2.212,y,.55),.035,ALLOY,N=40,root=cassette)
mesh('RV_ReactorCassette_FourNozzleBank',bank_v,bank_f,ALLOY,root=cassette,smooth=True)
for sg in [-1,1]:
    for x in [-2.19,-1.88]:path('RV_CassetteClosedJoint_'+str((sg,x)),[(x,sg*y,z-.004) for y,z in shell_section(x) if y>=0],.003,TRIM,root=cassette)
# Wheel guns are exactly twice the original in-rim width; channels match.
CURRENT=GEAR;GROUP='weapons_v12'
for axle,x in [('Front',1.22),('Rear',-1.22)]:
    for sg,side in [(1,'L'),(-1,'R')]:
        bar=bpy.data.objects['RV_'+axle+'HubCannon_'+side]
        for v in bar.data.vertices:v.co.z=.335+2*(v.co.z-.335)
        bar.data.update();bar['user_spec']='User requested2x width:90mm across rim plane, length unchanged, recessed at rest,45deg deployment retained.'
        for sign in [-1,1]:
            remove('RV_'+axle+'RecessedRimFace_'+side+str(sign));rr=.217;angle=math.asin(.049/rr);start,end=(angle,pi-angle) if sign>0 else (pi+angle,2*pi-angle)
            verts=[(x+rr*cos(a),sg*1.001,.335+rr*sin(a)) for a in seq(64,start,end)]
            face=mesh('RV_'+axle+'RecessedRimFace_'+side+str(sign),verts,[tuple(range(len(verts)))],ALLOY,root=bpy.data.objects['RV_'+axle+'WheelFold_'+side]);face.modifiers.new('WheelFaceWall','SOLIDIFY').thickness=.006
R['in_vehicle']=1.;R['driving_pose']=1.;R['mask_on']=False;R.update_tag();root['hover_height']=0.;S.frame_set(1);bpy.context.view_layer.update()
S['user_corrections_v12']='Compact whole reactor cassette lift, rounded black roof/sides only; flush smooth rigid hood; fixed projecting cowl/floor removed; C1 canopy; backed door/body seams;2x rim gun width.'
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Raven_V12_Assembly.blend'),compress=True)
(A/'surface_build_v12.json').write_text(json.dumps({'source':bpy.data.filepath,'session_backup':str(backup),'cassette_lift_m':lift,'cassette_nozzle_radius_m':.088,'black_shell_corner_radius_m':.055,'gun_width_m':.09,'fixed_floor_xmax_m':.425,'fixed_tunnel_xmax_m':.405,'validation':'pending evaluated geometry checks and actual renders'},indent=2))
print('RAVEN_V12_SURFACE_REFINEMENT_SAVED')
