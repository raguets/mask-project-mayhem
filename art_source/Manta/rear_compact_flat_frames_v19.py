import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Manta';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((A/'rebuild_bindings_v15.py').read_text().split('# Front tires')[0],'<helpers>','exec'))
CURRENT=bpy.data.collections['Manta_Vehicle'];PARENT=None
glass=bpy.data.objects['MA_Windshield'].data.materials[0]
def rearx(x):return -.70+(x+.70)*.90 if x<-.70 else x
oldrx=rx;rx=rearx(rx)
# Shrink only the rear, with stable local bindings and round rear tires.
wing_states=[]
for sign in [-1,1]:
 wing=bpy.data.objects['MA_UnderbodyWingPivot_'+str(sign)];carrier=bpy.data.objects['MA_RearWheelCarrier_'+str(sign)];parts=list(wing.children);ws={o:snap(o) for o in parts if o!=carrier};wheelparts=list(carrier.children);wdata={o:snap(o) for o in wheelparts};tire=bpy.data.objects['MA_RearWheel_'+str(sign)+'_Tire'];wc=sum(wdata[tire],Vector())/len(wdata[tire]);delta=Vector((rx,sign*.83,.32))-wc
 pivot=Vector((rx-.40,sign*.98,.24));control(wing,root,pivot,{2:str(sign*pi/2)+'*t'});control(carrier,wing,Vector((rx,sign*.83,.32))-pivot)
 for o,pp in ws.items():localize(o,wing,mapdata(o,pp,lambda p:Vector((rearx(p.x),p.y,p.z))))
 for o,pp in wdata.items():localize(o,carrier,mapdata(o,pp,lambda p:p+delta))
 # Resizing the rear must not resize tire circles or the reinforced axle bearings.
wing_set=set()
for sign in [-1,1]:wing_set.update(bpy.data.objects['MA_UnderbodyWingPivot_'+str(sign)].children_recursive);wing_set.add(bpy.data.objects['MA_UnderbodyWingPivot_'+str(sign)])
tail=bpy.data.objects['MA_RearLightSpoilerHinge'];tailparts=list(tail.children);taildata={o:snap(o) for o in tailparts};engine=bpy.data.objects['MA_TripleReactorTravel'];eparts=list(engine.children);edata={o:snap(o) for o in eparts}
exclude=wing_set|set(tailparts)|set(eparts)|{tail,engine,bpy.data.objects['MA_RearBoardSlide']}
for o in list(bpy.data.collections['Manta_Vehicle'].objects)+list(bpy.data.collections['Manta_Interior'].objects):
 if o in exclude or o.type not in ['MESH','CURVE','FONT']:continue
 if o.name.startswith(('MA_RearBoardRigidLeg','MA_CircularArchLip')):continue
 pts=snap(o)
 points=pts if o.type=='MESH' else ([p for sp in pts for p in sp] if o.type=='CURVE' else [pts.translation])
 if not any(p.x<-.70 for p in points):continue
 localize(o,root,mapdata(o,pts,lambda p:Vector((rearx(p.x),p.y,p.z))))
