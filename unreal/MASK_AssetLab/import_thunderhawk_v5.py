import unreal
p=r'G:/DEV/mask-project-mayhem/art_source/Thunderhawk/exports/THK_V5.fbx'
t=unreal.AssetImportTask(); t.filename=p; t.destination_path='/Game/Thunderhawk_V5'; t.automated=True; t.replace_existing=True; t.save=True
opts=unreal.FbxImportUI(); opts.import_as_skeletal=False; opts.import_animations=False; opts.static_mesh_import_data.combine_meshes=False; t.options=opts
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
unreal.log_warning('V5_IMPORTED '+str(t.imported_object_paths))
for name in ['THK_Body','THK_Wing_L','THK_Wing_R','THK_RearHatch']:
 obj=unreal.EditorAssetLibrary.load_asset('/Game/Thunderhawk_V5/'+name)
 if obj:
  b=obj.get_bounding_box(); unreal.log_warning('V5_BOUNDS_CM '+name+' min='+str(b.min)+' max='+str(b.max))
 else: unreal.log_error('V5_MISSING '+name)




