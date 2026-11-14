"""Consolidate all longitudinal proportions, clean round arches and left-hand drive."""
import bpy,math,re,bmesh,json
from pathlib import Path
from mathutils import Vector,Matrix
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Manta';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Session_before_consolidation.blend'),copy=True,compress=True)
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
root=bpy.data.objects['Manta_Control'];R=bpy.data.objects['VanessaWarfield_Rig'];S.frame_set(1);bpy.context.view_layer.update()
CURRENT=bpy.data.collections['Manta_Vehicle'];PARENT=root
purple=bpy.data.objects['MA_MainBody'].data.materials[0];black=bpy.data.objects['MA_Underbody'].data.materials[0]
def prior(x):return .75+(x-.75)*1.10 if x>.75 else (-1.05+(x+1.05)*1.08 if x<-1.05 else x)
back=min((bpy.data.objects['MA_RearLightPanel'].matrix_world@v.co).x for v in bpy.data.objects['MA_RearLightPanel'].data.vertices)
front=max((bpy.data.objects['MA_MainBody'].matrix_world@v.co).x for v in bpy.data.objects['MA_MainBody'].data.vertices)
rear_scale=1.41/(-.80-back);front_scale=1.88/(front-.50)
def X(x):
 if x<-.80:return -.94+(x+.80)*rear_scale
 if x>.50:return .47+(x-.50)*front_scale
 return -.94+(x+.80)*(1.41/1.30)
def C(x):return X(prior(x))
# Retain the specified aft pivot but move its bearing outboard enough to clear a
# ROUND wheel opening; do not turn the fender into an enormous swept slot.
for sign in [-1,1]:
 wing=bpy.data.objects['MA_UnderbodyWingPivot_'+str(sign)];delta=Vector((0,sign*.13,0));wing.location+=delta
 for ob in wing.children:ob.matrix_parent_inverse.translation-=delta
 # Keep both stored wings inside the inner tire faces (|Y|=.725), including edges.
 for ob in wing.children:
  if ob.type=='MESH' and ob.name.startswith('MA_MainWing_'+str(sign)):
   for v in ob.data.vertices:v.co.y-=sign*.17
  elif ob.type=='CURVE' and ob.name.startswith(('MA_WingPanelLine','MA_AileronSeam')):
   for sp in ob.data.splines:
    for v in sp.points:v.co.y-=sign*.17
  elif ob.type=='FONT':ob.location.y=sign*.44
  elif ob.type=='MESH' and ob.name.startswith(('MA_MainWingForwardCannon','MA_MainWingCannonBore')):
   for v in ob.data.vertices:v.co.y-=sign*.17
  elif ob.type=='MESH' and ob.name.startswith('MA_RearWheelCarrierGusset'):
   for v in ob.data.vertices:
    if abs(v.co.y)<.77:v.co.y=sign*.62
# Global piecewise remap: exact 40/30/30 exterior zones, round wheels preserved.
objects=list(set(bpy.data.collections['Manta_Vehicle'].all_objects)|set(bpy.data.collections['Manta_Interior'].all_objects));raw={};oldloc={o:o.location.copy() for o in objects}
def slimmer(p,name):
 q=p.copy()
 if name.startswith(('MA_RearHatchGlass','MA_RearLouvre','MA_HatchSurround','MA_RearQuarterRoofEdge')):
  q.y*=.94;q.z-=.06*max(0,min(1,(q.z-.82)/.45))
 elif name.startswith(('MA_QuarterGlass','MA_QuarterWindowFrame','MA_Bpillar','MA_RoofRearCross')):
  t=max(0,min(1,(q.z-.82)/.45));q.y*=1-.06*t;q.z-=.06*t
 elif name=='MA_TbarRoof':q.z-=.06*max(0,min(1,(.015-q.x)/.90))
 return q
for ob in objects:
 M=ob.matrix_world.copy()
 if ob.type=='MESH':raw[ob]=[slimmer(M@v.co,ob.name) for v in ob.data.vertices]
 elif ob.type=='CURVE':raw[ob]=[[slimmer(M@Vector(v.co[:3]),ob.name) for v in sp.points] for sp in ob.data.splines]
def depth(o):return 0 if not o.parent else 1+depth(o.parent)
for ob in sorted(objects,key=depth):
 if ob==root:continue
 if ob.parent:ob.matrix_parent_inverse=ob.parent.matrix_world.inverted()
 if ob.type in ['EMPTY','FONT']:ob.location.x=X(oldloc[ob].x)
 bpy.context.view_layer.update()
