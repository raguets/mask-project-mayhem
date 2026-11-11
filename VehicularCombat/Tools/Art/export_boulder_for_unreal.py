"""Blender MCP only: evaluated copy of the existing V6 base, opened gate pose.
The authoring source and previous session remain intact. No new silhouette is modeled.
"""
import bpy,json,traceback,hashlib
from pathlib import Path
from mathutils import Matrix
ROOT=Path('G:/DEV/mask-project-mayhem');OUT=ROOT/'VehicularCombat/SourceArt/MASK/BoulderHill';OUT.mkdir(parents=True,exist_ok=True)
source=ROOT/'art_source/Boulder_Hill/BoulderHill_V6_Base.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'VehicularCombat/Saved/SilentValley/blender-session-before-boulder-uv.blend'),copy=True)
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.scene.frame_set(211);bpy.context.view_layer.update()
report={'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'frame':211,'state':'Existing defense-open pose; static first integration, no runtime mechanism animation claimed.','materials':{},'excluded':['BH_DesertGround'],'parts':[]}
copies=[];deps=bpy.context.evaluated_depsgraph_get()
for ob in list(bpy.context.scene.objects):
    if ob.type not in ('MESH','FONT','CURVE') or not ob.name.startswith('BH_') or ob.name=='BH_DesertGround' or ob.hide_render:continue
    evaluated=ob.evaluated_get(deps)
    mesh=bpy.data.meshes.new_from_object(evaluated,depsgraph=deps);mesh.transform(Matrix.Scale(100,4)@evaluated.matrix_world)
    clone=bpy.data.objects.new('SV_'+ob.name,mesh);bpy.context.scene.collection.objects.link(clone);copies.append(clone);report['parts'].append(ob.name)
    for material in mesh.materials:
        if not material or material.name in report['materials']:continue
        data={'color':list(material.diffuse_color),'roughness':material.roughness,'metallic':material.metallic}
        if material.use_nodes:
            shader=next((n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
            if shader:
                if not shader.inputs['Base Color'].is_linked:data['color']=list(shader.inputs['Base Color'].default_value)
                data['roughness']=shader.inputs['Roughness'].default_value;data['metallic']=shader.inputs['Metallic'].default_value
        report['materials'][material.name]=data
vertices=[];faces=[];indices=[];smooth=[];materials=[]
for ob in copies:
    offset=len(vertices);vertices.extend(tuple(v.co) for v in ob.data.vertices)
    local=[]
    for mat in ob.data.materials:
        if mat not in materials:materials.append(mat)
        local.append(materials.index(mat))
    for polygon in ob.data.polygons:
        faces.append(tuple(offset+i for i in polygon.vertices));indices.append(local[polygon.material_index] if local else 0);smooth.append(polygon.use_smooth)
combined=bpy.data.meshes.new('BoulderHill_V6_Open');combined.from_pydata(vertices,[],faces);combined.update()
uv=combined.uv_layers.new(name='UnrealPlanarUV')
for poly in combined.polygons:
    dominant=max(range(3),key=lambda i:abs(poly.normal[i]));a,b=((1,2),(0,2),(0,1))[dominant]
    for loop_index in poly.loop_indices:
        co=combined.vertices[combined.loops[loop_index].vertex_index].co;uv.data[loop_index].uv=(co[a]/200,co[b]/200)
for mat in materials:combined.materials.append(mat)
for poly,index,soft in zip(combined.polygons,indices,smooth):poly.material_index=index;poly.use_smooth=soft
joined=bpy.data.objects.new('BoulderHill_V6_Open',combined);bpy.context.scene.collection.objects.link(joined)
for ob in list(bpy.data.objects):
    if ob!=joined:bpy.data.objects.remove(ob,do_unlink=True)
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=.01
joined.select_set(True);bpy.context.view_layer.objects.active=joined
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'BoulderHill_GameReady_v2.blend'))
bpy.ops.export_scene.fbx(filepath=str(OUT/'BoulderHill_V6_Open_v2.fbx'),use_selection=False,object_types={'MESH'},axis_forward='-Y',axis_up='Z',bake_anim=False,use_mesh_modifiers=True,mesh_smooth_type='FACE',path_mode='AUTO')
(OUT/'manifest_v2.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'VehicularCombat/Saved/SilentValley/blender-session-before-boulder-uv.blend'))
print('BOULDER_EXPORT_COMPLETE; source unchanged; session restored')
