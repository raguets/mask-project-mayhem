import bpy,json
S=bpy.context.scene
print(json.dumps({'file':bpy.data.filepath,'scene':S.name,'frame':S.frame_current,'render_job':bpy.app.driver_namespace.get('_mask_asset_review_active'),'stone_materials':[{'name':m.name,'diffuse':list(m.diffuse_color),'ramps':[[[e.position,list(e.color)] for e in n.color_ramp.elements] for n in m.node_tree.nodes if n.type=='VALTORGB']} for m in bpy.data.materials if m.use_nodes and 'Sandstone' in m.name]},indent=2))