for ob,data in raw.items():
 inv=ob.matrix_world.inverted();match=re.match(r'MA_(Front|Rear)Wheel_(-?1)_',ob.name)
 wheel=bool(match) or ob.name.startswith(('MA_WheelTurbine','MA_RearWheelTurbineBlade'));cx=prior(1.24 if match and match.group(1)=='Front' else -1.24)
 def mapped(p):q=p.copy();q.x+=X(cx)-cx if wheel else X(q.x)-q.x;return inv@q
 if ob.type=='MESH':
  for v,p in zip(ob.data.vertices,data):v.co=mapped(p)
 else:
  for sp,points in zip(ob.data.splines,data):
   for v,p in zip(sp.points,points):v.co=(*mapped(p),1)
for name,factor in [('MA_SlidingHood',front_scale),('MA_HeadlightCannonTravel_-1',front_scale),('MA_HeadlightCannonTravel_1',front_scale),('MA_TripleReactorTravel',rear_scale),('MA_RearBoardSlide',rear_scale)]:
 for f in bpy.data.objects[name].animation_data.drivers:
  if f.data_path=='location' and f.array_index==0:f.driver.expression='('+f.driver.expression+')*'+str(factor)
root['length_proportions']='4.70m exterior: front X[.47,2.35] 1.88m=40%; doors X[-.94,.47] 1.41m=30%; rear X[-2.35,-.94] 1.41m=30%. Scale estimated, ratios user-specified.'
# Rebuild the lower shell from CLEAN sections and circular cuts. No stretched old cuts.
oldbody=bpy.data.objects['MA_MainBody'];bpy.data.objects.remove(oldbody,do_unlink=True)
def hoodedge(x):
 k=[(.74,.835),(1.17,.79),(1.75,.70),(2.12,.63)];xx=min(2.12,max(.74,x));z=k[-1][1]
 for (a,v),(b,w) in zip(k,k[1:]):
  if xx<=b:z=v+(w-v)*(xx-a)/(b-a);break
 t=max(0,min(1,(xx-1.45)/.67));return z+.048*(1-(.67/.70)**2)+.015*sin(pi*(xx-.74)/1.38)-.135*t*t*(3-2*t)
vv=[];xs=seq(90,-2.15,2.13);K=20
for oldx in xs:
 x=C(oldx);w=profile(oldx,[(-2.15,.76),(-1.9,.86),(-1.3,.89),(-.4,.88),(.6,.87),(1.4,.88),(2.13,.79)])
 lo=profile(oldx,[(-2.15,.25),(-.4,.24),(.6,.24),(2.13,.28)]);hi=profile(oldx,[(-2.15,.73),(-1.9,.80),(-1.3,.86),(-.4,.84),(.6,.84),(.75,.84)]) if oldx<.75 else hoodedge(oldx)
 r=min(.06,(hi-lo)*.20)
 for cy,cz,a,b in [(w-r,lo+r,-pi/2,0),(w-r,hi-r,0,pi/2),(-w+r,hi-r,pi/2,pi),(-w+r,lo+r,pi,3*pi/2)]:
  for angle in seq(4,a,b):vv.append((x,cy+r*cos(angle),cz+r*sin(angle)))
