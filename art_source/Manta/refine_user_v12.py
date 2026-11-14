import bpy,math,re
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Manta';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
root=bpy.data.objects['Manta_Control'];R=bpy.data.objects['VanessaWarfield_Rig'];S.frame_set(1);bpy.context.view_layer.update()
CURRENT=bpy.data.collections['Manta_Vehicle'];PARENT=root
purple=bpy.data.objects['MA_MainBody'].data.materials[0];glass=bpy.data.objects['MA_Windshield'].data.materials[0];black=bpy.data.objects['MA_Underbody'].data.materials[0]
# Remove front bumper, black bumper bars and white headlight covers completely.
for ob in list(bpy.data.objects):
 if ob.name in ['MA_FrontBumper','MA_FrontIntake'] or ob.name.startswith('MA_Headlamp_'):bpy.data.objects.remove(ob,do_unlink=True)
ob=bpy.data.objects['MA_WeaponBayFloor']
for v in ob.data.vertices:v.co.x=min(v.co.x,2.015)
# Actual rectangular openings through fixed hood shoulders, rather than white decals.
for s,l in [(1,'L'),(-1,'R')]:
 ob=bpy.data.objects['MA_FixedHoodShoulder_'+l]
 cut=box('TempRectangularHeadlightOpening',(1.965,s*.535,.60),(.255,.22,.36),None,0)
 m=ob.modifiers.new('OpenRectangularCannonPort','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cut;bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cut,do_unlink=True)
 # Thin body-coloured inner walls preserve a recessed hole with a clear gun path.
 for yy in [.423,.647]:box('MA_HeadlightPortInnerWall',(1.965,s*yy,.505),(.25,.012,.07),purple,.004,root)
root['headlights_note']='Two actual rectangular holes in fixed shoulders; no white lenses, no front bumper or black bumper bars. Root-mounted cannon slides are independent of the moving hood.'
# Wings broaden by 50% chord and their roots extend across the wheel line under the body.
for s in [-1,1]:
 wing=bpy.data.objects['MA_UnderbodyWingPivot_'+str(s)]
 def broaden(p):
  q=p.copy();q.y=s*(.61+(s*q.y-.61)*1.5)
  if q.x<-.90:q.x-=.70
  return q
 for ob in wing.children:
  if ob.name.startswith('MA_MainWing_'+str(s)) and ob.type=='MESH':
   for v in ob.data.vertices:v.co=broaden(v.co)
  elif ob.type=='CURVE' and ob.name.startswith(('MA_WingPanelLine','MA_AileronSeam')):
   for sp in ob.data.splines:
    for p in sp.points:p.co=(*broaden(Vector(p.co[:3])),1)
  elif ob.name.startswith(('MA_MainWingForwardCannon','MA_MainWingCannonBore')) and ob.type=='MESH':
   for v in ob.data.vertices:v.co.y-=s*.07
root['wing_note']='Chord +50%; stored root extends aft under rear body, deployed root reaches under central chassis instead of stopping at rear wheel. Rear wheel farther from beginning of visible wing; same rigid carrier and aft pivot.'
# Rear board now covers the full jet envelope (including lower nozzle edges).
board=bpy.data.objects['MA_RearLightPanel']
for v in board.data.vertices:v.co.z=.610+(v.co.z-.665)*(.44/.31)
# Remove long support projections below the bumper while keeping nested overlap.
for ob in bpy.data.objects:
 if ob.type=='MESH' and ob.name.startswith('MA_RearBoardLowerLeg'):
  for v in ob.data.vertices:v.co.z=.47+(v.co.z-.38)*(.18/.36)
 if ob.type=='MESH' and ob.name.startswith('MA_RearBoardMiddleLeg'):
  for v in ob.data.vertices:v.co.z=.47+(v.co.z-.42)*(.26/.36)
# Slight horizontal windshield crown, including curved rubber outline and fitted wipers.
for ob in list(bpy.data.objects):
 if ob.name=='MA_Windshield' or ob.name.startswith('MA_WindshieldRubber'):bpy.data.objects.remove(ob,do_unlink=True)
def wind(t,q):return (.69-.67*t+.030*(1-q*q),(.75-.10*t)*q,.86+.42*t)
patch('MA_Windshield',seq(24),seq(32,-1,1),wind,glass,sub=1,thick=.007)
outline=[wind(0,q) for q in seq(32,-1,1)]+[wind(t,1) for t in seq(24)]+[wind(1,q) for q in seq(32,1,-1)]+[wind(t,-1) for t in seq(24,1,0)]
path('MA_WindshieldRubber',outline,.012,black)
for ob in bpy.data.objects:
 if ob.type=='CURVE' and ob.name.startswith('MA_Wiper'):
  for sp in ob.data.splines:
   for p in sp.points:
    t=(p.co.z-.86)/.42;q=p.co.y/(.75-.10*t);p.co.x=wind(t,q)[0]+.007
# Curved rear body borders follow the already curved rear glass, rather than straight chords.
for ob in list(bpy.data.objects):
 if ob.name.startswith(('MA_HatchSurround','MA_RearQuarterRoofEdge')):bpy.data.objects.remove(ob,do_unlink=True)
def hatch(t,q):return (-.94-1.05*t,(.67+.10*t)*q,1.27-.43*t+.023*sin(pi*t)*(1-.25*q*q)+.012*(1-q*q))
outline=[hatch(0,q) for q in seq(32,-1,1)]+[hatch(t,1) for t in seq(28)]+[hatch(1,q) for q in seq(32,1,-1)]+[hatch(t,-1) for t in seq(28,1,0)]
path('MA_HatchSurround',outline,.032,purple)
for s in [-1,1]:path('MA_RearQuarterRoofEdge',[hatch(t,s) for t in seq(30)],.035,purple)
# Lengthen front and rear overhangs about the cabin, preserving round wheel meshes
# and the independent pilot anatomy. Local mechanism translations follow the same scale.
def lengthen(x):return .75+(x-.75)*1.10 if x>.75 else (-1.05+(x+1.05)*1.08 if x<-1.05 else x)
objects=list(set(bpy.data.collections['Manta_Vehicle'].all_objects)|set(bpy.data.collections['Manta_Interior'].all_objects));raw={};oldloc={o:o.location.copy() for o in objects}
for ob in objects:
 M=ob.matrix_world.copy()
 if ob.type=='MESH':raw[ob]=[M@v.co for v in ob.data.vertices]
 elif ob.type=='CURVE':raw[ob]=[[M@Vector(p.co[:3]) for p in sp.points] for sp in ob.data.splines]
def depth(o):return 0 if not o.parent else 1+depth(o.parent)
for ob in sorted(objects,key=depth):
 if ob==root:continue
 if ob.parent:ob.matrix_parent_inverse=ob.parent.matrix_world.inverted()
 if ob.type in ['EMPTY','FONT']:ob.location.x=lengthen(oldloc[ob].x)
 bpy.context.view_layer.update()
for ob,data in raw.items():
 inv=ob.matrix_world.inverted();match=re.match(r'MA_(Front|Rear)Wheel_(-?1)_',ob.name)
 wheel=bool(match) or ob.name.startswith(('MA_WheelTurbine','MA_RearWheelTurbineBlade'))
 centre_x=(1.24 if match and match.group(1)=='Front' else -1.24)
 def mapped(p):
  q=p.copy();q.x+=lengthen(centre_x)-centre_x if wheel else lengthen(q.x)-q.x;return inv@q
 if ob.type=='MESH':
  for v,p in zip(ob.data.vertices,data):v.co=mapped(p)
 else:
  for sp,points in zip(ob.data.splines,data):
   for v,p in zip(sp.points,points):v.co=(*mapped(p),1)
for name,factor in [('MA_SlidingHood',1.10),('MA_HeadlightCannonTravel_-1',1.10),('MA_HeadlightCannonTravel_1',1.10),('MA_TripleReactorTravel',1.08),('MA_RearBoardSlide',1.08)]:
 ob=bpy.data.objects[name]
 for f in ob.animation_data.drivers:
  if f.data_path=='location' and f.array_index==0:f.driver.expression='('+f.driver.expression+')*'+str(factor)
root['proportions_note']='Front overhang stretched +10% ahead of X=.75m, rear +8% aft of X=-1.05m, inspired by supplied Nissan 300ZX photos. Wheel cross sections and independent character anatomy preserved; estimates, not official dimensions.'
R['driving_pose']=1.;R['in_vehicle']=1.;R['mask_on']=False;R.update_tag();S.frame_set(61);S.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Manta_V12_Assembly.blend'),compress=True)
print('V12_SAVED')
