"""Read-only G0 audit executed by the installed Unreal Editor, never fabricates assets."""
import unreal,json,platform
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();lib=unreal.EditorAssetLibrary
report={'engine':unreal.SystemLibrary.get_engine_version(),'platform':platform.platform(),'vehicles':[],'fab':[],'maps':[],'python_classes':{}}
for name in ('PCGGraph','PCGComponent','EditorAssetLibrary','EditorLevelLibrary','LevelEditorSubsystem','DynamicMesh','GeometryScript_Primitives'):
    report['python_classes'][name]=hasattr(unreal,name)
for name in ('Thunderhawk','Rhino','Hurricane'):
    folder='/Game/MASK/'+name;definition=lib.load_asset(folder+'/DA_'+name);cls=unreal.load_class(None,folder+'/BP_'+name+'.BP_'+name+'_C')
    props={key:str(definition.get_editor_property(key)) for key in ('driver_name','driver_location','chassis','supports_flight','clearance_extent')}
    props['wheels']=[{'name':str(w.get_editor_property('name')),'center_cm':[w.get_editor_property('center').x,w.get_editor_property('center').y,w.get_editor_property('center').z]} for w in definition.get_editor_property('wheels')]
    props['name']=name;props['class']=cls.get_path_name();props['native_parent']=str(cls.get_super_class()) if hasattr(cls,'get_super_class') else str(cls)
    props['chassis_bounds']=str(definition.get_editor_property('chassis').get_imported_bounds());report['vehicles'].append(props)
registry=unreal.AssetRegistryHelpers.get_asset_registry()
registry.scan_paths_synchronous(['/Game/Fab','/Game/Maps'],force_rescan=True)
for data in registry.get_assets_by_path('/Game/Fab',recursive=True):
    if str(data.asset_class_path.asset_name)=='StaticMesh':
        asset=data.get_asset();report['fab'].append({'path':str(data.package_name),'class':str(data.asset_class_path),'bounds':str(asset.get_bounds()),'nanite':str(asset.get_editor_property('nanite_settings')),'metadata':dict(lib.get_metadata_tag_values(asset))})
direct=lib.load_asset('/Game/Fab/Megascans/3D/Small_Beach_Rock_wd4kfdx/Medium/wd4kfdx_tier_2/StaticMeshes/wd4kfdx_tier_2')
report['fab_direct_load']={'valid':bool(direct),'path':direct.get_path_name() if direct else None,'bounds':str(direct.get_bounds()) if direct else None}
for folder in ('/Game/Maps','/Game/MASK/Maps'):
    report['maps'] += [str(a.package_name) for a in registry.get_assets_by_path(folder,recursive=True) if str(a.asset_class_path.asset_name)=='World']
path=root/'Saved/SilentValley/environment-audit.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8');unreal.log('SILENT_VALLEY_AUDIT_COMPLETE '+str(path))
