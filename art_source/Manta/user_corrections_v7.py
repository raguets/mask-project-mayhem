import bpy,math,json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Manta';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
root=bpy.data.objects['Manta_Control'];R=bpy.data.objects['VanessaWarfield_Rig'];S.frame_set(1)
CURRENT=bpy.data.collections['Manta_Vehicle'];PARENT=root
purple=bpy.data.objects['MA_MainBody'].data.materials[0];metal=bpy.data.objects['MA_MainWing_1'].data.materials[0];black=bpy.data.objects['MA_Underbody'].data.materials[0]
# Open tops: no glass above the seats and no upper door/window rail.
for ob in list(bpy.data.objects):
 if ob.name.startswith(('MA_TtopGlass','MA_RoofSideRail')):bpy.data.objects.remove(ob,do_unlink=True)
for s in [-1,1]:path('MA_RearQuarterRoofEdge',[(-.90,s*.68,1.29),(-1.87,s*.79,.86)],.035,purple)
root['roof_note']='User correction 2026-11-14: open above seats, no upper door window frame; central T bar and windshield/rear header retained.'
# Shorter bob: ends sit near upper shoulders rather than below them.
for ob in bpy.data.collections['Vanessa_Character'].objects:
 if ob.type=='MESH' and ob.name.startswith('VW_SweptLock'):
  for v in ob.data.vertices:
   t=max(0,min(1,(1.60-v.co.z)/.28));v.co.z+=.085*t
R['hair_note']='Shortened to upper-shoulder bob per user 2026-11-14; auburn interpretation.'
for s in [-1,1]:
 wing=bpy.data.objects['MA_UnderbodyWingPivot_'+str(s)]
 # Every mesh remains on the same wing; store inside rear/front tire envelopes.
 def fit(p):
  q=p.copy();q.x=-1.40+(q.x+1.40)*(2.20/3.10);q.y=s*(.45+(s*q.y-.60)*(.32/.42));return q
 for ob in wing.children:
  if ob.name.startswith('MA_RearWheelCarrier'):continue
  if ob.type=='MESH':
   for v in ob.data.vertices:v.co=fit(v.co)
  elif ob.type=='FONT':ob.location=fit(ob.location);ob.data.size*=.80
  elif ob.type=='CURVE':
    # Curve points are modelled in world/rest coordinates, with height offset on object.
   for sp in ob.data.splines:
    for p in sp.points:p.co=(*fit(Vector(p.co[:3])),1)
 # Pivot is directly behind the rear tire, not at the rear bumper.
 old=wing.location.copy();new=Vector((-1.57,s*.75,.24));delta=new-old;wing.location=new
 for ob in wing.children:ob.matrix_parent_inverse.translation-=delta
 # Remove counter-rotation: road wheel axle Y turns into airplane thrust axis X.
 carrier=bpy.data.objects['MA_RearWheelCarrier_'+str(s)];carrier.driver_remove('rotation_euler',2);carrier.rotation_euler[2]=0
 carrier['flight_role']='Persistent road wheel rotates with wing, outward rim becomes aft-facing turbine/reactor.'
 # Turbine insert is recessed within the existing rim and travels with that wheel.
 tube('MA_WheelTurbineRecess',(-1.24,s*.955,.32),(-1.24,s*.961,.32),.146,black,N=48,root=carrier)
 tube('MA_WheelTurbineHub',(-1.24,s*.964,.32),(-1.24,s*.978,.32),.045,metal,r2=.022,N=32,root=carrier)
 for i in range(12):
  a=i*2*pi/12;b=a+.22
  mesh('MA_RearWheelTurbineBlade', [(-1.24+.045*cos(a),s*.969,.32+.045*sin(a)),(-1.24+.14*cos(b),s*.969,.32+.14*sin(b)),(-1.24+.14*cos(b+.12),s*.969,.32+.14*sin(b+.12)),(-1.24+.045*cos(a+.16),s*.969,.32+.045*sin(a+.16))],[(0,1,2,3)],metal,carrier)
root['wing_note']='User correction: pivots X=-1.57m immediately aft of rear tires; stored blade X[-1.40,.80], inside wheel lateral envelope. Rear tires and recessed turbine inserts turn rigidly with wing.'
# Only the central ~40% of hood width slides. Outer headlamp shoulders stay fixed.
slide=bpy.data.objects['MA_SlidingHood'];old=bpy.data.objects['MA_SlidingHoodSkin'];bpy.data.objects.remove(old,do_unlink=True)
for ob in list(slide.children):
 wm=ob.matrix_world.copy();ob.parent=root;ob.matrix_parent_inverse=root.matrix_world.inverted();ob.matrix_world=wm
 if ob.name.startswith('MA_Headlamp'):
  drive(ob,'location',2,'-.10*t',[('t',root,'transform')])
def hoodz(x,y):
 keys=[(.74,.835),(1.17,.79),(1.75,.70),(2.12,.63)];z=keys[-1][1]
 for (a,za),(b,zb) in zip(keys,keys[1:]):
  if x<=b:z=za+(zb-za)*(x-a)/(b-a);break
 return z+.048*(1-(y/.70)**2)+.015*sin(pi*(x-.74)/1.38)
def hoodpiece(name,lo,hi,parent):
 xs=seq(22,.74,2.12);ys=seq(14,lo,hi);vv=[];K=len(ys)+2
 for x in xs:
  vv.extend((x,y,hoodz(x,y)) for y in ys);vv.extend([(x,hi,hoodz(x,hi)-.075),(x,lo,hoodz(x,lo)-.075)])
 ff=[tuple(reversed(range(K))),tuple((len(xs)-1)*K+i for i in range(K))]+[(j*K+i,j*K+(i+1)%K,(j+1)*K+(i+1)%K,(j+1)*K+i) for j in range(len(xs)-1) for i in range(K)]
 return mesh(name,vv,ff,purple,parent,smooth=True,bevel=.006)
hoodpiece('MA_SlidingHoodSkin',-.33,.33,slide)
hoodpiece('MA_FixedHoodShoulder_L',.342,.67,root)
hoodpiece('MA_FixedHoodShoulder_R',-.67,-.342,root)
root['hood_note']='User correction: only center strip 0.66m across 1.76m body (~38%) translates; outer shoulders remain fixed. Slight transverse and longitudinal crown. Headlight shutters sink independently as guns emerge.'
# Corresponding lower side walls close each fixed shoulder gun compartment.
for s in [-1,1]:
 for y in [.344,.67]:
  pts=[]
  for x in seq(18,.74,2.12):pts.extend([(x,s*y,hoodz(x,s*y)-.05),(x,s*y,.48)])
  mesh('MA_FixedHoodWellWall',pts,[(i*2,i*2+1,i*2+3,i*2+2) for i in range(18)],purple,root,bevel=.003)
R['driving_pose']=1.;R['in_vehicle']=1.;R['mask_on']=False;R.update_tag();S.frame_set(61);S.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Manta_V7_Assembly.blend'),compress=True)
print('USER_CORRECTIONS_V7_SAVED')
