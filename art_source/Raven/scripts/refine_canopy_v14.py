import bpy, math, json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem'); A=P/'art_source/Raven'; S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
assert not (A/'Raven_V14_Assembly.blend').exists()
assert Path(bpy.data.filepath).name=='Raven_V13_Assembly.blend', bpy.data.filepath
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(encoding='utf-8'),'<geometry>','exec'))
root=bpy.data.objects['Raven_Control'];root['hover_height']=0.;S.frame_set(1);bpy.context.view_layer.update()
CURRENT=bpy.data.collections['RV_Body'];PARENT=bpy.data.objects['RV_PresentationOffset'];GROUP='v14_canopy'
black=bpy.data.objects['RV_RoofTarga'].data.materials[0]; glass=bpy.data.objects['RV_Windshield'].data.materials[0];rubber=bpy.data.materials['RV_BlackRubberTrim']
rear=glass.copy();rear.name='RV_RearPrivacyGlass_V14'
bs=next(n for n in rear.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
bs.inputs['Base Color'].default_value=(.012,.018,.022,1);bs.inputs['Roughness'].default_value=.105
bs.inputs['Transmission Weight'].default_value=.65
rear.diffuse_color=(.012,.018,.022,1)
def remove(name):
    ob=bpy.data.objects.get(name)
    if ob:bpy.data.objects.remove(ob,do_unlink=True)
for n in ['RV_Windshield','RV_RoofTarga','RV_RearHatchGlass','RV_FrontRoofSeal','RV_RearRoofSeal','RV_WindshieldBaseSeal','RV_HatchBaseSeal','RV_RearDeck','RV_HatchLowerReturn']:
    remove(n)
for sg in [-1,1]:
    remove('RV_A_Pillar_'+str(sg));remove('RV_RearWindowFrame_'+str(sg))
wind_slope=(.79-1.19)/(.438+.18)
nodes=[(-1.815,.801,.20),(-.72,1.17,.18),(-.52,1.205,0),(-.24,1.195,-.12),(-.10,1.19+wind_slope*.08,wind_slope),(.438,.79,wind_slope)]
def height(x):
    for (a,za,ma),(b,zb,mb) in zip(nodes,nodes[1:]):
        if x<=b:
            t=max(0,min(1,(x-a)/(b-a)));return (2*t**3-3*t*t+1)*za+(t**3-2*t*t+t)*(b-a)*ma+(-2*t**3+3*t*t)*zb+(t**3-t*t)*(b-a)*mb
    return nodes[-1][1]
def cw(x):return profile(x,[(-1.815,.755),(-1.5,.790),(-.72,.704),(-.24,.692),(.438,.790)])
def canopy(x,u):
    q=max(0,min(1,(-x-.72)/1.095));crown=.018+.014*sin(pi*q)**2
    return Vector((x,cw(x)*u,height(x)+crown*(1-u*u)))
def rf(u):return -.24+.018*u*u
def rr(u):return -.72-.018*u*u
def wb(u):return .438-.105*abs(u)**4
def hb(u):return -1.815+.120*abs(u)**4
def windshield(v,u):return canopy(rf(u)*(1-v)+wb(u)*v,u)
def roof(v,u):return canopy(rr(u)*(1-v)+rf(u)*v,u)
def hatch(v,u):return canopy(rr(u)*(1-v)+hb(u)*v,u)
patch('RV_Windshield',seq(64),seq(64,-1,1),windshield,glass,thick=.006,sub=0,orient=(0,0,1))
center=patch('RV_RoofTarga',seq(26),seq(30,-1/3,1/3),roof,black,thick=.018,sub=0,orient=(0,0,1))
center['roof_width_fraction']=1/3
patch('RV_RearHatchGlass',seq(84),seq(64,-1,1),hatch,rear,thick=.008,sub=0,orient=(0,0,1))
# Roof thirds are actual parts of the corresponding doors, not independent animations.
for sg,side in [(1,'L'),(-1,'R')]:
    hinge=bpy.data.objects['RV_DoorWing_Hinge_'+side]
    wing=patch('RV_DoorRoofWing_'+side,seq(26),seq(30,sg/3,sg),roof,black,root=hinge,thick=.018,sub=0,orient=(0,0,1));wing['roof_width_fraction']=1/3
    path('RV_RoofThirdSeal_'+side,[roof(v,sg/3) for v in seq(60)],.003,rubber,root=hinge)
    path('RV_A_Pillar_'+str(sg),[windshield(v,sg) for v in seq(70)],.017,rubber)
    path('RV_RearWindowFrame_'+str(sg),[hatch(v,sg) for v in seq(90)],.016,rubber)
    def width(x):return profile(x,[(-2.225,.77),(-1.93,.88),(-1.24,.915),(-.45,.87),(.40,.85),(1.22,.905),(1.9,.86),(2.225,.76)])
    def belt(x):return profile(x,[(-.676,.823),(.444,.770)])
    # Structural black B-pillar behind each door, continuing down to the rear shoulder.
    def pillar(v,t):
        top=hatch(v,sg);x=top.x;bottom=Vector((x,sg*(width(x)-.010),profile(x,[(-1.815,.79),(-1.15,.86),(-.738,.835)])))
        return bottom.lerp(top,t)
    patch('RV_BlackRearDoorPillar_'+side,seq(66),seq(22),pillar,black,thick=.018,sub=0,orient=(0,sg,0))
    def sideglass(u,t):
        xb=-.676+1.120*u;xt=rr(sg)+(wb(sg)-rr(sg))*u;top=canopy(xt,sg);bottom=Vector((xb,sg*(width(xb)-.017),belt(xb)+.008));p=bottom.lerp(top,t);p.y+=sg*.012*sin(pi*u)*sin(pi*t);return p
    remove('RV_DoorWing_Glass_'+side);remove('RV_DoorWindowEdge_'+side)
    patch('RV_DoorWing_Glass_'+side,seq(60),seq(26),sideglass,glass,root=hinge,thick=.006,sub=0,orient=(0,sg,0))
    points=[sideglass(0,t) for t in seq(18)]+[sideglass(u,1) for u in seq(90)]+[sideglass(1,t) for t in seq(18,1,0)]+[sideglass(u,0) for u in seq(70,1,0)]
    path('RV_DoorWindowEdge_'+side,points,.012,rubber,root=hinge)
    # Short rear door post closes the gap between the door rear edge and hatch side.
    def post(t,u):
        front=sideglass(0,t);back=pillar(0,t);return front.lerp(back,u)
    patch('RV_B_Pillar_'+side,seq(28),seq(6),post,black,thick=.016,sub=0,orient=(0,sg,0))
for name,fn in [('RV_FrontRoofSeal',lambda u:roof(1,u)),('RV_RearRoofSeal',lambda u:roof(0,u)),('RV_WindshieldBaseSeal',lambda u:windshield(1,u)),('RV_HatchBaseSeal',lambda u:hatch(1,u))]:
    # Roof seals are split with the roof so the outer thirds follow doors.
    if 'RoofSeal' in name:
        for lo,hi,suffix,parent in [(-1,-1/3,'_R',bpy.data.objects['RV_DoorWing_Hinge_R']),(-1/3,1/3,'_Center',PARENT),(1/3,1,'_L',bpy.data.objects['RV_DoorWing_Hinge_L'])]:path(name+suffix,[fn(u) for u in seq(40,lo,hi)],.006,rubber,root=parent)
    else:path(name,[fn(u) for u in seq(100,-1,1)],.009,rubber)
# Rounded windshield base has a black surround, entirely behind the rotating front unit.
patch('RV_WindshieldRoundedBaseSurround',seq(18),seq(80,-1,1),lambda v,u:windshield(1,u).lerp(Vector((.443,cw(.438)*u,.787+.018*(1-u*u))),v),black,thick=.010,sub=0,orient=(0,0,1))
# Only a narrow border remains between the extended hatch and rear cassette.
patch('RV_RearDeck',seq(20),seq(80,-1,1),lambda v,u:hatch(1,u).lerp(Vector((-1.844,.86*u,.790)),v),black,thick=.012,sub=0,orient=(0,0,1))
box('RV_RearParcelShelf',(-1.19,0,.690),(1.22,1.46,.022),black,root=PARENT)
# Bowed fascia required depth occlusion as well as height: all metal behind its surface at rest.
cassette=bpy.data.objects['RV_ReactorBlock_VerticalSlide']
for ob in cassette.children:
    if ob.type=='MESH' and ob.name!='RV_ReactorCassette_RoundedTopAndSides':
        for vertex in ob.data.vertices:vertex.co.x+=.018
        ob.data.update()
S['v14_user_corrections']='Roof thirds integral to doors; curved trapezoidal windshield from s-l500 toy; rounded very dark rear hatch extending to cassette; black rear door pillars. Dimensions inferred.'
root['hover_height']=0.;S.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Raven_V14_Assembly.blend'),compress=True)
(A/'surface_build_v14.json').write_text(json.dumps({'source':bpy.data.filepath,'roof_thirds':True,'rear_glass_end_x':-1.815,'reactor_depth_correction_m':.018,'status':'saved, visual verification pending'},indent=2))
print('V14_CANOPY_SAVED')
