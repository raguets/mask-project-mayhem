"""Shared legacy FBX and PBR import helpers; caller supplies project context."""
def import_fbx(filename,name,skeletal=False,skeleton=None,animate=False):
    task=unreal.AssetImportTask();task.filename=str(SOURCE/filename);task.destination_path=DEST;task.destination_name=name
    task.automated=True;task.replace_existing=True;task.save=True;task.factory=unreal.FbxFactory()
    options=unreal.FbxImportUI();options.automated_import_should_detect_type=False
    options.import_as_skeletal=skeletal;options.import_mesh=True;options.import_animations=animate
    options.import_materials=False;options.import_textures=False;options.create_physics_asset=skeletal and name.endswith('_Physics')
    options.mesh_type_to_import=unreal.FBXImportType.FBXIT_SKELETAL_MESH if skeletal else unreal.FBXImportType.FBXIT_STATIC_MESH
    if skeleton:options.skeleton=skeleton
    data=options.skeletal_mesh_import_data if skeletal else options.static_mesh_import_data
    data.import_uniform_scale=1.0
    data.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS
    if not skeletal:
        data.combine_meshes=False;data.transform_vertex_to_absolute=True
        data.generate_lightmap_u_vs=True;data.auto_generate_collision=False
    else:
        data.set_editor_property('import_content_type',unreal.FBXImportContentType.FBXICT_ALL)
        data.set_editor_property('use_t0_as_ref_pose',False);data.set_editor_property('update_skeleton_reference_pose',True)
    task.options=options
    assets.import_asset_tasks([task]);report['imported']+=list(task.imported_object_paths)
    return lib.load_asset(DEST+'/'+name) if skeletal else None

def texture(name):
    path=DEST+'/Textures/'+name
    if not lib.does_asset_exist(path):
        task=unreal.AssetImportTask();task.filename=str(SOURCE/(name+'.png'));task.destination_path=DEST+'/Textures'
        task.destination_name=name;task.automated=True;task.save=True
        assets.import_asset_tasks([task])
    return lib.load_asset(path)

def scalar(mat,value):
    node=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant,0,0)
    node.set_editor_property('r',float(value));return node

def material(part,slot,contract):
    key=re.sub(r'[^A-Za-z0-9_]','_',part+'_'+slot)
    path=DEST+'/Materials/MI2_'+key
    old=lib.load_asset(path) if lib.does_asset_exist(path) else None
    if old:return old
    edit=unreal.MaterialEditingLibrary
    glass='Glass' in part or contract.get('glass')
    master_name='M_MASK_Glass' if glass else 'M_MASK_PBR'
    master_path=DEST+'/Materials/'+master_name
    mat=lib.load_asset(master_path) if lib.does_asset_exist(master_path) else None
    if mat:
        pass
    elif glass:
        mat=assets.create_asset(master_name,DEST+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
        mat.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT)
        mat.set_editor_property('two_sided',True)
        mat.set_editor_property('translucency_lighting_mode',unreal.TranslucencyLightingMode.TLM_SURFACE_PER_PIXEL_LIGHTING)
        # UE 5.8 defaults to RM_None. A connected refraction input must opt in
        # before compilation; otherwise Material.cpp's active-input check fails.
        # Thin car panes must not use a bulk IOR screen offset: oblique flat
        # windows can sample outside scene colour and become grey after cooking.
        mat.set_editor_property('refraction_method',unreal.RefractionMode.RM_PIXEL_NORMAL_OFFSET)
        color=edit.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,0,0)
        color.set_editor_property('constant',unreal.LinearColor(.11,.18,.20,1))
        edit.connect_material_property(color,'',unreal.MaterialProperty.MP_BASE_COLOR)
        edit.connect_material_property(scalar(mat,.22),'',unreal.MaterialProperty.MP_OPACITY)
        edit.connect_material_property(scalar(mat,.08),'',unreal.MaterialProperty.MP_ROUGHNESS)
        edit.connect_material_property(scalar(mat,.5),'',unreal.MaterialProperty.MP_SPECULAR)
        edit.connect_material_property(scalar(mat,1.45),'',unreal.MaterialProperty.MP_REFRACTION)
    else:
        mat=assets.create_asset(master_name,DEST+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
        node=edit.create_material_expression(mat,unreal.MaterialExpressionTextureSampleParameter2D,0,0)
        node.set_editor_property('parameter_name','Atlas')
        node.set_editor_property('texture',texture(DEFAULT_ATLAS))
        edit.connect_material_property(node,'RGB',unreal.MaterialProperty.MP_BASE_COLOR)
        for parameter,value,prop in [('Metallic',0,unreal.MaterialProperty.MP_METALLIC),('Roughness',.5,unreal.MaterialProperty.MP_ROUGHNESS)]:
            scalar_node=edit.create_material_expression(mat,unreal.MaterialExpressionScalarParameter,0,0)
            scalar_node.set_editor_property('parameter_name',parameter);scalar_node.set_editor_property('default_value',value)
            edit.connect_material_property(scalar_node,'',prop)
    edit.set_material_usage(mat,unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH)
    edit.recompile_material(mat);lib.save_loaded_asset(mat)
    instance=assets.create_asset('MI2_'+key,DEST+'/Materials',unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
    edit.set_material_instance_parent(instance,mat)
    if not glass:
        edit.set_material_instance_texture_parameter_value(instance,'Atlas',texture(part+'_BaseColor'))
        edit.set_material_instance_scalar_parameter_value(instance,'Metallic',contract.get('metallic',0))
        edit.set_material_instance_scalar_parameter_value(instance,'Roughness',contract.get('roughness',.5))
    lib.save_loaded_asset(instance);return instance

def assign_materials(mesh,part,contracts,skeletal=False):
    slots=mesh.get_editor_property('materials') if skeletal else mesh.get_editor_property('static_materials')
    for index,slot in enumerate(slots):
        name=str(slot.get_editor_property('material_slot_name'))
        canonical=name.removeprefix('M_Game_')
        contract=next((m for m in contracts if m['name'].split('.')[0]==canonical),{})
        mat=material(part,name,contract)
        if skeletal:
            slot.set_editor_property('material_interface',mat)
            # unreal.Array struct iteration returns a value copy, not a mutable
            # array element. Write it back before assigning the materials array.
            slots[index]=slot
        else:mesh.set_material(index,mat)
    if skeletal:mesh.set_editor_property('materials',slots)
    lib.save_loaded_asset(mesh,False)

