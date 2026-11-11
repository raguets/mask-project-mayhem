"""Read the live MCP scene before the V12 fit/footwear correction pass."""
import bpy, json
from mathutils import Vector
s=bpy.context.scene
r=bpy.data.objects['MattTrakker_Rig']
out={'file':bpy.data.filepath,'dirty':bpy.data.is_dirty,'frame':s.frame_current,
     'rig_location':list(r.location),'controls':dict(r.items()),'objects':{}}
dg=bpy.context.evaluated_depsgraph_get()
for ob in s.objects:
    if ob.name.startswith(('MT_Boot','MT_Glove','MT_Finger','MT_Thumb','THK_Pedal','THK_Steer','THK_Seat','THK_Headrest','THK_RearPanel','THK_Reactor_Deploy')):
        ev=ob.evaluated_get(dg)
        vv=[ev.matrix_world@Vector(v) for v in ev.bound_box]
        out['objects'][ob.name]={'type':ob.type,'location':list(ob.location),
            'min':[min(v[i] for v in vv) for i in range(3)],
            'max':[max(v[i] for v in vv) for i in range(3)],
            'groups':[g.name for g in ob.vertex_groups],
            'parent':ob.parent.name if ob.parent else None,
            'materials':[m.name for m in ob.data.materials] if ob.type=='MESH' else []}
out['pose']={b.name:{'head':list(r.matrix_world@b.head),'tail':list(r.matrix_world@b.tail)} for b in r.pose.bones}
out['render']={'camera':s.camera.name if s.camera else None,'engine':s.render.engine}
print(json.dumps(out))
