import bpy,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Condor';s=bpy.context.scene;root=bpy.data.objects['Condor_Control'];R=bpy.data.objects['BradTurner_Rig']
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
def geo(obs):
 dg=bpy.context.evaluated_depsgraph_get();vv=[];ff=[];ee=[]
 for ob in obs:
  if ob.type not in ['MESH','CURVE']:continue
  ev=ob.evaluated_get(dg);me=ev.to_mesh();off=len(vv);vv.extend(ev.matrix_world@v.co for v in me.vertices);ff.extend(tuple(off+i for i in f.vertices) for f in me.polygons);ee.extend((off+e.vertices[0],off+e.vertices[1]) for e in me.edges);ev.to_mesh_clear()
 return vv,ff,ee
wheel=[o for o in bpy.data.collections['Condor_Vehicle'].all_objects if o.name.startswith(('Condor_Rear_PersistentTire','Condor_Rear_Rim','Condor_Rear_ThreeSpoke','Condor_Rear_Hub','Condor_Rear_Tread'))]
support=[o for o in bpy.data.collections['Condor_Vehicle'].all_objects if o.name.startswith(('Condor_ConvergingMast','Condor_MainBlade','Condor_MastTopBridge','Condor_RotorBearing','Condor_RotatingBladeGrips'))]
body=bpy.data.objects['Condor_RearMonobloc'];spin=bpy.data.objects['Condor_TailRotorSpin'];mast=bpy.data.objects['Condor_RotorSupport'];samples=[]
block=bpy.data.objects['Condor_SeatSkidBlock'];fixed=[o for o in bpy.data.collections['Condor_Vehicle'].all_objects if o.name.startswith(('Condor_LandingSkid','Condor_SeatSkidFixedStrut'))];saved_relative={};relative_error=0.
for frame in range(1,122,2):
 s.frame_set(frame);bpy.context.view_layer.update();wv,wf,we=geo(wheel);sv,sf,se=geo(support);bv,bf,be=geo([body]);wt=BVHTree.FromPolygons(wv,wf);st=BVHTree.FromPolygons(sv,sf);bt=BVHTree.FromPolygons(bv,bf)
 center=spin.matrix_world.translation;inside=0
 # Conservative full wheel cylinder, sampled along ALL support edges every15mm.
 for a,b in se:
  p,q=sv[a],sv[b];steps=max(1,math.ceil((q-p).length/.015))
  for j in range(steps+1):
   v=p.lerp(q,j/steps)-center
   if abs(v.y)<.09 and v.x*v.x+v.z*v.z<.365**2:inside+=1
 for ob in fixed:
  rel=block.matrix_world.inverted()@ob.matrix_world
  if ob.name not in saved_relative:saved_relative[ob.name]=rel.copy()
  relative_error=max(relative_error,max(abs(rel[i][j]-saved_relative[ob.name][i][j]) for i in range(4) for j in range(4)))
 samples.append({'frame':frame,'transform':root['transform'],'wheel_phase':root['rear_wheel_deploy'],'mast_angle_deg':math.degrees(mast.rotation_euler.y),'wheel_center':list(center),'wheel_support_triangles':len(wt.overlap(st)),'wheel_support_cylinder_samples':inside,'wheel_body_triangles':len(wt.overlap(bt))})
first=next((v for v in samples if v['wheel_phase']>1e-6),None)
R['driving_pose']=0.;R.update_tag();bpy.context.view_layer.update();mask=bpy.data.objects['BT_HocusPocus_OnePiece'];head=bpy.data.objects['BT_Head_AnatomicalSurface'];mv,mf,me=geo([mask]);hv,hf,he=geo([head]);mask_skull_hits=len(BVHTree.FromPolygons(mv,mf).overlap(BVHTree.FromPolygons(hv,hf)))
R['driving_pose']=1.;R.update_tag();s.frame_set(1);bpy.context.view_layer.update()
report={'source':bpy.data.filepath,'scope':'61 phases: actual wheel surfaces vs support/blades/rear cowl plus support-edge samples against conservative wheel cylinder. Rigid skid transforms relative to seat block. Not all vehicle/floor collisions.','samples':samples,'first_wheel_motion':first,'max_skid_relative_transform_error':relative_error,'mask_head_triangle_pairs_standing':mask_skull_hits,'passed_wheel_support':all(v['wheel_support_triangles']==0 and v['wheel_support_cylinder_samples']==0 for v in samples),'passed_wheel_body':all(v['wheel_body_triangles']==0 for v in samples),'passed_rigid_skids':relative_error<1e-6}
(A/'clearance_v16.json').write_text(json.dumps(report,indent=2));print('CLEARANCE_RESULT',json.dumps({k:v for k,v in report.items() if k!='samples'}))
