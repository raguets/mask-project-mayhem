"""Shared Blender MCP mesh, atlas and FBX helpers. Caller provides OUT."""
import bpy, math
def write(name, data):
    (OUT/name).write_text(json.dumps(data, indent=2), encoding='utf-8')

def select(objects):
    bpy.ops.object.select_all(action='DESELECT')
    for ob in objects:
        ob.hide_set(False)
        ob.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]

def join(objects, name):
    select(objects)
    bpy.ops.object.join()
    ob = bpy.context.object
    ob.name = name
    return ob

def export(objects, name, skeletal=False, animations=False):
    select(objects)
    bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')), use_selection=True,
        object_types={'ARMATURE','MESH'} if skeletal else {'MESH'},
        axis_forward='-Y', axis_up='Z', add_leaf_bones=False,
        use_mesh_modifiers=True, bake_anim=animations,
        mesh_smooth_type='FACE',use_tspace=True,
        bake_anim_use_all_actions=animations, bake_anim_use_nla_strips=False,
        bake_anim_simplify_factor=0.0, path_mode='COPY', embed_textures=False)

def unwrap(ob):
    select([ob])
    # Keep source label UVs available to the material while baking into a NEW atlas.
    original=next((uv for uv in ob.data.uv_layers if uv.active_render),None)
    for slot in ob.material_slots:
        mat=slot.material
        if not mat or not mat.use_nodes or not original:continue
        for node in list(mat.node_tree.nodes):
            if node.type=='TEX_IMAGE' and not node.inputs['Vector'].is_linked:
                uv=mat.node_tree.nodes.new('ShaderNodeUVMap');uv.uv_map=original.name
                mat.node_tree.links.new(uv.outputs['UV'],node.inputs['Vector'])
    layer=ob.data.uv_layers.new(name='GameAtlas')
    ob.data.uv_layers.active=layer;layer.active_render=True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(70), island_margin=0.008)
    bpy.ops.object.mode_set(mode='OBJECT')

def triangulate(ob):
    select([ob])
    mod=ob.modifiers.new('GameTriangulation','TRIANGULATE')
    bpy.ops.object.modifier_apply(modifier=mod.name)

def reduce(ob, maximum):
    ob.data.calc_loop_triangles()
    n=len(ob.data.loop_triangles)
    if n > maximum:
        select([ob])
        mod=ob.modifiers.new('GameBudget','DECIMATE')
        mod.ratio=maximum/n
        bpy.ops.object.modifier_apply(modifier=mod.name)

def material_contract(materials):
    result=[]
    for mat in materials:
        if not mat: continue
        p=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if mat.use_nodes else None
        item={'name':mat.name,'base_color':list(mat.diffuse_color),'metallic':0.,'roughness':0.5,'glass':'Glass' in mat.name,
              'linked_inputs':[]}
        if p:
            item.update(base_color=list(p.inputs['Base Color'].default_value),metallic=p.inputs['Metallic'].default_value,
                        roughness=p.inputs['Roughness'].default_value)
            item['linked_inputs']=[s.name for s in p.inputs if s.is_linked]
        for n in mat.node_tree.nodes if mat.use_nodes else []:
            if n.type=='TEX_IMAGE' and n.image:
                # Preserve source label/logo textures in addition to the baked atlas.
                image_path=OUT/(n.image.name.replace('/','_')+'.png')
                n.image.save_render(str(image_path))
                item.setdefault('source_images',[]).append(image_path.name)
        result.append(item)
    return result

def bake_color(ob, name, size):
    """Bake the actual procedural color, without lights, into exported UV0."""
    unwrap(ob)
    image=bpy.data.images.new(name,width=size,height=size,alpha=False)
    image.filepath_raw=str(OUT/(name+'.png')); image.file_format='PNG'
    used=[]
    for slot in ob.material_slots:
        mat=slot.material
        if not mat: continue
        mat.use_nodes=True
        node=mat.node_tree.nodes.new('ShaderNodeTexImage'); node.image=image
        mat.node_tree.nodes.active=node
        p=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
        output=next((n for n in mat.node_tree.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output),None)
        emission=mat.node_tree.nodes.new('ShaderNodeEmission')
        saved=[(l.from_socket,l.to_socket) for l in list(output.inputs['Surface'].links)] if output else []
        if p:
            source=list(p.inputs['Base Color'].links)
            if source:mat.node_tree.links.new(source[0].from_socket,emission.inputs['Color'])
            else:emission.inputs['Color'].default_value=p.inputs['Base Color'].default_value
        if output:mat.node_tree.links.new(emission.outputs[0],output.inputs['Surface'])
        used.append((mat,node,emission,saved))
    scene=bpy.context.scene
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=1
    scene.render.bake.use_pass_direct=False;scene.render.bake.use_pass_indirect=False;scene.render.bake.use_pass_color=True
    scene.render.bake.margin=12
    select([ob])
    # Diffuse baking attenuates metals and makes the silver helmet/rims black.
    bpy.ops.object.bake(type='EMIT')
    image.save()
    for mat,node,emission,saved in used:
        mat.node_tree.nodes.remove(emission)
        for source,target in saved:mat.node_tree.links.new(source,target)
        mat.node_tree.nodes.remove(node)
    # Runtime TextureSample uses UV0. Export only the atlas, not the old label UVs.
    for layer in list(ob.data.uv_layers):
        if layer.name!='GameAtlas':ob.data.uv_layers.remove(layer)
    return image.name


