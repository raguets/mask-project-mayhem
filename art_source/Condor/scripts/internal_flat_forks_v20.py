import bpy,math,gc,types
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Condor'
lock=bpy.app.driver_namespace.get('_mask_asset_review_active')
if lock:
 assert Path(lock['output_dir']).resolve()==(A/'renders/v19_review').resolve();fs=[f for f in gc.get_objects() if isinstance(f,types.FunctionType) and f.__name__=='step' and f.__globals__.get('lock_token')==lock['token']];assert len(fs)==1;fn=fs[0]
 if bpy.app.timers.is_registered(fn):bpy.app.timers.unregister(fn)
 fn.__globals__['restore']();(A/'renders/v19_review/CANCELLED').write_text('Stopped for user correction: hidden broad flat rear wheel arms.')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
CURRENT=bpy.data.collections['Condor_Vehicle'];root=bpy.data.objects['Condor_Control'];PARENT=root;s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
rear=bpy.data.objects['Condor_RearWheelPivot'];spin=bpy.data.objects['Condor_TailRotorSpin'];world=spin.matrix_world.copy();rear.location.z=.74;bpy.context.view_layer.update();spin.matrix_world=world;bpy.context.view_layer.update()
for o in list(CURRENT.all_objects):
 if o.name.startswith(('Condor_ConnectedRearFork','Condor_FixedRearPivot','Condor_RearPivotChassisBracket')):bpy.data.objects.remove(o,do_unlink=True)
black=bpy.data.materials['Condor_Charcoal']
for side in [-1,1]:
 a=Vector((-1.45,side*.045,.74));b=Vector((-1.05,side*.045,.355));axis=(b-a).normalized();perp=Vector((-axis.z,0,axis.x));outline=[];width=.092;thickness=.018
 for center,sign in [(b,1),(a,-1)]:
  for j in range(13):
   ang=-math.pi/2+math.pi*j/12;outline.append(center+axis*(sign*math.cos(ang)*width/2)+perp*(sign*math.sin(ang)*width/2))
 vv=[tuple(p+Vector((0,dy,0))) for dy in [-thickness/2,thickness/2] for p in outline];n=len(outline);ff=[tuple(reversed(range(n))),tuple(range(n,2*n))]
 for i in range(n):ff.append((i,(i+1)%n,n+(i+1)%n,n+i))
 ob=mesh('Condor_InternalFlatFork_'+str(side),vv,ff,black,root=rear,bevel=.003);ob['section_m']=[width,thickness];ob['storage']='Inboard under rear chassis, hidden at rest, visible after swing.'
tube('Condor_InternalRearPivotAxle',(-1.45,-.065,.74),(-1.45,.065,.74),.026,black)
root['rear_arm_note']='Two flat92mm wide /18mm thick inboard swing arms at Y±45mm; pivot below rear roof. User 2026-11-12, estimated dimensions.'
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(A/'Condor_V20_Assembly.blend'),compress=True);print('V20_INTERNAL_FLAT_FORKS_SAVED')
