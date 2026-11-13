import bpy,json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');out=[]
for fr in [1,121]:
 bpy.context.scene.frame_set(fr);bpy.context.view_layer.update();entries=[]
 for o in bpy.data.collections['Condor_Vehicle'].all_objects:
  if o.type=='MESH' and o.name.startswith(('Condor_Rear_PersistentTire','Condor_Rear_Rim','Condor_Rear_Hub','Condor_ConvergingMast','Condor_RearMonobloc')):
   ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();p=[ev.matrix_world@v.co for v in me.vertices];bb=[[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)];ev.to_mesh_clear();entries.append({'name':o.name,'bounds':bb,'parent':o.parent.name if o.parent else None})
 out.append({'frame':fr,'spin':list(bpy.data.objects['Condor_TailRotorSpin'].matrix_world.translation),'objects':entries})
bpy.context.scene.frame_set(1);print(json.dumps(out));(P/'art_source/Condor/probe_wheel_v16.json').write_text(json.dumps(out,indent=2))
