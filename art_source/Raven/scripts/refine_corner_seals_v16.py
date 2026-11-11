import bpy,math
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Raven';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
assert Path(bpy.data.filepath).name=='Raven_V15_Assembly.blend'
assert not (A/'Raven_V16_Assembly.blend').exists()
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(encoding='utf-8'),'<geometry>','exec'))
root=bpy.data.objects['Raven_Control'];root['hover_height']=0.;S.frame_set(1);bpy.context.view_layer.update()
CURRENT=bpy.data.collections['RV_Body'];PARENT=bpy.data.objects['RV_PresentationOffset'];GROUP='v16_corner_seals'
rubber=bpy.data.materials['RV_BlackRubberTrim']
code=(A/'scripts/refine_canopy_v14.py').read_text(encoding='utf-8');exec(code[code.index('wind_slope='):code.index("patch('RV_Windshield'")])
def width(x):return profile(x,[(-2.225,.77),(-1.93,.88),(-1.24,.915),(-.45,.87),(.40,.85),(1.22,.905),(1.9,.86),(2.225,.76)])
def belt(x):return profile(x,[(-.676,.823),(.444,.770)])
def inner(v):return 1/3+.095*v
def sideglass(u,t,sg):
    xb=-.676+1.120*u;xt=rr(sg)+(wb(sg)-rr(sg))*u;top=canopy(xt,sg);bottom=Vector((xb,sg*(width(xb)-.017),belt(xb)+.008));p=bottom.lerp(top,t);p.y+=sg*.012*sin(pi*u)*sin(pi*t);return p
def fillet(v,t,sg):
    roof_end=(rf(sg)-rr(sg))/(wb(sg)-rr(sg));a=roof(v,sg*.92);b=roof(v,sg);c=sideglass(v*roof_end,.90,sg)
    return (1-t)**2*a+2*t*(1-t)*b+t*t*c
def roofedge(end,u):
    if abs(u)<=.92:return roof(end,u)
    return fillet(end,(abs(u)-.92)/.08,1 if u>0 else -1)
def corrected(fn,end,v,u):return fn(v,u)+(roofedge(end,u)-fn(0,u))*(1-v)**3
# Both fixed glazed panels meet the rounded door roof without leftover raised corners.
for name,fn,end,rows in [('RV_Windshield',windshield,1,64),('RV_RearHatchGlass',hatch,0,84)]:
    ob=bpy.data.objects[name]
    for i,vert in enumerate(ob.data.vertices):vert.co=corrected(fn,end,(i//65)/rows,-1+2*(i%65)/64)
    ob.data.update()
for sg,side in [(1,'L'),(-1,'R')]:
    for name,end,fn in [('RV_A_Pillar_'+str(sg),1,windshield),('RV_RearWindowFrame_'+str(sg),0,hatch)]:
        ob=bpy.data.objects[name]
        for sp in ob.data.splines:
            N=len(sp.points)-1
            for i,p in enumerate(sp.points):p.co=(*corrected(fn,end,i/N,sg),1)
    for end,label in [(0,'Rear'),(1,'Front')]:
        ob=bpy.data.objects.get('RV_DoorRoofBendReturn_'+label+'_'+side)
        if ob:bpy.data.objects.remove(ob,do_unlink=True)
        name=('RV_RearRoofSeal' if end==0 else 'RV_FrontRoofSeal')+'_'+side
        ob=bpy.data.objects[name];bpy.data.objects.remove(ob,do_unlink=True)
        points=[roof(end,sg*u) for u in seq(35,inner(end),.92)]+[fillet(end,t,sg) for t in seq(30)]
        path(name,points,.006,rubber,root=bpy.data.objects['RV_DoorWing_Hinge_'+side])
    delta=roofedge(0,sg)-roof(0,sg)
    ob=bpy.data.objects['RV_BlackRearDoorPillar_'+side]
    # 67 rows longitudinally,23 vertices bottom-to-top per row.
    for i,v in enumerate(ob.data.vertices):v.co+=delta*(1-(i//23)/66)**3*((i%23)/22)
    ob.data.update()
    ob=bpy.data.objects['RV_B_Pillar_'+side]
    for i,v in enumerate(ob.data.vertices):v.co+=delta*((i//7)/28)
    ob.data.update()
S['v16_corner_seals']='Fixed windshield/rear glass upper corners and black rear pillar follow the rounded door roof bends. Removed old raised corner returns and joined seal ends.'
S.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Raven_V16_Assembly.blend'),compress=True)
print('V16_CORNER_SEALS_SAVED')
