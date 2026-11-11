import bpy,math,json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Raven';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
assert not (A/'Raven_V13_Assembly.blend').exists()
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(encoding='utf-8'),'<geometry>','exec'))
root=bpy.data.objects['Raven_Control'];root['hover_height']=0.;S.frame_set(1);bpy.context.view_layer.update()
offset=bpy.data.objects['RV_PresentationOffset'];cassette=bpy.data.objects['RV_ReactorBlock_VerticalSlide'];BODY=bpy.data.collections['RV_Body'];CURRENT=BODY;PARENT=None;GROUP='v13_refinement'
def oldtop(x):return profile(x,[(-2.225,.67),(-1.8,.79),(-1.15,.86),(-.6,.82),(.35,.77)])
def width(x):return profile(x,[(-2.225,.77),(-1.93,.88),(-1.24,.915),(-.45,.87),(.40,.85),(1.22,.905),(1.9,.86),(2.225,.76)])
def lower(x):return .335+math.sqrt(max(0,.365**2-(x+1.22)**2)) if abs(x+1.22)<.365 else .22
# Flat horizontal cassette top and level tail; the entire jet bank moves together.
shell=bpy.data.objects['RV_ReactorCassette_RoundedTopAndSides']
for v in shell.data.vertices:
    w=width(v.co.x)-.020;delta=v.co.z-(oldtop(v.co.x)+.008)
    v.co.z=.79 if abs(v.co.y)<=w-.055+1e-6 and delta>=-.001 else .79+delta
shell.data.update();shell['user_spec']='Horizontal black top at0.79m closed, continuously rounded into sides; the complete four-reactor cassette rises together.'
for ob in cassette.children:
    if ob==shell:continue
    if ob.type=='MESH':
        for v in ob.data.vertices:v.co.z+=.13
        ob.data.update()
    elif ob.type=='CURVE':
        for sp in ob.data.splines:
            for p in sp.points:p.co.z+=.79-(oldtop(p.co.x)+.008)
drive(cassette,'location',2,'.197*t',[('t',root,'transform')])
cassette['user_spec']='Complete four-reactor cassette rises197mm, only9mm clearance over the fixed rear fascia. Horizontal rounded black roof/sides; no separate lid.'
fascia=bpy.data.objects['RV_RearFascia']
for v in fascia.data.vertices:v.co.z=.24+(v.co.z-.24)*(.54/.42)
fascia.data.update()
for side in ['L','R']:
    ob=bpy.data.objects['RV_RearFender_'+side]
    for i,v in enumerate(ob.data.vertices):
        if v.co.x>=-1.844:continue
        t=(i%19)/18;v.co.z=lower(v.co.x)+(.79-.035-lower(v.co.x))*t
    ob.data.update()
    ob=bpy.data.objects['RV_CassetteSideRail_'+side]
    for v in ob.data.vertices:v.co.z+=.79-oldtop(v.co.x)
    ob.data.update()
# Shorter gentle fillet: most of the windscreen remains a near-plane.
wind_slope=(.79-1.19)/(.438+.18)
nodes=[(-1.32,.85,.55),(-.72,1.17,.18),(-.52,1.205,0),(-.24,1.195,-.12),(-.10,1.19+wind_slope*.08,wind_slope),(.438,.79,wind_slope)]
def height(x):
    for (a,za,ma),(b,zb,mb) in zip(nodes,nodes[1:]):
        if x<=b:
            t=max(0,min(1,(x-a)/(b-a)));return (2*t**3-3*t*t+1)*za+(t**3-2*t*t+t)*(b-a)*ma+(-2*t**3+3*t*t)*zb+(t**3-t*t)*(b-a)*mb
    return nodes[-1][1]
def cw(x):return profile(x,[(-1.32,.748),(-.72,.704),(-.24,.692),(.438,.790)])
def canopy(x,u):return Vector((x,cw(x)*u,height(x)+.018*(1-u*u)))
for name in ['RV_Windshield','RV_RoofTarga','RV_RearHatchGlass']:
    ob=bpy.data.objects[name]
    for v in ob.data.vertices:v.co.z=canopy(v.co.x,v.co.y/cw(v.co.x)).z
    ob.data.update();normals=[]
    for v in ob.data.vertices:
        x,y,z=v.co;u=y/cw(x);dx=canopy(x+.0001,u)-canopy(x-.0001,u);du=canopy(x,u+.0001)-canopy(x,u-.0001);normals.append(tuple(dx.cross(du).normalized()))
    if hasattr(ob.data,'normals_split_custom_set_from_vertices'):ob.data.normals_split_custom_set_from_vertices(normals)
for sg,side in [(1,'L'),(-1,'R')]:
    ob=bpy.data.objects['RV_A_Pillar_'+str(sg)]
    for sp in ob.data.splines:
        for p in sp.points:p.co.z=canopy(p.co.x,sg).z
    def belt(x):return profile(x,[(-.676,.823),(.444,.770)])
    def sideglass(u,t):
        xb=-.676+1.120*u;xt=-.72+1.158*u;top=canopy(xt,sg);bottom=Vector((xb,sg*(width(xb)-.017),belt(xb)+.008));p=bottom.lerp(top,t);p.y+=sg*.012*sin(pi*u)*sin(pi*t);return p
    ob=bpy.data.objects['RV_DoorWing_Glass_'+side]
    for i,v in enumerate(ob.data.vertices):v.co=sideglass((i//27)/60,(i%27)/26)
    ob.data.update();old=bpy.data.objects['RV_DoorWindowEdge_'+side];parent=old.parent;bpy.data.objects.remove(old,do_unlink=True)
    points=[sideglass(0,t) for t in seq(18)]+[sideglass(u,1) for u in seq(90)]+[sideglass(1,t) for t in seq(10,1,0)]+[sideglass(u,0) for u in seq(70,1,0)]
    path('RV_DoorWindowEdge_'+side,points,.012,bpy.data.materials['RV_BlackRubberTrim'],root=parent)
R=bpy.data.objects['CalhounBurns_Rig'];R['driving_pose']=1.;R['in_vehicle']=1.;R['mask_on']=False;R.update_tag();root['hover_height']=0.;S.frame_set(1);bpy.context.view_layer.update()
S['user_corrections_v13']='Reduced windshield/roof fillet; lifting rear cassette roof and rear end horizontal. All four jets and common carrier rise with rounded black roof/sides.'
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Raven_V13_Assembly.blend'),compress=True)
(A/'surface_build_v13.json').write_text(json.dumps({'source':bpy.data.filepath,'cassette_lift_m':.197,'cassette_roof_z_m':.79,'fixed_rear_fascia_top_m':.78,'nozzle_center_closed_z_m':.68,'windshield_fillet_x_range_m':[-.24,-.10],'gun_width_m':.09,'validation':'pending final renders and checks'},indent=2))
print('RAVEN_V13_FLAT_REAR_AND_GENTLER_CANOPY_SAVED')
