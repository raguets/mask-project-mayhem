import bpy,json
from pathlib import Path
from mathutils import Vector
s=bpy.context.scene;out={};src=bpy.data.objects['GEO-head_animation_realistic']
dg=bpy.context.evaluated_depsgraph_get()
for name in ['GEO-head_animation_realistic','GEO-head_animation_realistic.sclera.L','GEO-head_animation_realistic.sclera.R','Hand  - Realistic']:
    ob=bpy.data.objects[name];ev=ob.evaluated_get(dg);me=ev.to_mesh();vv=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear()
    out[name]={'vertices':len(vv),'min':[min(v[i] for v in vv) for i in range(3)],'max':[max(v[i] for v in vv) for i in range(3)],'modifiers':[{'type':m.type,'levels':getattr(m,'levels',None),'total_levels':getattr(m,'total_levels',None)} for m in ob.modifiers]}
out['rear']={}
for frame in [1,97]:
    s.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();out['rear'][frame]={}
    for ob in s.objects:
        if ob.name.startswith(('THK_Reactor','THK_RearPanel','THK_RearGlass','THK_RearBumper','THK_Headrest')):
            ev=ob.evaluated_get(dg);vv=[ev.matrix_world@Vector(v) for v in ev.bound_box]
            out['rear'][frame][ob.name]={'min':[min(v[i] for v in vv) for i in range(3)],'max':[max(v[i] for v in vv) for i in range(3)],'parent':ob.parent.name if ob.parent else None}
s.frame_set(97)
(Path('G:/DEV/mask-project-mayhem/docs/qa/anatomy_rear_measurements.json')).write_text(json.dumps(out,indent=2));print(json.dumps(out))
