import bpy,json
from mathutils import Vector
r=bpy.data.objects['MattTrakker_Rig'];r['driving_pose']=1;r.update_tag();bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
out={}
for n in ['MT_GlovePalm_L','MT_GlovePalm_R','MT_Head_AnatomicalSurface','MT_Eyeball_L','THK_SeatBack_L','THK_Headrest_L','MT_ContinuousSleeve_L']:
 o=bpy.data.objects.get(n)
 if not o:continue
 ev=o.evaluated_get(dg);bb=[ev.matrix_world@Vector(v) for v in ev.bound_box]
 out[n]={'location':list(o.location),'rotation':list(o.rotation_euler),'groups':[g.name for g in o.vertex_groups],'bbox_min':[min(v[i] for v in bb) for i in range(3)],'bbox_max':[max(v[i] for v in bb) for i in range(3)],'mesh_center':list(sum((v.co for v in o.data.vertices),Vector())/len(o.data.vertices)) if o.type=='MESH' else None}
for n in ['hand.L','forearm.L','head']:
 p=r.pose.bones[n];out[n]={'head':list(r.matrix_world@p.head),'tail':list(r.matrix_world@p.tail),'loc':list(p.location),'rot':list(p.rotation_quaternion)}
print(json.dumps(out))