ff=[tuple(reversed(range(K))),tuple((len(xs)-1)*K+i for i in range(K))]+[(j*K+i,j*K+(i+1)%K,(j+1)*K+(i+1)%K,(j+1)*K+i) for j in range(len(xs)-1) for i in range(K)]
body=mesh('MA_MainBody',vv,ff,purple,root,smooth=True,bevel=.012)
def subtract(target,cut,name):
 m=target.modifiers.new(name,'BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cut;bpy.context.view_layer.objects.active=target;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cut,do_unlink=True)
def cutbox(name,xa,xb,ya,yb,za,zb):return box(name,((xa+xb)/2,(ya+yb)/2,(za+zb)/2),(xb-xa,yb-ya,zb-za),None,0)
subtract(body,cutbox('TempCabin',C(-1.285),C(.565),-.70,.70,.43,1.9),'CleanCabinWell')
subtract(body,cutbox('TempHood',C(.685),2.40,-.6675,.6675,.390,1.8),'CleanHoodWell')
subtract(body,cutbox('TempRearJets',C(-2.45),C(-1.425),-.53,.53,.38,.73),'CleanReactorWell')
frontcx=C(1.24);rearcx=C(-1.24)
for x in [frontcx,rearcx]:subtract(body,tube('TempRoundWheelArch',(x,-1.2,.34),(x,1.2,.34),.340,None,N=96),'CircularWheelArch')
for ob in list(bpy.data.objects):
 if ob.name.startswith(('MA_ArchLip','MA_RearSweptArchLip')):bpy.data.objects.remove(ob,do_unlink=True)
for x in [frontcx,rearcx]:
 for sign in [-1,1]:path('MA_CircularArchLip',[(x+.344*cos(a),sign*.89,.34+.344*sin(a)) for a in seq(64,0,pi)],.009,purple)
# Body-coloured lower nose closes below the hood; no black bar or separate bumper.
ys=seq(40,-.77,.77);v=[]
for y in ys:
 z=.515-.048*(abs(y)/.70)**2
 if abs(y)>.54:z-=.065*min(1,(abs(y)-.54)/.13)
 v.extend([(C(2.12)+.001,y,.285),(C(2.12)+.001,y,z-.003)])
mesh('MA_IntegratedRoundedNose',v,[(i*2,i*2+2,i*2+3,i*2+1) for i in range(len(ys)-1)],purple,root,smooth=True,bevel=.008)
# Correct thin left-right, broad fore-aft supports, and enlarge rear lamps vertically.
for ob in bpy.data.objects:
 if ob.type=='MESH' and ob.name.startswith(('MA_RearBoardLowerLeg','MA_RearBoardMiddleLeg','MA_RearBoardUpperLeg')):
  pts=[ob.matrix_world@v.co for v in ob.data.vertices];c=sum(pts,Vector())/len(pts);oldx=max(p.x for p in pts)-min(p.x for p in pts);oldy=max(p.y for p in pts)-min(p.y for p in pts);inv=ob.matrix_world.inverted()
  targetx=.14 if 'Lower' in ob.name else (.12 if 'Middle' in ob.name else .10);targety=.025 if 'Lower' in ob.name else (.021 if 'Middle' in ob.name else .017)
  for v,p in zip(ob.data.vertices,pts):p.x=c.x+(p.x-c.x)*targetx/oldx;p.y=c.y+(p.y-c.y)*targety/oldy;v.co=inv@p
 if ob.type=='MESH' and ob.name.startswith(('MA_TailRed','MA_TailAmber','MA_TailReverse')):
  for v in ob.data.vertices:v.co.z=.68+(v.co.z-.70)*1.90
# Left hand drive (+Y). Mirror every driving control, keep the same character.
for ob in bpy.data.collections['Manta_Interior'].objects:
 if ob.name.startswith(('MA_Instrument','MA_Steering','MA_WheelSpoke','MA_Pedal')):
  if ob.type=='MESH':
   for v in ob.data.vertices:v.co.y=-v.co.y
   bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(ob.data);bm.free()
  elif ob.type=='CURVE':
   for sp in ob.data.splines:
    for v in sp.points:v.co.y=-v.co.y
R.animation_data.drivers.find('location',index=1).driver.expression='.37*v'
R.animation_data.drivers.find('location',index=0).driver.expression=str(X(-.40))+'*v'
R['driving_side']='LEFT +Y; steering, instruments and pedals mirrored with the driver.'
root['arch_note']='Clean rebuilt rounded body; circular arches radius .340m around round .296m tires. Wheel pivot clearance must be solved without deforming arches.'
root['wing_storage_note']='Stored blades |Y|<=.68, inside rear tire inner face |Y|=.725; roots extend below rear body, not across tire sidewalls.'
S.frame_set(61);S.frame_set(1);R.update_tag();bpy.context.view_layer.update()
(A/'proportions_v13.json').write_text(json.dumps({'overall_length':4.70,'front':{'length':1.88,'fraction':.4},'doors':{'length':1.41,'fraction':.3},'rear':{'length':1.41,'fraction':.3},'front_axle_x':frontcx,'rear_axle_x':rearcx,'arch_radius':.340,'wheel_radius':.296,'old_rear':back,'old_front':front},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Manta_V13_Assembly.blend'),compress=True)
print('V13_CONSOLIDATED_SAVED',frontcx,rearcx)
