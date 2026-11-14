"""Stable local pivots: rebuild bindings, never globally rescale parent inverses."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Manta';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
root=bpy.data.objects['Manta_Control'];R=bpy.data.objects['VanessaWarfield_Rig'];S.frame_set(1);bpy.context.view_layer.update()
D=json.loads((A/'proportions_v13.json').read_text());fx=D['front_axle_x'];rx=D['rear_axle_x']
CURRENT=bpy.data.collections['Manta_Vehicle'];PARENT=None
purple=bpy.data.objects['MA_MainBody'].data.materials[0];metal=bpy.data.objects['MA_MainWing_1'].data.materials[0];black=bpy.data.objects['MA_Underbody'].data.materials[0];silver=next(m for m in bpy.data.materials if m.name.startswith('MA_Alloy'))
def snap(o):
 M=o.matrix_world.copy()
 if o.type=='MESH':return [M@v.co for v in o.data.vertices]
 if o.type=='CURVE':return [[M@Vector(v.co[:3]) for v in sp.points] for sp in o.data.splines]
 return M
def localize(o,parent,points):
 o.parent=parent;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=Matrix.Identity(4);bpy.context.view_layer.update();inv=parent.matrix_world.inverted()
 if o.type=='MESH':
  for v,p in zip(o.data.vertices,points):v.co=inv@p
 elif o.type=='CURVE':
  for sp,pp in zip(o.data.splines,points):
   for v,p in zip(sp.points,pp):v.co=(*(inv@p),1)
 else:o.matrix_basis=inv@points
 o.update_tag()
def control(o,parent,pos,rot=None,loc_expr=None):
 o.parent=parent;o.matrix_parent_inverse=Matrix.Identity(4);o.rotation_mode='XYZ';o.scale=(1,1,1)
 for i in range(3):drive(o,'location',i,(loc_expr or {}).get(i,str(pos[i])),[('t',root,'transform')]);drive(o,'rotation_euler',i,(rot or {}).get(i,'0'),[('t',root,'transform')])
 o.update_tag();bpy.context.view_layer.update()
def mapdata(o,points,fn):
 if o.type=='MESH':return [fn(p.copy()) for p in points]
 if o.type=='CURVE':return [[fn(p.copy()) for p in sp] for sp in points]
 m=points.copy();m.translation=fn(m.translation);return m
def newbox(name,p,d,mat,parent):
 o=box(name,p,d,mat,.012);pts=snap(o);localize(o,parent,pts);return o
def newtube(name,a,b,r,mat,parent,**kwargs):
 o=tube(name,a,b,r,mat,**kwargs);pts=snap(o);localize(o,parent,pts);return o
# Front tires and their winglets: exact measured axle centre, circular fender.
for sign in [-1,1]:
 flip=bpy.data.objects['MA_FrontWheelFlip_'+str(sign)];parts=list(flip.children);saved={o:snap(o) for o in parts};tire=bpy.data.objects['MA_FrontWheel_'+str(sign)+'_Tire'];centre=sum(saved[tire],Vector())/len(saved[tire]);delta=Vector((fx,sign*.83,.32))-centre
 control(flip,root,(fx,sign*.80,.34),{0:str(sign*pi)+'*t'})
 for o in parts:
  pts=mapdata(o,saved[o],lambda p:p+delta)
  if o.type=='MESH' and o.name.startswith('MA_FrontGunWing'):
   outer=max(sign*p.y for p in pts)
   for p in pts:p.y=sign*(outer+(sign*p.y-outer)*1.50)
  localize(o,flip,pts)
# Main wings: wider, farther aft, fully tucked inside rear-tire inner faces.
for sign in [-1,1]:
 wing=bpy.data.objects['MA_UnderbodyWingPivot_'+str(sign)];carrier=bpy.data.objects['MA_RearWheelCarrier_'+str(sign)];parts=list(wing.children);saved={o:snap(o) for o in parts if o!=carrier};wheelparts=list(carrier.children);wdata={o:snap(o) for o in wheelparts};tire=bpy.data.objects['MA_RearWheel_'+str(sign)+'_Tire'];wc=sum(wdata[tire],Vector())/len(wdata[tire]);delta=Vector((rx,sign*.83,.32))-wc
 main=bpy.data.objects['MA_MainWing_'+str(sign)];mv=saved[main];xmin=min(p.x for p in mv);xmax=max(p.x for p in mv);ymin=min(sign*p.y for p in mv);ymax=max(sign*p.y for p in mv)
 pivot=Vector((rx-.40,sign*.98,.24));control(wing,root,pivot,{2:str(sign*pi/2)+'*t'})
 control(carrier,wing,Vector((rx,sign*.83,.32))-pivot)
 def fit(p):p.x=-2.29+(p.x-xmin)*3.07/(xmax-xmin);p.y=sign*(sign*p.y-ymin)*.72/(ymax-ymin);return p
 for o in parts:
  if o==carrier:continue
  if o.name.startswith(('MA_RearWheelWingBridge','MA_RearWheelBearing','MA_RearWheelCarrierGusset','MA_MainWingForwardCannon','MA_MainWingCannonBore')):bpy.data.objects.remove(o,do_unlink=True);continue
  pts=saved[o]
  if o==main or o.name.startswith(('MA_WingPanelLine','MA_AileronSeam')):pts=mapdata(o,pts,fit)
  elif o.type=='FONT':pts=mapdata(o,pts,lambda p:Vector((.28,sign*.30,.132)))
  localize(o,wing,pts)
 for o in wheelparts:localize(o,carrier,mapdata(o,wdata[o],lambda p:p+delta))
 newbox('MA_RearWheelWingBridge_'+str(sign),(rx-.13,sign*.80,.29),(.26,.135,.14),metal,wing)
 newtube('MA_RearWheelBearing_'+str(sign),(rx,sign*.68,.32),(rx,sign*.85,.32),.103,metal,wing,N=48)
 vv=[(x,sign*y,z) for y in [.62,.81] for x,z in [(rx-.38,.125),(rx+.02,.125),(rx+.02,.34),(rx-.22,.37)]]
 o=mesh('MA_RearWheelCarrierGusset_'+str(sign),vv,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],metal,bevel=.013);localize(o,wing,snap(o))
 newtube('MA_MainWingForwardCannon_'+str(sign),(.20,sign*.34,.09),(.20,0,.09),.020,metal,wing)
 newtube('MA_MainWingCannonBore_'+str(sign),(.20,sign*.002,.09),(.20,sign*.001,.09),.013,black,wing)
# Light board correctly behind all stowed jets (negative X = rear).
carriage=bpy.data.objects['MA_RearBoardSlide'];board=bpy.data.objects['MA_RearLightSpoilerHinge'];boardparts=list(board.children);bsnap={o:snap(o) for o in boardparts};bp=bpy.data.objects['MA_RearLightPanel'];bc=sum(bsnap[bp],Vector())/len(bsnap[bp]);delta=Vector((-2.318,0,.61))-bc
q='min(1,max(0,(t-.18)/.82))';s=q+'**2*(3-2*'+q+')'
control(carriage,root,(0,0,0),loc_expr={0:'-.16*min(1,t/.18)'})
control(board,carriage,(-2.318,0,.61),{1:str(pi/2)+'*('+s+')'},{2:'.61+.47*('+s+')'})
for o in boardparts:localize(o,board,mapdata(o,bsnap[o],lambda p:p+delta))
for o in list(bpy.data.objects):
 if o.name.startswith(('MA_RearBoardLowerLeg','MA_RearBoardMiddleLeg','MA_RearBoardUpperLeg','MA_RearBoardMiddleStage','MA_RearBoardUpperStage','MA_RearBoardGuideRail')):bpy.data.objects.remove(o,do_unlink=True)
for sign in [-1,1]:
 newbox('MA_RearBoardLowerLeg_'+str(sign),(-2.318,sign*.60,.47),(.28,.025,.18),purple,carriage)
 mid=empty('MA_RearBoardMiddleStage_'+str(sign));control(mid,carriage,(0,0,0),loc_expr={2:'.21*('+s+')'});newbox('MA_RearBoardMiddleLeg_'+str(sign),(-2.318,sign*.60,.47),(.24,.021,.26),purple,mid)
 upper=empty('MA_RearBoardUpperStage_'+str(sign));control(upper,carriage,(0,0,0),loc_expr={2:'.47*('+s+')'});newbox('MA_RearBoardUpperLeg_'+str(sign),(-2.318,sign*.60,.485),(.20,.017,.36),purple,upper)
engine=bpy.data.objects['MA_TripleReactorTravel'];parts=list(engine.children);es={o:snap(o) for o in parts};rearmin=min(p.x for o,pp in es.items() if o.type=='MESH' for p in pp);delta=Vector((-2.20-rearmin,0,0));control(engine,root,(0,0,0),loc_expr={0:'-.42*t'})
for o in parts:localize(o,engine,mapdata(o,es[o],lambda p:p+delta))
# Rebuild the seats with real local geometry, avoiding rotation about world origin.
CURRENT=bpy.data.collections['Manta_Interior'];seatmat=bpy.data.objects['MA_SeatBase_1'].data.materials[0]
for o in list(CURRENT.objects):
 if o.name.startswith(('MA_SeatBase','MA_SeatBack','MA_Headrest','MA_SeatStitch','MA_SeatPedestal')):bpy.data.objects.remove(o,do_unlink=True)
for sign in [-1,1]:
 newbox('MA_SeatBase_'+str(sign),(-.35,sign*.37,.345),(.52,.46,.09),seatmat,root)
 vv=[(x,sign*.37+y,z) for y in [-.23,.23] for x,z in [(-.59,.40),(-.50,.40),(-.57,.98),(-.66,.98)]]
 o=mesh('MA_SeatBack_'+str(sign),vv,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],seatmat,root,bevel=.035)
 newbox('MA_Headrest_'+str(sign),(-.62,sign*.37,1.055),(.11,.27,.16),seatmat,root)
 newbox('MA_SeatPedestal_'+str(sign),(-.35,sign*.37,.265),(.40,.36,.05),seatmat,root)
R.animation_data.drivers.find('location',index=0).driver.expression='-.40*v';R.animation_data.drivers.find('location',index=1).driver.expression='.37*v';R.update_tag()
# Flat roof link and lower, genuinely tapered, transversely curved windshield.
CURRENT=bpy.data.collections['Manta_Vehicle'];glass=bpy.data.objects['MA_Windshield'].data.materials[0]
for o in list(bpy.data.objects):
 if o.name in ['MA_TbarRoof','MA_RoofFrontCross','MA_Windshield'] or o.name.startswith(('MA_WindshieldRubber','MA_Apillar','MA_Wiper')):bpy.data.objects.remove(o,do_unlink=True)
newbox('MA_TbarRoof',(-.542,0,1.233),(.98,.23,.055),purple,root);newbox('MA_RoofFrontCross',(-.055,0,1.226),( .075,1.27,.070),purple,root)
def wind(t,q):return (.67-.725*t+.055*(1-q*q)+.006*sin(pi*t),(.75-.15*t)*q,.86+.361*t+.008*(1-q*q)*sin(pi*t))
patch('MA_Windshield',seq(32),seq(40,-1,1),wind,glass,root,sub=1,thick=.007,orient=(1,0,1))
outline=[wind(0,q) for q in seq(40,-1,1)]+[wind(t,1) for t in seq(32)]+[wind(1,q) for q in seq(40,1,-1)]+[wind(t,-1) for t in seq(32,1,0)]
path('MA_WindshieldRubber',outline,.011,black,root)
for sign in [-1,1]:path('MA_Apillar',[wind(t,sign) for t in seq(32)],.027,purple,root)
for q0 in [-.35,.35]:path('MA_Wiper',[tuple(Vector(wind(t,q0+.20*t))+Vector((.006,0,0))) for t in seq(12,.025,.34)],.005,black,root)
# All THREE rear windows are curved, but the surrounding volume stays slim.
for o in list(bpy.data.objects):
 if o.name.startswith(('MA_RearHatchGlass','MA_RearLouvre','MA_HatchSurround','MA_QuarterGlass','MA_QuarterWindowFrame','MA_RearQuarterRoofEdge','MA_Bpillar')):bpy.data.objects.remove(o,do_unlink=True)
def hatch(t,q):return (-1.08-1.04*t,(.62+.10*t)*q,1.21-.39*t+.040*sin(pi*t)+.025*(1-q*q))
patch('MA_RearHatchGlass',seq(32),seq(32,-1,1),hatch,glass,root,sub=1,thick=.006,orient=(-1,0,1))
outline=[hatch(0,q) for q in seq(32,-1,1)]+[hatch(t,1) for t in seq(32)]+[hatch(1,q) for q in seq(32,1,-1)]+[hatch(t,-1) for t in seq(32,1,0)]
path('MA_HatchSurround',outline,.027,purple,root)
for i in range(13):path('MA_RearLouvre_%02d'%i,[tuple(Vector(hatch(.04+.92*i/12,q))+Vector((0,0,.012))) for q in seq(24,-1,1)],.011,black,root)
for sign in [-1,1]:
 a=Vector((-1.08,sign*.62,1.21));b=Vector((-.995,sign*.84,.84));c=Vector((-2.12,sign*.72,.82))
 def tri(u,v):
  aa=1-u-v;p=a*aa+b*v+c*u;ac=aa+u
  if ac>.00001:p.z+=.040*ac*sin(pi*u/ac)
  p.y+=sign*.035*27*aa*v*u
  return p
 N=24;vv=[];index={}
 for i in range(N+1):
  for j in range(N+1-i):index[i,j]=len(vv);vv.append(tuple(tri(i/N,j/N)))
 ff=[]
 for i in range(N):
  for j in range(N-i):
   ff.append((index[i,j],index[i+1,j],index[i,j+1]))
   if j<N-i-1:ff.append((index[i+1,j],index[i+1,j+1],index[i,j+1]))
 o=mesh('MA_QuarterGlass_'+str(sign),vv,ff,glass,root,smooth=True,orient=(0,sign,0));o.modifiers.new('GlassThickness','SOLIDIFY').thickness=.006
 outline=[tri(t,0) for t in seq(32)]+[tri(1-t,t) for t in seq(32)]+[tri(0,1-t) for t in seq(32)]
 path('MA_QuarterWindowFrame',outline,.024,purple,root);path('MA_Bpillar',[tuple(b.lerp(a,t)) for t in seq(20)],.032,purple,root)
root['binding_note']='V15 uses explicit local coordinates with identity parent inverse and constant rest-position drivers. No global re-scaling of inverse matrices. Tires centred on circular arches.'
root['roof_note']='Open above seats, no upper door rails; horizontal T link and lowered trapezoidal windshield, width 1.50m base / 1.20m top, true 55mm transverse crown.'
root['wing_storage_note']='Main root chord .72m; stored |Y|<=.72 versus tire inner face .725, X[-2.29,.78]; aft pivots at rear axle-.40m, roots pass under body when deployed. Main/front winglets +50% over preceding widths.'
root['tail_support_note']='Two supports doubled fore/aft .28/.24/.20m, only .025/.021/.017m thick left/right. Single light board covers jets at rest.'
R['driving_pose']=1.;R['in_vehicle']=1.;R['mask_on']=False;R.update_tag();S.frame_set(121);S.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Manta_V15_Assembly.blend'),compress=True)
print('V15_LOCAL_BINDINGS_REBUILT')
