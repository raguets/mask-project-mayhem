import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Manta';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
prefix=(A/'rebuild_bindings_v15.py').read_text().split('# Front tires')[0]
exec(compile(prefix,'<local_binding_helpers>','exec'))
CURRENT=bpy.data.collections['Manta_Vehicle'];PARENT=None
glass=bpy.data.objects['MA_Windshield'].data.materials[0];lensmat=next(m for m in bpy.data.materials if m.name.startswith('MA_HeadlightLens'));tailmat=next(m for m in bpy.data.materials if m.name.startswith('MA_RedTailLens'));amber=next(m for m in bpy.data.materials if m.name.startswith('MA_AmberLamps'));lime=next(m for m in bpy.data.materials if m.name.startswith('MA_LimeGraphics'))
# Strictly convex longitudinal bonnet; small curvature increase toward front.
H0=.73;H1=2.35
def hoodz(x,y):
 u=max(0,min(1,(x-H0)/(H1-H0)))
 return .875-.025*u-.305*u*u-.005*u**5-.035*(y/.70)**2
def width(x):
 u=max(0,min(1,(x-H0)/(H1-H0)))
 return .33 if u<.86 else .33+.21*min(1,(u-.86)/.10)
quarter=H0+(H1-H0)*.25
for o in list(bpy.data.objects):
 if o.name in ['MA_SlidingHoodSkin','MA_FixedHoodRearQuarter','MA_FixedHoodShoulder_L','MA_FixedHoodShoulder_R'] or o.name.startswith(('MA_HoodHiddenJointUnderlap','MA_FixedHoodWellWall')):bpy.data.objects.remove(o,do_unlink=True)
slide=bpy.data.objects['MA_SlidingHood'];control(slide,root,(0,0,0),loc_expr={0:'.44*t'})
def skin(name,xa,xb,side,parent):
 xs=sorted(set(seq(44,xa,xb)+[x for x in [H0+(H1-H0)*.86,H0+(H1-H0)*.96] if xa<x<xb]));K=18;vv=[]
 for x in xs:
  w=width(x);lo,hi=(-w,w) if side==0 else ((w+.0015,.67) if side==1 else (-.67,-w-.0015));yy=seq(15,lo,hi)
  vv.extend((x,y,hoodz(x,y)) for y in yy);th=.050 if side else .060-.033*max(0,min(1,((x-H0)/(H1-H0)-.80)/.20));vv.extend([(x,hi,hoodz(x,hi)-th),(x,lo,hoodz(x,lo)-th)])
 ff=[tuple(reversed(range(K))),tuple((len(xs)-1)*K+i for i in range(K))]+[(j*K+i,j*K+(i+1)%K,(j+1)*K+(i+1)%K,(j+1)*K+i) for j in range(len(xs)-1) for i in range(K)]
 o=mesh(name,vv,ff,purple,smooth=True,bevel=.002);localize(o,parent,snap(o));return o
skin('MA_FixedHoodRearQuarter',H0,quarter-.0015,0,root);skin('MA_SlidingHoodSkin',quarter,H1,0,slide);skin('MA_FixedHoodShoulder_L',H0,H1,1,root);skin('MA_FixedHoodShoulder_R',H0,H1,-1,root)
# New matching clean fenders, circular wheel openings unchanged.
old=bpy.data.objects['MA_MainBody'];bpy.data.objects.remove(old,do_unlink=True)
xs=seq(96,-2.28,2.35);vv=[];K=20
for x in xs:
 w=profile(x,[(-2.28,.76),(-2.05,.86),(-1.45,.89),(-.5,.88),(.6,.87),(1.45,.88),(2.35,.79)]);lo=profile(x,[(-2.28,.25),(-.4,.24),(.6,.24),(2.35,.28)]);hi=hoodz(x,.67) if x>=H0 else profile(x,[(-2.28,.73),(-2.05,.80),(-1.45,.86),(-.5,.84),(.6,.84),(H0,hoodz(H0,.67))]);r=min(.060,(hi-lo)*.20)
 for cy,cz,a,b in [(w-r,lo+r,-pi/2,0),(w-r,hi-r,0,pi/2),(-w+r,hi-r,pi/2,pi),(-w+r,lo+r,pi,3*pi/2)]:
  for angle in seq(4,a,b):vv.append((x,cy+r*cos(angle),cz+r*sin(angle)))
