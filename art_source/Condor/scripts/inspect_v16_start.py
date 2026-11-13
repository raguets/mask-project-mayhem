import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Condor'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Session_before_V16.blend'),copy=True,compress=True)
out={'file':bpy.data.filepath,'frame':bpy.context.scene.frame_current,'objects':[]}
for o in bpy.context.scene.objects:
 if any(k in o.name for k in ['RearWheel','RearFork','RotorSupport','Converging','MainBlade','Seat','Skid','HocusPocus','RearMonobloc','ChassisRail']):
  item={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'location':list(o.location),'world':list(o.matrix_world.translation),'drivers':[{'path':f.data_path,'index':f.array_index,'expr':f.driver.expression} for f in o.animation_data.drivers] if o.animation_data else []}
  if o.type=='MESH':
   ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();pts=[ev.matrix_world@v.co for v in me.vertices];item['bounds']=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)];ev.to_mesh_clear()
  if o.type=='CURVE':item['curve_points']=[[list(p.co) for p in sp.points] for sp in o.data.splines]
  out['objects'].append(item)
(A/'inspection_v16_start.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
