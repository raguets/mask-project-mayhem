"""Read-only persisted material, sky and render-distance inspection."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir());out=root/'Saved/SilentValley/environment-v1'
unreal.AssetRegistryHelpers.get_asset_registry().search_all_assets(True)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level('/Game/MASK/Maps/SilentValley/L_SilentValley_Blockout')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
edit=unreal.MaterialEditingLibrary;seen=set();materials=[];sky=[]
def params(instance):
    master=instance
    while isinstance(master,unreal.MaterialInstanceConstant):master=master.get_editor_property('parent')
    return master
for actor in actors:
    label=actor.get_actor_label()
    if label.startswith('SV_Natural_'):
        for comp in actor.get_components_by_class(unreal.MeshComponent):
            for i in range(comp.get_num_materials()):
                mat=comp.get_material(i)
                if not mat or mat.get_path_name() in seen:continue
                seen.add(mat.get_path_name());master=params(mat)
                record={'instance':mat.get_path_name(),'master':master.get_path_name(),'attributes':master.get_editor_property('use_material_attributes'),'opacity_node':str(edit.get_material_property_input_node(master,unreal.MaterialProperty.MP_OPACITY_MASK))}
                if isinstance(mat,unreal.MaterialInstanceConstant):
                    record['textures']={str(n):str(edit.get_material_instance_texture_parameter_value(mat,n)) for n in edit.get_texture_parameter_names(master)}
                materials.append(record)
    if isinstance(actor,unreal.PostProcessVolume):
        s=actor.get_editor_property('settings');names=['auto_exposure_min_brightness','auto_exposure_max_brightness','auto_exposure_bias','override_auto_exposure_min_brightness','override_auto_exposure_max_brightness']
        sky.append({'actor':label,'postprocess':{n:str(s.get_editor_property(n)) for n in names}})
    if isinstance(actor,unreal.VolumetricCloud):
        comp=actor.get_component_by_class(unreal.VolumetricCloudComponent);mat=comp.get_editor_property('material');master=params(mat)
        sky.append({'actor':label,'scalars':{str(n):edit.get_material_instance_scalar_parameter_value(mat,n) for n in edit.get_scalar_parameter_names(master)}})
    if isinstance(actor,unreal.DirectionalLight):sky.append({'actor':label,'intensity':actor.light_component.get_editor_property('intensity')})
(out/'visual-audit.json').write_text(json.dumps({'materials':materials,'sky':sky},indent=2),encoding='utf-8')
