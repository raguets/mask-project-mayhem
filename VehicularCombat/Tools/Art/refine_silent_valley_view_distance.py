"""Preserve collision heights; retain terrain detail and fade grass at distance."""
import unreal,json,datetime,shutil,math
from pathlib import Path
root=Path(unreal.Paths.project_dir());out=root/'Saved/SilentValley/environment-v1'
source=root/'Content/MASK/Maps/SilentValley/L_SilentValley_Blockout.umap'
shutil.copy2(source,root/'Saved/SilentValley/backups'/('BeforeViewDistance-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.umap'))
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
levels.load_level('/Game/MASK/Maps/SilentValley/L_SilentValley_Blockout')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
land=next(a for a in actors if isinstance(a,unreal.Landscape))
before={n:land.get_editor_property(n) for n in ['lod0_screen_size','lod_distribution_setting','max_lod_level']}
land.set_editor_property('lod0_screen_size',.2)
land.set_editor_property('lod_distribution_setting',3.5)
land.set_editor_property('max_lod_level',2)
road=next(a for a in actors if isinstance(a,unreal.SilentValleyRoad))
route=[road.route_location(d) for d in range(0,int(road.route_length_cm()),2000)]
locked=0
for component in land.get_components_by_class(unreal.LandscapeComponent):
    # This map uses two 63-quad subsections at 2 m spacing (252 m/component).
    origin=component.get_world_location();half=12600
    x,y=origin.x+half,origin.y+half
    near=min(math.hypot(x-p.x,y-p.y) for p in route)<33000
    component.set_forced_lod(0 if near else -1)
    locked+=int(near)
edit=unreal.MaterialEditingLibrary;lib=unreal.EditorAssetLibrary;masters=set();groups=[]
for actor in actors:
    if not actor.get_actor_label().startswith('SV_Natural_Grass_'):continue
    component=actor.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
    component.set_cull_distances(10000,18000)
    for slot in range(component.get_num_materials()):
        mat=component.get_material(slot)
        while isinstance(mat,unreal.MaterialInstanceConstant):mat=mat.get_editor_property('parent')
        if mat.get_path_name() in masters:continue
        if not mat.get_path_name().startswith('/Game/MASK/Environment/SilentValley/Materials/'):raise RuntimeError('Refuse to edit imported master')
        masters.add(mat.get_path_name())
        node=edit.get_material_property_input_node(mat,unreal.MaterialProperty.MP_OPACITY_MASK)
        if node and node.get_editor_property('desc')!='SV_DISTANCE_FADE_V1':
            output=edit.get_material_property_input_node_output_name(mat,unreal.MaterialProperty.MP_OPACITY_MASK)
            fade=edit.create_material_expression(mat,unreal.MaterialExpressionPerInstanceFadeAmount)
            multiply=edit.create_material_expression(mat,unreal.MaterialExpressionMultiply)
            multiply.set_editor_property('desc','SV_DISTANCE_FADE_V1')
            edit.connect_material_expressions(node,output,multiply,'A')
            edit.connect_material_expressions(fade,'',multiply,'B')
            edit.connect_material_property(multiply,'',unreal.MaterialProperty.MP_OPACITY_MASK)
            edit.recompile_material(mat);lib.save_loaded_asset(mat,False)
    groups.append(actor.get_actor_label())
if not groups:raise RuntimeError('Planting must be saved before view-distance refinement')
if not levels.save_current_level():raise RuntimeError('Save failed')
(out/'view-distance.json').write_text(json.dumps({'passed':True,'terrain_before':before,'terrain_after':{'lod0_screen_size':.2,'lod_distribution_setting':3.5,'max_lod_level':2},'road_components_lod0':locked,'grass_fade_m':[100,180],'groups':groups,'visual_validation':'pending rendered comparison'},indent=2))
