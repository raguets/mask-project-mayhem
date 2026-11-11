import unreal
p = r'G:/DEV/mask-project-mayhem/art_source/Thunderhawk/exports/THK_V0.fbx'
task = unreal.AssetImportTask()
task.filename = p
task.destination_path = '/Game/Thunderhawk'
task.automated = True
task.replace_existing = True
task.save = True
opts = unreal.FbxImportUI()
opts.import_as_skeletal = False
opts.import_animations = False
opts.static_mesh_import_data.combine_meshes = False
task.options = opts
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
unreal.log_warning('THK_IMPORT_RESULT: ' + str(task.imported_object_paths))
