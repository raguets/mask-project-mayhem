import bpy,json
from mathutils import Vector
from pathlib import Path
s=bpy.context.scene;s.frame_set(1);result={'source':bpy.data.filepath,'wheel_centres':{},'references_missing':[]}
for name in ['THK_Tire_FL','THK_Tire_FR','THK_Tire_RL','THK_Tire_RR']:
    o=bpy.data.objects[name];vv=[o.matrix_world@v.co for v in o.data.vertices];c=sum(vv,Vector())/len(vv)
    result['wheel_centres'][name]=list(c)
    result.setdefault('tire_dimensions',{})[name]=[max(v[i] for v in vv)-min(v[i] for v in vv) for i in range(3)]
result['actual_tire_wheelbase_m']=result['wheel_centres']['THK_Tire_FL'][0]-result['wheel_centres']['THK_Tire_RL'][0]
result['debug_transforms']={n:{'world':list(bpy.data.objects[n].matrix_world.translation),'local':list(bpy.data.objects[n].location),'first_vertex':list(bpy.data.objects[n].data.vertices[0].co) if bpy.data.objects[n].type=='MESH' else None} for n in ('THK_Root','THK_WheelPivot_FL','THK_Tire_FL','THK_WheelPivot_RL','THK_Tire_RL')}
for ob in bpy.data.collections['THK9_Reference'].objects:
    if ob.data and not Path(bpy.path.abspath(ob.data.filepath)).exists():result['references_missing'].append(ob.name)
result['mesh_objects']=sum(o.type=='MESH' for o in bpy.data.collections['THK9_Exterior'].objects)
(Path('G:/DEV/mask-project-mayhem/art_source/Thunderhawk')/'final_measurements_v9.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
