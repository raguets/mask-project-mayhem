"""Run inside the installed Blender MCP session. Preserve source, inspect evaluated data."""
import bpy, json
from pathlib import Path
from mathutils import Vector

out = Path('G:/DEV/mask-project-mayhem/VehicularCombat/Saved/Art')
out.mkdir(parents=True, exist_ok=True)
backup = out / 'Thunderhawk_before_game_preparation.blend'
if not backup.exists():
    bpy.ops.wm.save_as_mainfile(filepath=str(backup), copy=True)
scene = bpy.context.scene
deps = bpy.context.evaluated_depsgraph_get()
data = {'file':bpy.data.filepath,'frame':scene.frame_current,'backup':str(backup),'collections':{},'meshes':[],'rigs':[],'controls':[],'materials':[]}
for coll in bpy.data.collections:
    data['collections'][coll.name] = {'objects':len(coll.all_objects),'hide_render':coll.hide_render}
for obj in scene.objects:
    if obj.type == 'ARMATURE':
        data['rigs'].append({'name':obj.name,'properties':{k:v for k,v in obj.items() if isinstance(v,(str,int,float,bool))},'matrix':[list(r) for r in obj.matrix_world],
          'bones':[{'name':b.name,'parent':b.parent.name if b.parent else None,'head':list(b.head_local),'tail':list(b.tail_local),'deform':b.use_deform} for b in obj.data.bones]})
    if obj.type == 'EMPTY':
        data['controls'].append({'name':obj.name,'parent':obj.parent.name if obj.parent else None,'location':list(obj.matrix_world.translation),'properties':{k:v for k,v in obj.items() if isinstance(v,(str,int,float,bool))}})
    if obj.type != 'MESH': continue
    evaluated = obj.evaluated_get(deps)
    mesh = evaluated.to_mesh()
    mesh.calc_loop_triangles()
    bounds = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    data['meshes'].append({'name':obj.name,'parent':obj.parent.name if obj.parent else None,'collections':[c.name for c in obj.users_collection],
      'hidden_render':obj.hide_render,'visible':obj.visible_get(),'vertices':len(obj.data.vertices),'evaluated_vertices':len(mesh.vertices),'triangles':len(mesh.loop_triangles),
      'uv_layers':len(mesh.uv_layers),'groups':[g.name for g in obj.vertex_groups],
      'modifiers':[{'type':m.type,'name':m.name,'viewport':m.show_viewport,'render':m.show_render} for m in obj.modifiers],
      'bounds_min':[min(p[a] for p in bounds) for a in range(3)],'bounds_max':[max(p[a] for p in bounds) for a in range(3)],
      'materials':[s.material.name if s.material else None for s in obj.material_slots]})
    evaluated.to_mesh_clear()
for mat in bpy.data.materials:
    nodes=[]
    if mat.use_nodes:
        for node in mat.node_tree.nodes:
            if node.type == 'BSDF_PRINCIPLED':
                nodes.append({key: {'linked':node.inputs[key].is_linked,'value':list(node.inputs[key].default_value) if key=='Base Color' else node.inputs[key].default_value} for key in ['Base Color','Metallic','Roughness','Transmission Weight']})
    data['materials'].append({'name':mat.name,'diffuse':list(mat.diffuse_color),'principled':nodes})
(out/'thunderhawk-source-audit.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
print(json.dumps({'audit':str(out/'thunderhawk-source-audit.json'),'meshes':len(data['meshes']),'rigs':[r['name'] for r in data['rigs']],
 'visible_triangles':sum(m['triangles'] for m in data['meshes'] if not m['hidden_render']),'controls':len(data['controls'])}))
