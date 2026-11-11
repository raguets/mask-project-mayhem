import bpy,math,json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Raven';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
assert Path(bpy.data.filepath).name=='Raven_V14_Assembly.blend'
assert not (A/'Raven_V15_Assembly.blend').exists()
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(encoding='utf-8'),'<geometry>','exec'))
root=bpy.data.objects['Raven_Control'];root['hover_height']=0.;S.frame_set(1);bpy.context.view_layer.update()
CURRENT=bpy.data.collections['RV_Body'];PARENT=bpy.data.objects['RV_PresentationOffset'];GROUP='v15_rounded_door_roof'
black=bpy.data.objects['RV_RoofTarga'].data.materials[0];glass=bpy.data.objects['RV_Windshield'].data.materials[0];rubber=bpy.data.materials['RV_BlackRubberTrim']
code=(A/'scripts/refine_canopy_v14.py').read_text(encoding='utf-8');exec(code[code.index('wind_slope='):code.index("patch('RV_Windshield'")])
def remove(name):
    ob=bpy.data.objects.get(name)
    if ob:bpy.data.objects.remove(ob,do_unlink=True)
def inner(v):return 1/3+.095*v
remove('RV_RoofTarga')
center=patch('RV_RoofTarga',seq(40),seq(40,-1,1),lambda v,u:roof(v,u*inner(v)),black,thick=.018,sub=0,orient=(0,0,1));center['roof_width_fraction']=1/3
def width(x):return profile(x,[(-2.225,.77),(-1.93,.88),(-1.24,.915),(-.45,.87),(.40,.85),(1.22,.905),(1.9,.86),(2.225,.76)])
def belt(x):return profile(x,[(-.676,.823),(.444,.770)])
for sg,side in [(1,'L'),(-1,'R')]:
    hinge=bpy.data.objects['RV_DoorWing_Hinge_'+side]
    def sideglass(u,t):
        xb=-.676+1.120*u;xt=rr(sg)+(wb(sg)-rr(sg))*u;top=canopy(xt,sg);bottom=Vector((xb,sg*(width(xb)-.017),belt(xb)+.008));p=bottom.lerp(top,t);p.y+=sg*.012*sin(pi*u)*sin(pi*t);return p
    roof_end=(rf(sg)-rr(sg))/(wb(sg)-rr(sg))
    def tmax(u):
        q=max(0,min(1,(u-roof_end)/(1-roof_end)));return .90+.10*q*q*(3-2*q)
    def fillet(v,t):
        a=roof(v,sg*.92);b=roof(v,sg);c=sideglass(v*roof_end,.90)
        return (1-t)**2*a+2*t*(1-t)*b+t*t*c
    for n in ['RV_DoorRoofWing_','RV_RoofThirdSeal_','RV_DoorWing_Glass_','RV_DoorWindowEdge_']:remove(n+side)
    wing=patch('RV_DoorRoofWing_'+side,seq(40),seq(38),lambda v,u:roof(v,sg*(inner(v)+(.92-inner(v))*u)),black,root=hinge,thick=.018,sub=0,orient=(0,0,1));wing['roof_width_fraction']=1/3;wing['front_narrowing_fraction']=.095;wing['rounded_outer_edge']=True
    path('RV_RoofThirdSeal_'+side,[roof(v,sg*inner(v)) for v in seq(75)],.003,rubber,root=hinge)
    patch('RV_DoorGlassRoof_RoundedBend_'+side,seq(64),seq(24),fillet,black,root=hinge,thick=.012,sub=0,orient=(0,sg,1))
    # Rounded bend joins tangentially to the trimmed glass and to the roof skin.
    glass_us=sorted(set(seq(90)+[roof_end]))
    patch('RV_DoorWing_Glass_'+side,glass_us,seq(36),lambda u,t:sideglass(u,t*tmax(u)),glass,root=hinge,thick=.006,sub=0,orient=(0,sg,0))
    points=[sideglass(0,t) for t in seq(18,0,.90)]+[sideglass(u,tmax(u)) for u in glass_us]+[sideglass(1,t) for t in seq(20,1,0)]+[sideglass(u,0) for u in seq(70,1,0)]
    path('RV_DoorWindowEdge_'+side,points,.006,rubber,root=hinge)
    for end,label in [(0,'Rear'),(1,'Front')]:
        # Close the return ends of the formed roof bend, no exposed triangular slit.
        curve=[fillet(end,t) for t in seq(32)];verts=[roof(end,sg)]+curve;faces=[(0,i+1,i+2) for i in range(len(curve)-1)]
        mesh('RV_DoorRoofBendReturn_'+label+'_'+side,verts,faces,black,root=hinge,smooth=True)
    for suffix in ['_Center','_L','_R']:
        for name in ['RV_FrontRoofSeal','RV_RearRoofSeal']:remove(name+suffix)
# Seal divisions follow the new tapered inner edge.
for end,name in [(0,'RV_RearRoofSeal'),(1,'RV_FrontRoofSeal')]:
    w=inner(end)
    for lo,hi,suffix,parent in [(-.92,-w,'_R',bpy.data.objects['RV_DoorWing_Hinge_R']),(-w,w,'_Center',PARENT),(w,.92,'_L',bpy.data.objects['RV_DoorWing_Hinge_L'])]:path(name+suffix,[roof(end,u) for u in seq(45,lo,hi)],.006,rubber,root=parent)
S['v15_user_correction']='Rounded formed bend between door glass and roof wing; outer roof wings taper towards the front by an additional0.095 roof half-width. Estimated fillet geometry.'
S.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Raven_V15_Assembly.blend'),compress=True)
print('V15_ROUNDED_TAPERED_DOOR_ROOF_SAVED')
