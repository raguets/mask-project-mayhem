import bpy,gc,types,json
from pathlib import Path
A=Path('G:/DEV/mask-project-mayhem/art_source/Manta')
for f in gc.get_objects():
 if isinstance(f,types.FunctionType) and f.__name__=='step' and str(f.__globals__.get('out','')).replace('\\','/').endswith('/Manta/renders/v14'):
  if bpy.app.timers.is_registered(f):
   bpy.app.timers.unregister(f);f.__globals__['restore']();(A/'renders/v14/CANCELLED.json').write_text(json.dumps({'reason':'User identified assembly offsets; interrupted for repair. Completed images are not final.'}));print('REVIEW_STOPPED_AND_RESTORED')
S=bpy.context.scene;S.frame_set(1);bpy.context.view_layer.update()
from mathutils import Vector
def bounds(o):
 dg=bpy.context.evaluated_depsgraph_get();e=o.evaluated_get(dg);m=e.to_mesh();pts=[e.matrix_world@v.co for v in m.vertices];e.to_mesh_clear();return {'min':[min(p[i] for p in pts) for i in range(3)],'max':[max(p[i] for p in pts) for i in range(3)],'centroid':list(sum(pts,Vector())/len(pts))}
report={}
for n in ['MA_MainBody','MA_FrontWheel_1_Tire','MA_RearWheel_1_Tire','MA_RearLightPanel','MA_ReactorCassette','MA_SeatBase_1','MA_SeatBase_-1','MA_SeatBack_1','MA_SeatBack_-1','MA_RoofFrontCross','MA_RoofRearCross','MA_TbarRoof','MA_Windshield','MA_SteeringWheel']:
 o=bpy.data.objects[n];report[n]={'location':list(o.location),'world_location':list(o.matrix_world.translation),'parent':o.parent.name if o.parent else None,'matrix_inverse':[list(row) for row in o.matrix_parent_inverse]}
 if o.type in ['MESH','CURVE']:report[n]['bounds']=bounds(o)
for n in ['MA_FrontWheelFlip_1','MA_UnderbodyWingPivot_1','MA_RearWheelCarrier_1','MA_RearLightSpoilerHinge','MA_TripleReactorTravel','VanessaWarfield_Rig']:
 o=bpy.data.objects[n];report[n]={'location':list(o.location),'world_location':list(o.matrix_world.translation),'parent':o.parent.name if o.parent else None}
(A/'diagnose_assembly_v14.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