ff=[tuple(reversed(range(K))),tuple((len(xs)-1)*K+i for i in range(K))]+[(j*K+i,j*K+(i+1)%K,(j+1)*K+(i+1)%K,(j+1)*K+i) for j in range(len(xs)-1) for i in range(K)]
body=mesh('MA_MainBody',vv,ff,purple,root,smooth=True,bevel=.010)
def subtract(o,cut,name):
 m=o.modifiers.new(name,'BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cut;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cut,do_unlink=True)
def cutbox(name,lo,hi):return box(name,tuple((lo[i]+hi[i])/2 for i in range(3)),tuple(hi[i]-lo[i] for i in range(3)),None,0)
subtract(body,cutbox('CabinCut',(-1.40,-.70,.43),(.55,.70,1.9)),'OpenCabin')
subtract(body,cutbox('HoodCut',(H0-.03,-.6675,.39),(2.40,.6675,1.8)),'FunctionalHoodWell')
subtract(body,cutbox('JetCut',(-2.40,-.53,.38),(-1.60,.53,.73)),'JetWell')
for x in [fx,rx]:subtract(body,tube('ArchCut',(x,-1.2,.34),(x,1.2,.34),.340,None,N=96),'RoundWheelArch')
# Rigid supports are horizontal when stored, and pivot upright as a single frame.
carriage=bpy.data.objects['MA_RearBoardSlide'];board=bpy.data.objects['MA_RearLightSpoilerHinge'];boardchildren=list(board.children);saved={o:snap(o) for o in boardchildren};oldcentre=sum(saved[bpy.data.objects['MA_RearLightPanel']],Vector())/len(saved[bpy.data.objects['MA_RearLightPanel']]);delta=Vector((-2.318,0,.61))-oldcentre
q='min(1,max(0,(t-.18)/.82))';smooth=q+'**2*(3-2*'+q+')'
for o in list(bpy.data.objects):
 if o.name.startswith(('MA_RearBoardLowerLeg','MA_RearBoardMiddleLeg','MA_RearBoardUpperLeg','MA_RearBoardMiddleStage','MA_RearBoardUpperStage')):bpy.data.objects.remove(o,do_unlink=True)
arms=empty('MA_RearBoardRigidSupportFrame');control(arms,carriage,(-1.80,0,.61),{1:str(pi/2)+'*('+smooth+')'})
control(board,arms,(-.518,0,0))
for o in boardchildren:localize(o,board,mapdata(o,saved[o],lambda p:p+delta))
for sign in [-1,1]:
 newbox('MA_RearBoardRigidLeg_'+str(sign),(-2.059,sign*.60,.61),(.518,.025,.28),purple,arms)
 subtract(body,cutbox('SupportChannel',(-2.34,sign*.60-.023,.45),(-1.63,sign*.60+.023,.84)),'HiddenRigidSupportChannel')
# Rounded ascending rear board edges and taller lamp faces following that edge.
for o in list(board.children):
 if o.type in ['MESH','CURVE'] and o.name.startswith(('MA_RearLightPanel','MA_Tail')):bpy.data.objects.remove(o,do_unlink=True)
def edge(z):return .775-.035*max(0,min(1,(z-.39)/.44))**2
outline=[(y,.39) for y in seq(24,-.775,.775)]+[(edge(z),z) for z in seq(24,.39,.83)]+[(y,.83+.006*(1-(y/.74)**2)) for y in seq(24,.74,-.74)]+[(-edge(z),z) for z in seq(24,.83,.39)]
n=len(outline);verts=[(-2.318+dx,y,z) for dx in [-.032,.032] for y,z in outline];faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
o=mesh('MA_RearLightPanel',verts,faces,purple,smooth=True,bevel=.006);localize(o,board,snap(o))
for sign in [-1,1]:
 for name,lo,hi,mat in [('Red',.38,.69,tailmat),('Reverse',.29,.36,lensmat),('Amber',.70,.77,amber)]:
  vv=[];rows=seq(16,.58,.79)
  for z in rows:
   outer=min(hi,edge(z)-.007);vv.extend([(-2.354,sign*lo,z),(-2.354,sign*outer,z)])
  o=mesh('MA_Tail'+name+'_'+str(sign),vv,[(i*2,i*2+1,i*2+3,i*2+2) for i in range(len(rows)-1)],mat,smooth=True,bevel=.002,orient=(-1,0,0));o.modifiers.new('LensThickness','SOLIDIFY').thickness=.003;localize(o,board,snap(o))
  for z in seq(9,.588,.782):
   o=path('MA_TailLensRibs',[(-2.358,sign*lo,z),(-2.358,sign*min(hi,edge(z)-.007),z)],.0013,metal);localize(o,board,snap(o))
newbox('MA_TailCentreBlackGrille',(-2.353,0,.685),(.005,.48,.21),black,board)
for z in seq(11,.59,.78):
 o=path('MA_TailGrilleSlat',[(-2.357,-.235,z),(-2.357,.235,z)],.0018,metal);localize(o,board,snap(o))
# Exact short independent front-cannon bores in the newly curved fixed shoulders.
for o in list(bpy.data.objects):
 if o.name.startswith('MA_HeadlightPortRim'):bpy.data.objects.remove(o,do_unlink=True)
for sign,l in [(1,'L'),(-1,'R')]:
 gun=bpy.data.objects['MA_HeadlightCannonTravel_'+str(sign)];parts=list(gun.children);pts={o:snap(o) for o in parts};xmax=max(p.x for o,pp in pts.items() if o.type=='MESH' for p in pp);xmin=min(p.x for o,pp in pts.items() if o.type=='MESH' for p in pp);control(gun,root,(0,0,0),loc_expr={0:'.20*t'})
 for o in parts:localize(o,gun,pts[o])
 portx=xmax+.020
 for ob in [bpy.data.objects['MA_FixedHoodShoulder_'+l],body]:subtract(ob,cutbox('HeadlightRectangularBore',(xmin-.02,sign*.53-.11,.545),(portx+.24,sign*.53+.11,.615)),'OpenFixedHeadlightBore')
 for zz in [.542,.618]:newbox('MA_HeadlightPortRim',(portx,sign*.53,zz),(.010,.232,.006),purple,root)
 for yy in [-.113,.113]:newbox('MA_HeadlightPortRim',(portx,sign*.53+yy,.58),(.010,.006,.070),purple,root)
# Seam underlaps and front skin agree with the single convex bonnet function.
for sign in [-1,1]:
 vv=[];xs=seq(60,quarter,H1)
 for x in xs:
  w=width(x)
  for y in [w-.016,w+.016]:vv.append((x,sign*y,hoodz(x,sign*y)-.064))
 o=mesh('MA_HoodHiddenJointUnderlap',vv,[(i*2,i*2+1,i*2+3,i*2+2) for i in range(len(xs)-1)],purple,root,bevel=.001)
o=bpy.data.objects['MA_IntegratedRoundedNose']
for v in o.data.vertices:
 v.co.x=H1+.001
 if v.co.z>.30:v.co.z=hoodz(H1,v.co.y)-(.027 if abs(v.co.y)<=.54 else .050)-.0015
# Correct logos: new fonts placed directly on the evaluated upper blade plane.
for o in list(bpy.data.objects):
 if o.name.startswith('MA_WingVENOM'):bpy.data.objects.remove(o,do_unlink=True)
for sign in [-1,1]:
 wing=bpy.data.objects['MA_UnderbodyWingPivot_'+str(sign)];o=text('MA_WingVENOM_'+str(sign),'VENOM',(.05,sign*.22,.131),.084,lime,rot=(0,0,0 if sign==1 else pi));bpy.context.view_layer.update();localize(o,wing,snap(o))
# Thickened windshield and quarter-window pillars, without introducing door-top rails.
for o in bpy.data.objects:
 if o.type=='CURVE' and o.name.startswith('MA_Apillar'):o.data.bevel_depth=.040
 if o.type=='CURVE' and o.name.startswith('MA_QuarterWindowFrame'):o.data.bevel_depth=.036
 if o.type=='CURVE' and o.name.startswith('MA_Bpillar'):o.data.bevel_depth=.043
# A few millimetres of bearing clearance during the front wheel roll, preserving round arches.
for sign in [-1,1]:bpy.data.objects['MA_FrontWheelFlip_'+str(sign)].animation_data.drivers.find('location',index=2).driver.expression='.34-.006*sin(3.141592653589793*t)'
# Same pilot and meshes; move wrists/ankles to the corrected forward seat.
piece=(A/'finish_consolidated_v14.py').read_text().split('# Re-solve the SAME')[1].split("root['hood_note']")[0]
piece='# Re-solve the SAME'+piece;piece=piece.replace('(.73,sign*.105,.85)','(.64,sign*.105,.85)').replace('(.48,sign*.13,1.34)','(.38,sign*.13,1.34)')
exec(compile(piece,'<forward_seat_pose>','exec'))
root['hood_curve_note']='Single strictly convex centreline z=.875-.025u-.305u²-.005u⁵, u=0..1. Curvature increases gently toward front, no concave terminal return.'
root['rear_board_note']='Two rigid broad fore/aft bars lie horizontally stored, first slide aft, then pivot upright. Board follows same rigid frame; no telescopic columns and nothing protrudes above stowed lamps. Black centre grille and rounded ascending outer lamp edges.'
for o in bpy.data.objects:
 if o.type=='MESH':o.data.update()
 o.update_tag()
R['driving_pose']=1.;R['in_vehicle']=1.;R['mask_on']=False;R.update_tag();S.frame_set(121);S.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Manta_V17_Assembly.blend'),compress=True)
print('V17_ALL_REMARKS_CONSOLIDATED')
