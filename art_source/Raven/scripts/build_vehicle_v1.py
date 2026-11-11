"""Execute INSIDE Blender through MCP. Reference-based editable Corvette/Raven study."""
import bpy,math,json,random
from mathutils import Vector,Matrix
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Raven';S=bpy.context.scene
assert not bpy.data.objects.get('Raven_Control')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(encoding='utf-8'),'<shared-geometry>','exec'))
BODY=collection('RV_Body');GEAR=collection('RV_RunningGear');INSIDE=collection('RV_Interior');WEAPONS=collection('RV_Weapons');STUDIO=collection('RV_Studio')
CURRENT=BODY;PARENT=None;GROUP='body'
root=empty('Raven_Control');root['transform']=0.;root['disc_launch']=0.;root['hover_height']=0.;root['dimensions_note']='Estimated 4.45m x1.82m body, 2.44m wheelbase. No official dimensions asserted.'
for k in ['transform','disc_launch']:root.id_properties_ui(k).update(min=0,max=1)
root.id_properties_ui('hover_height').update(min=0,max=5,description='Presentation height only; not flight or flotation physics')
drive(root,'location',2,'h',[('h',root,'hover_height')]);PARENT=root
PAINT=material('RV_Obsidian_Clearcoat',(.012,.016,.022),.7,.23);p=next(n for n in PAINT.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Coat Weight'].default_value=.65;p.inputs['Coat Roughness'].default_value=.13
TRIM=material('RV_BlackRubberTrim',(.009,.011,.013),.05,.55)
RUBBER=material('RV_TireRubber',(.018,.020,.023),0,.72)
ALLOY=material('RV_BrushedAlloy',(.43,.48,.53),.86,.26)
DARK=material('RV_Gunmetal',(.038,.046,.054),.78,.35)
RED=material('RV_RedLeather',(.24,.012,.018),0,.46)
ORANGE=material('RV_OrangeWeaponDisc',(.8,.10,.012),.25,.31)
PIN=material('RV_RedPinstripe',(.63,.025,.018),.3,.25)
WHITE=material('RV_SilverPinstripe',(.68,.72,.75),.6,.24)
GLASS=material('RV_TintedGlass',(.23,.34,.39),0,.11);pg=next(n for n in GLASS.node_tree.nodes if n.type=='BSDF_PRINCIPLED');pg.inputs['Transmission Weight'].default_value=1;pg.inputs['IOR'].default_value=1.45
TAIL=material('RV_RubyLens',(.42,.006,.009),.2,.22)
HEAD=material('RV_HeadlampGlass',(.61,.68,.70),.15,.18)
def width(x):return profile(x,[(-2.225,.77),(-1.93,.88),(-1.24,.915),(-.45,.87),(.40,.85),(1.22,.905),(1.9,.86),(2.225,.76)])
def top(x):return profile(x,[(-2.225,.67),(-1.8,.79),(-1.15,.86),(-.6,.82),(.35,.77),(1.25,.74),(1.8,.66),(2.225,.46)])
def surface(x,u):return top(x)-.055*(abs(u)**2)
def outside_arch(x,z):return all((x-ax)**2+(z-.335)**2>.365**2 or z<.335 for ax in [-1.22,1.22])
# Continuous editable front/rear fenders, with actual open wheel wells.
for sg,label in [(1,'L'),(-1,'R')]:
    for title,a,b in [('Front',.45,2.215),('Rear',-2.215,-.68)]:
        patch('RV_'+title+'Fender_'+label,seq(144,a,b),seq(20),lambda x,t,sg=sg:(x,sg*(width(x)-.035*(1-t)),.22+(top(x)-.22)*t),PAINT,orient=(0,sg,0),skip=lambda x,t:not outside_arch(x,.22+(top(x)-.22)*t))
        patch('RV_'+title+'UpperShoulder_'+label,seq(72,a,b),seq(8),lambda x,t,sg=sg:(x,sg*(.68+(width(x)-.68)*t),top(x)-.055*t*t),PAINT,orient=(0,0,1))
    for ax in [-1.22,1.22]:
        patch('RV_InnerWheelArch_'+label+'_'+str(ax),seq(64,0,pi),[0,1],lambda t,v,sg=sg,ax=ax:(ax+.365*cos(t),sg*(.64+.245*v),.335+.365*sin(t)),TRIM,thick=.008,orient=(0,-sg,0))
    box('RV_RockerSill_'+label,(-.10,sg*.86,.245),(1.12,.09,.12),PAINT,.022)
    # Functional doors carry their glazing outward to become wings.
    hinge=empty('RV_DoorWing_Hinge_'+label,(0,sg*.87,.34),parent=root)
    drive(hinge,'rotation_euler',0,f'{-sg*80*pi/180}*t',[('t',root,'transform')])
    patch('RV_DoorWing_Panel_'+label,seq(40,-.66,.44),seq(15),lambda x,t,sg=sg:(x,sg*(.87-.055*t),.35+.39*t),PAINT,root=hinge,orient=(0,sg,0))
    patch('RV_DoorWing_InnerSkin_'+label,seq(30,-.63,.42),seq(12),lambda x,t,sg=sg:(x,sg*(.837-.055*t),.36+.36*t),RED,root=hinge,orient=(0,-sg,0))
    patch('RV_DoorWing_Glass_'+label,seq(30),seq(12),lambda u,v,sg=sg:(-.64+1.05*u+(.16-.67*u)*v,sg*(.812-.125*v),.752+.37*v),GLASS,root=hinge,orient=(0,sg,0),thick=.005,sub=0)
    path('RV_DoorWindowEdge_'+label,[(-.64,sg*.812,.752),(-.48,sg*.687,1.122),(-.10,sg*.687,1.122),(.41,sg*.812,.752)],.014,TRIM,root=hinge)
    box('RV_DoorHandle_'+label,(-.46,sg*.829,.69),(.145,.019,.028),DARK,.005,root=hinge)
    mirror=box('RV_MirrorHousing_'+label,(.40,sg*.945,.78),(.20,.13,.075),PAINT,.028,root=hinge)
    box('RV_MirrorGlass_'+label,(.326,sg*.948,.785),(.007,.10,.045),ALLOY,.007,root=hinge)
    # A red/silver narrow livery follows the body rather than a mesh projection.
    for dy,mat in [(0,PIN),(.015,WHITE)]:
        path('RV_RearPinstripe_'+label+'_'+str(dy),[(x,sg*(width(x)+.005),top(x)-.14+dy+.014*sin((x+2.2)*12)) for x in seq(70,-2.16,-.72)],.0035,mat)
# Hood with independent longitudinal flip. Both surfaces remain editable.
hood=empty('RV_Hood_LongitudinalPivot',(1.32,0,.71),parent=root)
drive(hood,'rotation_euler',0,f'{pi}*t',[('t',root,'transform')])
patch('RV_Hood_OuterSkin',seq(100,.46,2.215),seq(36,-1,1),lambda x,u:(x,.675*u,surface(x,u)),PAINT,root=hood,orient=(0,0,1),thick=.018)
patch('RV_Hood_ReverseArmor',seq(60,.48,2.19),seq(26,-1,1),lambda x,u:(x,.658*u,surface(x,u)-.026),DARK,root=hood,orient=(0,0,-1),thick=.008)
for y in [-.50,-.24,0,.24,.50]:
    path('RV_HoodReverseRib_'+str(y),[(x,y,surface(x,y/.675)-.046) for x in seq(50,.58,2.05)],.012,TRIM,root=hood)
for sg in [-1,1]:
    for yy,mat in [(.22,PIN),(.239,WHITE)]:
        path('RV_HoodPinstripe_'+str((sg,yy)),[(x,sg*(yy+.025*sin((x-.5)*9)),surface(x,yy/.675)+.006) for x in seq(90,.59,2.1)],.0035,mat,root=hood)
    # Retractable-light lids are closed in road mode; driving lamps remain in nose.
    patch('RV_HeadlightLid_'+str(sg),seq(12,1.53,1.95),seq(8),lambda x,t,sg=sg:(x,sg*(.46+.17*t),surface(x,(.46+.17*t)/.675)+.005),PAINT,root=hood,sub=0)
# Low pointed fascia, disc launcher slot and lower intake.
patch('RV_NoseFascia',seq(30,-1,1),seq(8),lambda u,t:(2.225-.055*abs(u),.76*u,.24+.22*t),PAINT,orient=(1,0,0))
box('RV_FrontDiscLaunchSlot',(2.232,0,.388),(.016,.53,.046),TRIM,.005)
box('RV_LowerNoseIntake',(2.234,0,.28),(.016,.74,.063),TRIM,.006)
for sg in [-1,1]:
    box('RV_FrontDrivingLamp_'+str(sg),(2.206,sg*.57,.32),(.027,.24,.073),HEAD,.011)
    box('RV_SideMarker_'+str(sg),(1.89,sg*.864,.39),(.16,.015,.035),ORANGE,.007)
patch('RV_RearDeck',seq(40,-2.2,-1.13),seq(30,-1,1),lambda x,u:(x,.68*u,top(x)-.025*u*u),PAINT,orient=(0,0,1))
# Fixed rear lamp fascia. Cover above the lamps opens to reveal FOUR thrusters.
patch('RV_RearFascia',seq(36,-1,1),seq(10),lambda u,t:(-2.225+.035*u*u,.77*u,.24+.42*t),PAINT,orient=(-1,0,0))
for sg in [-1,1]:
    for y in [.43,.64]:tube('RV_RoundRearLamp_'+str((sg,y)),(-2.231,sg*y,.545),(-2.247,sg*y,.545),.083,TAIL,N=48)
    box('RV_RearReflector_'+str(sg),(-2.235,sg*.48,.35),(.018,.31,.038),TAIL,.006)
    tube('RV_Exhaust_'+str(sg),(-2.15,sg*.55,.245),(-2.29,sg*.55,.245),.037,DARK,N=28)
box('RV_RearLicenseBacking',(-2.248,0,.45),(.017,.29,.15),TRIM,.014)
cover=empty('RV_ReactorCover_Hinge',(-1.72,0,.81),parent=root)
drive(cover,'rotation_euler',1,f'{55*pi/180}*t',[('t',root,'transform')])
box('RV_ReactorCover',(-2.02,0,.82),(.59,1.45,.055),PAINT,.018,root=cover)
for y in [-.47,-.157,.157,.47]:
    tube('RV_ReactorHousing_'+str(y),(-1.88,y,.72),(-2.19,y,.72),.105,DARK,r2=.12,N=48)
    tube('RV_ReactorNozzle_'+str(y),(-2.195,y,.72),(-2.205,y,.72),.087,TRIM,N=48)
    tube('RV_ReactorCore_'+str(y),(-2.211,y,.72),(-2.215,y,.72),.048,ALLOY,N=32)
# Cabin: swept windshield, roof/T-bar, hatch and continuous floor.
patch('RV_Windshield',seq(36,-1,1),seq(20),lambda u,t:(.47-.61*t-.045*u*u,(.78-.10*t)*u,.78+.38*t+.02*(1-u*u)),GLASS,orient=(1,0,1),thick=.005)
for sg in [-1,1]:path('RV_A_Pillar_'+str(sg),[(.48,sg*.797,.78),(-.14,sg*.692,1.16)],.023,PAINT)
patch('RV_RoofTarga',seq(25,-.58,-.14),seq(26,-1,1),lambda x,u:(x,.697*u,1.17+.025*(1-u*u)),PAINT,orient=(0,0,1),thick=.02)
patch('RV_RearHatchGlass',seq(28),seq(30,-1,1),lambda t,u:(-.60-.64*t,(.697+.045*t)*u,1.15-.29*t+.014*(1-u*u)),GLASS,orient=(-1,0,1),thick=.005)
for sg in [-1,1]:path('RV_RearWindowFrame_'+str(sg),[(-.60,sg*.706,1.15),(-1.25,sg*.75,.86)],.023,PAINT)
CURRENT=INSIDE;GROUP='interior'
box('RV_CabinFloor',(-.13,0,.22),(1.95,1.44,.10),DARK,.015)
box('RV_RearCabinBulkhead',(-1.08,0,.62),(.10,1.38,.68),TRIM,.02)
box('RV_TransmissionTunnel',(-.12,0,.38),(1.53,.24,.30),TRIM,.04)
box('RV_Dashboard',(.48,0,.69),(.32,1.43,.20),TRIM,.035)
for sg,label in [(1,'Driver'),(-1,'Passenger')]:
    box('RV_'+label+'SeatPan',(-.48,sg*.37,.37),(.56,.49,.14),RED,.055)
    back=box('RV_'+label+'SeatBack',(-.79,sg*.37,.65),(.15,.49,.58),RED,.045)
    center=Vector((-.79,sg*.37,.65));rotation=Matrix.Rotation(-.15,3,'Y')
    for v in back.data.vertices:v.co=center+rotation@(v.co-center)
    box('RV_'+label+'Headrest',(-.82,sg*.37,.93),(.14,.28,.17),RED,.035)
    for sy in [-1,1]:box('RV_'+label+'SeatBolster_'+str(sy),(-.47,sg*.37+sy*.23,.44),(.48,.06,.13),RED,.025)
    path('RV_SeatStitch_'+label,[(-.7,sg*.37-.16,.455),(-.27,sg*.37-.16,.455)],.0018,WHITE)
def ring(name,center,axis,radius,minor,mat,root=None,N=64,M=12):
    c=Vector(center);q=Vector(axis).to_track_quat('Z','Y');vv=[];ff=[]
    for i in range(N):
        a=i*tau/N
        for j in range(M):
            b=j*tau/M;vv.append(tuple(c+q@Vector(((radius+minor*cos(b))*cos(a),(radius+minor*cos(b))*sin(a),minor*sin(b)))))
    for i in range(N):
        for j in range(M):ff.append((i*M+j,((i+1)%N)*M+j,((i+1)%N)*M+(j+1)%M,i*M+(j+1)%M))
    return mesh(name,vv,ff,mat,root=root,smooth=True)
tau=2*pi
wheelcenter=(.19,.37,.70);axis=(1,0,.32)
ring('RV_SteeringWheel',wheelcenter,axis,.16,.018,TRIM)
tube('RV_SteeringColumn',(.45,.37,.60),wheelcenter,.034,DARK)
for a in [0,2*pi/3,4*pi/3]:tube('RV_SteeringSpoke_'+str(a),wheelcenter,(.19,.37+.14*cos(a),.70+.14*sin(a)),.009,DARK,N=16)
for y in [.30,.42,.54]:box('RV_Instrument_'+str(y),(.307,y,.765),(.011,.08,.048),DARK,.004)
tube('RV_ShiftLever',(-.03,0,.51),(-.02,0,.64),.013,DARK,N=20)
box('RV_ShiftKnob',(-.02,0,.65),(.044,.044,.05),TRIM,.015)
for y in [.31,.46]:box('RV_Pedal_'+str(y),(.53,y,.29),(.12,.075,.018),DARK,.006)
CURRENT=GEAR;GROUP='runninggear'
for ax,label in [(1.22,'Front'),(-1.22,'Rear')]:
    for sg,side in [(1,'L'),(-1,'R')]:
        py,pz=(.3725,.4125) if ax>0 else (.5475,.4325)
        fold=empty('RV_'+label+'WheelFold_'+side,(ax,sg*py,pz),parent=root)
        angle=(sg if ax>0 else -sg)*pi/2
        drive(fold,'rotation_euler',0,f'{angle}*t',[('t',root,'transform')])
        # Tire built as a rounded cross section revolved about its real axle.
        vv=[];ff=[];N=96
        sections=[(-.113,.225),(-.121,.267),(-.10,.315),(-.072,.335),(.072,.335),(.10,.315),(.121,.267),(.113,.225)]
        for yy,rr in sections:
            for i in range(N):a=tau*i/N;vv.append((ax+rr*cos(a),sg*(.87+yy),.335+rr*sin(a)))
        for j in range(len(sections)):
            for i in range(N):ff.append((j*N+i,j*N+(i+1)%N,((j+1)%len(sections))*N+(i+1)%N,((j+1)%len(sections))*N+i))
        mesh('RV_'+label+'Tire_'+side,vv,ff,RUBBER,root=fold,smooth=True)
        for i in range(60):
            a=tau*i/60
            for band in [-.052,.052]:
                aa=a+(0.014 if band<0 else -.014)
                tread=box('RV_Tread_'+label+side+str((i,band)),(ax+.336*cos(aa),sg*(.87+band),.335+.336*sin(aa)),(.027,.071,.009),RUBBER,.001,root=fold)
                # Local Z points radially outward.
                center=Vector((ax+.336*cos(aa),sg*(.87+band),.335+.336*sin(aa)));rotation=Matrix.Rotation(pi/2-aa,3,'Y')
                for v in tread.data.vertices:v.co=center+rotation@(v.co-center)
        tube('RV_'+label+'BrakeDisc_'+side,(ax,sg*.915,.335),(ax,sg*.925,.335),.19,DARK,N=64,root=fold)
        ring('RV_'+label+'AlloyLip_'+side,(ax,sg*.985,.335),(0,1,0),.229,.013,ALLOY,root=fold)
        tube('RV_'+label+'Hub_'+side,(ax,sg*.97,.335),(ax,sg*1.002,.335),.072,ALLOY,N=40,root=fold)
        for j in range(5):
            a=tau*j/5
            tube('RV_'+label+'AlloySpoke_'+side+str(j),(ax+.065*cos(a),sg*.985,.335+.065*sin(a)),(ax+.215*cos(a+.15),sg*.985,.335+.215*sin(a+.15)),.023,ALLOY,N=12,root=fold)
            tube('RV_'+label+'Lug_'+side+str(j),(ax+.045*cos(a),sg*1.004,.335+.045*sin(a)),(ax+.045*cos(a),sg*1.012,.335+.045*sin(a)),.009,DARK,N=12,root=fold)
        gun=empty('RV_'+label+'HubCannonSlide_'+side,(ax,sg*1.02,.335),parent=fold)
        drive(gun,'location',1,f'{sg*1.02}+{sg*.075}*t',[('t',root,'transform')])
        box('RV_'+label+'HubCannon_'+side,(ax,sg*1.04,.335),(.09,.085,.075),TRIM,.008,root=gun)
        tube('RV_'+label+'HubCannonBore_'+side,(ax,sg*1.08,.335),(ax,sg*1.087,.335),.021,DARK,N=20,root=gun)
        tube('RV_'+label+'SuspensionLink_'+side,(ax,sg*py,pz),(ax,sg*.87,.335),.025,DARK,N=24,root=fold)
CURRENT=WEAPONS;GROUP='weapons'
discroot=empty('RV_DiscLaunch_Control',(1.93,0,.39),parent=root)
drive(discroot,'location',0,'1.93+3.5*d',[('d',root,'disc_launch')])
verts=[];faces=[];N=96
for zz in [-.012,.012]:
    for i in range(N):a=tau*i/N;rr=.192 if i%3==0 else .177;verts.append((1.93+rr*cos(a),rr*sin(a),.39+zz))
faces=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,N+(i+1)%N,N+i) for i in range(N)]
mesh('RV_PersistentSerratedDisc',verts,faces,ORANGE,root=discroot,bevel=.001)
# Studio is independent of the editable vehicle source.
CURRENT=STUDIO;PARENT=None;GROUP='presentation'
FLOOR=material('RV_StudioFloor',(.065,.075,.087),.1,.52)
box('RV_ReviewFloor',(0,0,-.045),(200,200,.08),FLOOR,.001)
world=bpy.data.worlds.new('RV_StudioWorld');world.use_nodes=True;bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.32,.39,.50,1);bg.inputs[1].default_value=.55;S.world=world
for name,loc,energy,size in [('Key',(2.5,-4.5,6),1700,4),('Fill',(-1,5,4),1300,3),('Rim',(-4,-1,4),1800,3)]:
    light=bpy.data.lights.new('RV_'+name,'AREA');light.energy=energy;light.shape='DISK';light.size=size;o=bpy.data.objects.new('RV_'+name,light);STUDIO.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,.6))-o.location).to_track_quat('-Z','Y').to_euler()
