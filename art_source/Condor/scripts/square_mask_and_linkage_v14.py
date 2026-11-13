import bpy,math,gc,types
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Condor'
lock=bpy.app.driver_namespace.get('_mask_asset_review_active')
if lock:
 assert Path(lock['output_dir']).resolve()==(A/'renders/v13_review').resolve()
 fs=[f for f in gc.get_objects() if isinstance(f,types.FunctionType) and f.__name__=='step' and f.__globals__.get('lock_token')==lock['token']];assert len(fs)==1;fn=fs[0]
 if bpy.app.timers.is_registered(fn):bpy.app.timers.unregister(fn)
 fn.__globals__['restore']();(A/'renders/v13_review/CANCELLED').write_text('Stopped for square helmet/front-only visor correction.')
bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
CURRENT=bpy.data.collections['Condor_Vehicle'];PARENT=bpy.data.objects['Condor_Control'];rear=bpy.data.objects['Condor_RearWheelPivot'];black=bpy.data.materials['Condor_Charcoal']
# Rebuild after explicit dependency update: old parenting inverse was sampled stale.
for ob in list(CURRENT.all_objects):
 if ob.name.startswith('Condor_ConnectedRearFork'):bpy.data.objects.remove(ob,do_unlink=True)
for side in [-1,1]:tube('Condor_ConnectedRearFork_'+str(side),(-1.57,side*.11,.80),(-1.37,side*.11,.355),.033,black,root=rear)
mask=bpy.data.objects['BT_HocusPocus_OnePiece'];N=128
for v in mask.data.vertices:
 if v.index>=14*N:continue
 a=2*pi*(v.index%N)/N;c=cos(a);sn=sin(a)
 if abs(c)>1e-6:v.co.x=-.01+(v.co.x+.01)/math.sqrt(abs(c))
 else:v.co.x=-.01
 if abs(sn)>1e-6:v.co.y/=math.sqrt(abs(sn))
 else:v.co.y=0
# Frontal diving-goggle visor, yellow sides, one connected mesh and material boundary.
for face in mask.data.polygons:
 if face.index>=13*N:continue
 row=face.index//N;i=face.index%N;a=2*pi*(i+.5)/N;aa=min(a,2*pi-a)
 if row in [8,9]:face.material_index=int(aa<.66)
for i in range(N):mask.data.vertices[14*N+i].co=mask.data.vertices[i].co.lerp(mask.data.vertices[15*N+i].co,.5)
mask.data.update();mask['front_sides_note']='Squarer rounded front/side corners. Diving-goggle visor restricted to front face; yellow lateral shell.'
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Condor_V14_Assembly.blend'),compress=True);print('V14_MASK_AND_FORK_ANCHOR_CORRECTED')