# Circular rear arch is rebuilt, never horizontally scaled.
body=bpy.data.objects['MA_MainBody']
cut=tube('NewRearCircularWell',(rx,-1.2,.34),(rx,1.2,.34),.340,None,N=96)
def subtract(o,cut,name):
 m=o.modifiers.new(name,'BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cut;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cut,do_unlink=True)
subtract(body,cut,'NewCircularRearWell')
# Former compressed hole is smaller and lies inside the new circle: retain clean round boundary.
for o in list(bpy.data.objects):
 if o.name.startswith('MA_CircularArchLip'):bpy.data.objects.remove(o,do_unlink=True)
for x in [fx,rx]:
 for sign in [-1,1]:path('MA_CircularArchLip',[(x+.344*cos(a),sign*.89,.34+.344*sin(a)) for a in seq(64,0,pi)],.009,purple,root)
# Rear board: flush height in road, horizontal rigid legs, arc stays behind glass.
x0=rearx(-2.318);z0=.56;L=.43;base=x0+L
q='min(1,max(0,(t-.18)/.82))';sm=q+'**2*(3-2*'+q+')';root['tail_raise']=0.
drive(root,'["tail_raise"]',None,sm,[('t',root,'transform')])
carriage=bpy.data.objects['MA_RearBoardSlide'];control(carriage,root,(0,0,0))
drive(carriage,'location',0,'-.108*min(1,t/.18)-.036*r+.43*(cos(1.5707963267948966*r)-1)-.17*sin(1.5707963267948966*r)',[('t',root,'transform'),('r',root,'tail_raise')])
oldarms=bpy.data.objects.get('MA_RearBoardRigidSupportFrame')
arms=empty('MA_RearBoardRigidFrameV19');control(arms,carriage,(base,0,.39));drive(arms,'rotation_euler',1,'1.5707963267948966*r',[('r',root,'tail_raise')])
control(tail,arms,(-L,0,.17))
for o,pp in taildata.items():
 def trim(p):p.x=rearx(p.x);p.z=.39+(p.z-.39)*(.34/.446);return p
 localize(o,tail,mapdata(o,pp,trim))
for o in list(bpy.data.objects):
 if o.name.startswith('MA_RearBoardRigidLeg'):bpy.data.objects.remove(o,do_unlink=True)
if oldarms:bpy.data.objects.remove(oldarms,do_unlink=True)
for sign in [-1,1]:newbox('MA_RearBoardRigidLeg_'+str(sign),(base-L/2,sign*.60,.39),(L,.025,.28),purple,arms)
control(engine,root,(0,0,0),loc_expr={0:'-.018*t-.36*min(1,max(0,(t-.65)/.35))'})
for o,pp in edata.items():localize(o,engine,mapdata(o,pp,lambda p:Vector((rearx(p.x),p.y,p.z))))
# Short front cannon projection; nose finishes only 25mm beyond muzzle.
for sign in [-1,1]:
 gun=bpy.data.objects['MA_HeadlightCannonTravel_'+str(sign)];parts=list(gun.children);saved={o:snap(o) for o in parts};oldend=max(p.x for o,pp in saved.items() if o.type=='MESH' for p in pp);delta=Vector((2.32-oldend,0,0));control(gun,root,(0,0,0),loc_expr={0:'.20*t'})
 for o,pp in saved.items():localize(o,gun,mapdata(o,pp,lambda p:p+delta))
slide=bpy.data.objects['MA_SlidingHood'];control(slide,root,(0,0,0),loc_expr={0:'.195*t'})
# Horizontal base plus shorter guides/missiles on a separate 30-degree elevation cradle.
launcher=bpy.data.objects['MA_TripleLauncherLift'];tilt=next(o for o in launcher.children if o.type=='EMPTY')
parts=list(tilt.children);saved={o:snap(o) for o in parts};case=bpy.data.objects['MA_TripleLauncherCassette'];cp=snap(case);cx=(min(p.x for p in cp)+max(p.x for p in cp))/2;target=.73+1.62*.25+.195/2
liftq='min(1,max(0,(t-.94)/.06))';control(launcher,root,(0,0,0),loc_expr={2:'.02*t+.24*('+liftq+'**2*(3-2*'+liftq+'))'});control(tilt,launcher,(target,0,.645),{1:str(-pi/6)+'*'+liftq})
for o,pp in saved.items():
 def shortened(p):p.x=target+(p.x-cx)*.48;return p
 localize(o,launcher if o==case else tilt,mapdata(o,pp,shortened))
# Replace ALL round window tubes by broad flat stamped body bands.
for o in list(bpy.data.objects):
 if o.name.startswith(('MA_Apillar','MA_WindshieldRubber','MA_HatchSurround','MA_QuarterWindowFrame','MA_Bpillar')) or o.name in ['MA_RoofFrontCross','MA_RoofRearCross']:bpy.data.objects.remove(o,do_unlink=True)
def band(name,points,normal,width):
 pp=[]
 for p in points:
  p=Vector(p)
  if not pp or (p-pp[-1]).length>.00001:pp.append(p)
 vv=[]
 for i,p in enumerate(pp):
  tangent=(pp[min(i+1,len(pp)-1)]-pp[max(0,i-1)]).normalized();n=Vector(normal(p) if callable(normal) else normal).normalized();d=n.cross(tangent).normalized()
  vv.extend(tuple(p+d*w+n*h) for h in [-.009,.009] for w in [-width/2,width/2])
 ff=[]
 for i in range(len(pp)-1):
  a=i*4;b=a+4;ff.extend([(a,b,b+1,a+1),(a+2,a+3,b+3,b+2),(a,a+2,b+2,b),(a+1,b+1,b+3,a+3)])
 ff.extend([(0,1,3,2),tuple((len(pp)-1)*4+j for j in [0,2,3,1])]);return mesh(name,vv,ff,purple,root,bevel=.004)
def wind(t,q):return (.67-.725*t+.055*(1-q*q)+.006*sin(pi*t),(.75-.15*t)*q,.86+.361*t+.008*(1-q*q)*sin(pi*t))
for sign in [-1,1]:band('MA_FlatWindshieldSide_'+str(sign),[wind(t,sign) for t in seq(48)],(.44,0,.90),.160)
band('MA_FlatWindshieldHeader',[wind(1,q) for q in seq(48,-1,1)],(.44,0,.90),.140);band('MA_FlatWindshieldLower',[wind(0,q) for q in seq(48,-1,1)],(.44,0,.90),.100)
def hatch(t,q):return (rearx(-.76-1.36*t),(.62+.10*t)*q,1.21-.39*t+.040*sin(pi*t)+.025*(1-q*q))
for sign in [-1,1]:band('MA_FlatHatchSide_'+str(sign),[hatch(t,sign) for t in seq(48)],(-.28,0,.96),.108)
for t,n in [(0,'Header'),(1,'Lower')]:band('MA_FlatHatch'+n,[hatch(t,q) for q in seq(48,-1,1)],(-.28,0,.96),.108)
for sign in [-1,1]:
 a=Vector((rearx(-.76),sign*.62,1.21));b=Vector((-.70,sign*.84,.84));c=Vector((rearx(-2.12),sign*.72,.82));n=(b-a).cross(c-a).normalized()
 if n.y*sign<0:n=-n
 def tri(u,v):
  aa=1-u-v;p=a*aa+b*v+c*u;ac=aa+u
  if ac>.00001:p.z+=.040*ac*sin(pi*u/ac)
  p.y+=sign*.035*27*aa*v*u;return p
 band('MA_FlatQuarterUpper_'+str(sign),[tri(t,0) for t in seq(48)],n,.144);band('MA_FlatQuarterLower_'+str(sign),[tri(1-t,t) for t in seq(48)],n,.144);band('MA_FlatQuarterFront_'+str(sign),[tri(0,t) for t in seq(48)],n,.172)
root['rear_length_note']='Latest user correction: rear shortened10% around X=-.70, glazing/lights/details retained; rear tires remain circular and recentered on rebuilt circular arches.'
root['window_frames_note']='Four glazing outlines now broad FLAT 18mm-deep body bands: windshield sides160mm/header140mm, hatch108mm, quarter144mm/front172mm. Replaces all tubular outlines.'
root['nose_extension_note']='Fixed cannon muzzles X2.52m, moving hammer tipX2.545m, just25mm beyond. Slider195mm. Launcher base shortened48%, remains horizontal; three guides/missiles elevate30deg after bay clearance.'
root['rear_board_note']='Road board top at body height~.73m, horizontal rigid arms below lamps. During deployment board kept aft of hatch, centre~.82m just above jets. Hidden carriage motion estimated to support visible rigid-arm path.'
for o in bpy.data.objects:
 if o.type=='MESH':o.data.update()
 o.update_tag()
R['driving_pose']=1.;R['in_vehicle']=1.;R['mask_on']=False;R.update_tag();S.frame_set(121);S.frame_set(1);bpy.context.view_layer.update()
D['rear_axle_x']=rx;D['rear_reduction_factor']=.90;(A/'proportions_v19.json').write_text(json.dumps(D,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Manta_V19_Assembly.blend'),compress=True)
print('V19_REAR10_FLAT_FRAMES_SHORT_NOSE_SAVED')