camera=bpy.data.cameras.new('RV_ReviewCamera');o=bpy.data.objects.new('RV_ReviewCamera',camera);STUDIO.objects.link(o);o.location=(6,-6,3.2);o.rotation_euler=(Vector((0,0,.65))-o.location).to_track_quat('-Z','Y').to_euler();camera.lens=53;S.camera=o
S.render.engine='CYCLES';S.cycles.samples=24;S.cycles.use_denoising=True
S.render.resolution_x=1280;S.render.resolution_y=900;S.render.resolution_percentage=100
S.view_settings.view_transform='AgX'
for f,v in [(1,0.),(31,0.),(121,1.),(151,1.)]:root['transform']=v;root.keyframe_insert(data_path='["transform"]',frame=f)
S.frame_end=210;S.frame_set(1);root['disc_launch']=0;root['hover_height']=0
S['reference_note']='Supplied Raven toys/cartoon + Corvette C4 photographs. Fiche transformation.txt read first. Hidden geometry, dimensions and cockpit interpreted with user approval 2026-11-11.'
bpy.context.view_layer.update()
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':area.spaces.active.shading.type='SOLID'
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Raven_V1_VehicleStudy.blend'),compress=True)
(A/'vehicle_build_v1.json').write_text(json.dumps({'objects':len(S.objects),'tire_objects':[o.name for o in S.objects if 'Tire_' in o.name],'source':bpy.data.filepath,'validation':'pending actual renders and collision review'},indent=2))
print('RAVEN_VEHICLE_STUDY_SAVED',len(S.objects))
