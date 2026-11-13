import bpy,math,json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Condor'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
root=bpy.data.objects['Condor_Control'];R=bpy.data.objects['BradTurner_Rig'];CURRENT=bpy.data.collections['Condor_Vehicle'];PARENT=root;s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
# Shorten green tail toward seat, keeping the single block and tapered lower line.
for o in CURRENT.all_objects:
 if o.type=='MESH' and any(k in o.name for k in ['RearMonobloc','RearBlockVent','RearBlockStripe']):
  for v in o.data.vertices:v.co.x=-.40+(v.co.x+.40)*.82
# Move rear road wheel forward with its fixed hinge; retain continuous fork.
rear=bpy.data.objects['Condor_RearWheelPivot'];rear.location.x+=.18
for o in CURRENT.all_objects:
 if o.name.startswith('Condor_FixedRearPivot') and o.type=='MESH':
  for v in o.data.vertices:v.co.x+=.18
cut=bpy.data.objects['Condor_RearWheelWell_Cutter']
for v in cut.data.vertices:v.co.x+=.18
# Shorter mast and folded blades: road end follows shortened cowl; rotor remains above pilot.
mast=bpy.data.objects['Condor_RotorSupport'];mast.location.z+=.13
for o in list(CURRENT.all_objects):
 if o.type=='MESH' and any(o.name.startswith(k) for k in ['Condor_MastArm','Condor_MainBlade','Condor_MainRotorSpindle','Condor_MastCrossBridge']):
  for v in o.data.vertices:
   if o.name.startswith('Condor_MainBlade'):v.co.y*=.85
   else:v.co.x=-.46+(v.co.x+.46)*.85
hub=bpy.data.objects['Condor_MainRotorHub'];hub.location.x+=.222
# Empty attachment inverse was created at the original rotor end. Preserve authored
# blade coordinates after shifting the hub by applying the same rest offset to blades.
for o in CURRENT.all_objects:
 if o.name.startswith('Condor_MainBlade'):
  for v in o.data.vertices:v.co.x+=.222
# Seat and landing skids are now one translation assembly with rigid shared carriage.
block=empty('Condor_SeatSkidBlock',(0,0,0),root)
seat=bpy.data.objects['Condor_SeatCarriage'];seat.driver_remove('location',2);seat.location.z=.69
for o in [seat]+[bpy.data.objects['Condor_SkidCarriage_'+str(side)] for side in [-1,1]]:
 if o!=seat:o.driver_remove('location',2);o.location.z=.29
 mw=o.matrix_world.copy();o.parent=block;o.matrix_world=mw
drive(block,'location',2,'-0.12*t',[('t',root,'transform')])
box('Condor_SeatSkidCommonCarriage',(-.17,0,.53),(.51,.33,.32),bpy.data.materials['Condor_Charcoal'],.025,block)
for o in CURRENT.all_objects:
 if o.name.startswith('Condor_LandingSkid') and o.type=='CURVE':
  for sp in o.data.splines:
   for p in sp.points:p.co.z-=.09
 if o.name.startswith('Condor_SkidStrut') and o.type=='MESH':
  for v in o.data.vertices:
   if v.co.z<.31:v.co.z-=.09
drive(R,'location',2,'v*(-0.10-0.12*t)',[('v',R,'in_vehicle'),('t',root,'transform')])
# A SINGLE connected shell mesh, visor and flush markings assigned as materials.
CURRENT=bpy.data.collections['BT_Mask'];PARENT=None
for o in list(CURRENT.all_objects):bpy.data.objects.remove(o,do_unlink=True)
shell=bpy.data.materials['BT_HocusPocusYellow'];dark=bpy.data.materials['BT_HocusPocusVisor']
zs=[1.535,1.565,1.582,1.594,1.610,1.627,1.639,1.657,1.675,1.728,1.792,1.820,1.845,1.857]
rxs=[.108,.125,.136,.140,.149,.162,.166,.160,.155,.157,.145,.122,.075,.004]
rys=[.100,.107,.112,.116,.120,.124,.127,.133,.141,.145,.139,.120,.078,.004]
N=128;vv=[];ff=[];mats=[]
for j,(z,rx,ry) in enumerate(zip(zs,rxs,rys)):
 for i in range(N):
  a=2*pi*i/N;aa=min(a,2*pi-a);zz=z
  if aa<1.42:
   if j==8:zz=1.674+.024*math.exp(-(aa/.23)**2)+.011*(aa/1.42)**4
   if j==10:zz=1.785+.017*math.exp(-(aa/.95)**2)
  x=-.010+rx*cos(a);y=ry*sin(a);vv.append((x,y,zz))
for j in range(len(zs)-1):
 for i in range(N):
  a=2*pi*(i+.5)/N;aa=min(a,2*pi-a)
  ff.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
  visor=8<=j<10 and aa<1.33
  mouth=j==2 and aa<.17
  ports=j==5 and any(abs(aa-c)<.025 for c in [0,.19,.38])
  mats.append(int(visor or mouth or ports))
ff.append(tuple((len(zs)-1)*N+i for i in range(N)));mats.append(0)
o=mesh('BT_HocusPocus_OnePiece',vv,ff,shell,smooth=True);o.data.materials.append(dark)
for face,idx in zip(o.data.polygons,mats):face.material_index=idx
o.parent=R;o.vertex_groups.new(name='head').add(list(range(len(vv))),1,'REPLACE');o.modifiers.new('EditableMaskSkin','ARMATURE').object=R;wall=o.modifiers.new('ContinuousShellThickness','SOLIDIFY');wall.thickness=.004
for k in ['hide_render','hide_viewport']:drive(o,k,None,'1-m',[('m',R,'mask_on')])
o['construction']='One connected editable shell mesh; opaque diving-goggle-shaped visor is an integrated material region, not an open slot. Face fully enclosed except neck attachment.'
root['seat_skid_note']='Single Condor_SeatSkidBlock translates down 0.12m; seat and skids are children of the same carriage. Estimated travel.'
R['mask_note']='One-piece compact shell, fully covered face and integrated diving-goggle-shaped visor, user correction 2026-11-12.'
R['mask_on']=True;R.update_tag();s.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Condor_V9_Assembly.blend'),compress=True)
print('V9_SHARED_SEAT_SKIDS_AND_ONEPIECE_MASK_SAVED')
