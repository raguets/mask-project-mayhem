import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Switchblade'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
R=bpy.data.objects['MilesMayhem_Rig'];saved={k:R[k] for k in ['in_vehicle','driving_pose','mask_on']};report=[]
def evaluated(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();v=[e.matrix_world@p.co for p in m.vertices];f=[tuple(p.vertices) for p in m.polygons];e.to_mesh_clear();return v,BVHTree.FromPolygons(v,f)
for pose in [0.,1.]:
 R['in_vehicle']=0.;R['driving_pose']=pose;R['mask_on']=True;R.update_tag();bpy.context.view_layer.update();cloth=bpy.data.objects['MM_ContinuousFlightSuit'];cv,tree=evaluated(cloth);g=bpy.data.objects['MM_Viper_ShoulderGorget'];gv,gtree=evaluated(g)
 # Solidify preserves original vertices first; last ring of original base grid is560? 7x80.
 distances=[];signed=[]
 for p in gv[480:560]:
  pos,n,idx,d=tree.find_nearest(p);distances.append(d);signed.append((p-pos).dot(n))
 report.append({'pose':pose,'samples':len(distances),'edge_distance_min_m':min(distances),'edge_distance_max_m':max(distances),'edge_distance_mean_m':sum(distances)/len(distances),'samples_more_than_2mm_inside':sum(x<-.002 for x in signed),'scope':'Outer rim to evaluated garment only; nearest-surface sign, not volumetric collision proof.'})
for k,v in saved.items():R[k]=v
R.update_tag();bpy.context.view_layer.update();(A/'mask_shoulder_fit_v10.json').write_text(json.dumps(report,indent=2));print('SHOULDER_FIT',json.dumps(report))
