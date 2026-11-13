import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Condor';s=bpy.context.scene;root=bpy.data.objects['Condor_Control'];R=bpy.data.objects['BradTurner_Rig']
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
rear=bpy.data.objects['Condor_RearWheelPivot'];spin=bpy.data.objects['Condor_TailRotorSpin'];block=bpy.data.objects['Condor_SeatSkidBlock'];seat=bpy.data.objects['Condor_SeatCarriage']
results=[]
for f in range(1,122,3):
 s.frame_set(f);bpy.context.view_layer.update()
 # Connected fork proximal point is authored at rest anchor, transformed by rear parent.
 arm=bpy.data.objects['Condor_ConnectedRearFork_-1'];ev=arm.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();pts=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear();prox=sum(pts[:40],Vector())/40;fixed=root.matrix_world@Vector((-1.57,-.11,.80));results.append({'frame':f,'rear_fork_anchor_error_m':(prox-fixed).length})
s.frame_set(1);bpy.context.view_layer.update();z0=seat.matrix_world.translation.z;s.frame_set(121);bpy.context.view_layer.update();z1=seat.matrix_world.translation.z
mask=bpy.data.objects['BT_HocusPocus_OnePiece'];edges={tuple(sorted(e.vertices)) for e in mask.data.edges};adj=[[] for v in mask.data.vertices]
for a,b in edges:adj[a].append(b);adj[b].append(a)
seen=set();components=0
for start in range(len(adj)):
 if start in seen:continue
 components+=1;stack=[start];seen.add(start)
 while stack:
  for n in adj[stack.pop()]:
   if n not in seen:seen.add(n);stack.append(n)
report={'rear_fork_samples':results,'max_rear_fork_anchor_error_m':max(v['rear_fork_anchor_error_m'] for v in results),'seat_descent_m':z0-z1,'seat_and_skids_same_parent':seat.parent==block and all(bpy.data.objects['Condor_SkidCarriage_'+str(side)].parent==block for side in [-1,1]),'mask_mesh_objects':len([o for o in bpy.data.collections['BT_Mask'].all_objects if o.type=='MESH']),'mask_connected_components':components}
s.frame_set(1);(A/'mechanisms_v11.json').write_text(json.dumps(report,indent=2));print('MECHANISM_CHECK',json.dumps(report))
