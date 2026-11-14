import bpy,math,json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Manta';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
root=bpy.data.objects['Manta_Control'];R=bpy.data.objects['VanessaWarfield_Rig'];S.frame_set(1)
CURRENT=bpy.data.collections['Manta_Vehicle'];PARENT=root
purple=bpy.data.objects['MA_MainBody'].data.materials[0];glass=bpy.data.objects['MA_RearHatchGlass'].data.materials[0];black=bpy.data.objects['MA_Underbody'].data.materials[0]
# Gently crowned rear glazing; louvre bars follow the evaluated visible curvature.
def hatch(t,q):
 x=-.94-1.05*t;w=.67+.10*t;z=1.27-.43*t+.023*sin(pi*t)*(1-.25*q*q)+.012*(1-q*q)
 return (x,w*q,z)
for ob in list(bpy.data.objects):
 if ob.name=='MA_RearHatchGlass' or ob.name.startswith('MA_RearLouvre'):bpy.data.objects.remove(ob,do_unlink=True)
patch('MA_RearHatchGlass',seq(30),seq(24,-1,1),hatch,glass,sub=1,thick=.006)
for i in range(13):
 t=.04+.92*i/12;pts=[]
 for q in seq(20,-1,1):p=Vector(hatch(t,q));p.z+=.013;pts.append(tuple(p))
 path('MA_RearLouvre_%02d'%i,pts,.012,black)
# Flat hammerhead at the front of the central slider; the headlight cannons stay independent.
for n in ['MA_SlidingHoodSkin','MA_FixedHoodShoulder_L','MA_FixedHoodShoulder_R']:
 bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
for ob in list(bpy.data.objects):
 if ob.name.startswith('MA_FixedHoodWellWall'):bpy.data.objects.remove(ob,do_unlink=True)
def width(x):
 keys=[(.74,.33),(1.87,.305),(1.98,.325),(2.045,.54),(2.12,.54)]
 for (a,v),(b,w) in zip(keys,keys[1:]):
  if x<=b:return v+(w-v)*(x-a)/(b-a)
 return .54
def ztop(x,y):
 keys=[(.74,.835),(1.17,.79),(1.75,.70),(2.12,.63)]
 for (a,v),(b,w) in zip(keys,keys[1:]):
  if x<=b:z=v+(w-v)*(x-a)/(b-a);break
 return z+.048*(1-(y/.70)**2)+.015*sin(pi*(x-.74)/1.38)
xs=sorted(set(seq(34,.74,2.12)+[1.87,1.98,2.045,2.12]));K=18
def hood(name,side,parent):
 vv=[]
 for x in xs:
  w=width(x)
  lo,hi=(-w,w) if side==0 else ((w+.012,.67) if side==1 else (-.67,-w-.012))
  ys=seq(K-3,lo,hi)
  vv.extend((x,y,ztop(x,y)) for y in ys)
  thick=.075 if side else .075-.048*max(0,min(1,(x-1.86)/.26))
  vv.extend([(x,hi,ztop(x,hi)-thick),(x,lo,ztop(x,lo)-thick)])
 ff=[tuple(reversed(range(K))),tuple((len(xs)-1)*K+i for i in range(K))]+[(j*K+i,j*K+(i+1)%K,(j+1)*K+(i+1)%K,(j+1)*K+i) for j in range(len(xs)-1) for i in range(K)]
 return mesh(name,vv,ff,purple,parent,smooth=True,bevel=.004)
slide=bpy.data.objects['MA_SlidingHood'];hood('MA_SlidingHoodSkin',0,slide);hood('MA_FixedHoodShoulder_L',1,root);hood('MA_FixedHoodShoulder_R',-1,root)
for s in [-1,1]:
 vv=[]
 for x in xs:vv.extend([(x,s*(width(x)+.012),ztop(x,s*(width(x)+.012))-.05),(x,s*(width(x)+.012),.48)])
 mesh('MA_FixedHoodWellWall',vv,[(i*2,i*2+1,i*2+3,i*2+2) for i in range(len(xs)-1)],purple,root,bevel=.003)
root['hood_note']='Only central ~38% strip moves; front thins to 27mm and broadens into a flat transverse hammerhead. Cannons have root-mounted independent travel through headlamp shutters; not parented to slider.'
root['rear_glass_note']='Slight transverse/longitudinal crown; dark louvres follow curvature, user 2026-11-14.'
# Cut actual swept rear-wheel recesses instead of allowing the persistent wheels through skin.
body=bpy.data.objects['MA_MainBody']
for frame in range(1,122,3):
 S.frame_set(frame);bpy.context.view_layer.update()
 for s in [-1,1]:
  ob=bpy.data.objects['MA_RearWheel_'+str(s)+'_Tire'];matrix=ob.matrix_world.copy();c=Vector((-1.24,s*.83,.32));a=matrix@(c+Vector((0,-.125,0)));b=matrix@(c+Vector((0,.125,0)))
  cut=tube('TempRearSweptRecess',a,b,.318,None,N=48)
  m=body.modifiers.new('RearWheelSweptClearance','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cut;bpy.context.view_layer.objects.active=body;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cut,do_unlink=True)
R.animation_data.drivers.find('location',index=2).driver.expression='-.49*v'
R['driving_pose']=1.;R['in_vehicle']=1.;R['mask_on']=False;R.update_tag();S.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Manta_V8_Assembly.blend'),compress=True)
print('V8_SAVED')
