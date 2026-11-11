"""Saved-level finishing: physical daylight, cloud detail, calm lake and bark bindings.
Only generated scene actors and local material copies are edited.
"""
import unreal,json,datetime,shutil
from pathlib import Path
root=Path(unreal.Paths.project_dir());out=root/'Saved/SilentValley/environment-v1'
shutil.copy2(root/'Content/MASK/Maps/SilentValley/L_SilentValley_Blockout.umap',root/'Saved/SilentValley/backups'/('BeforeAtmosphere-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.umap'))
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
registry=unreal.AssetRegistryHelpers.get_asset_registry();registry.search_all_assets(True)
registry.scan_paths_synchronous(['/Game/Megaplant_Library/Tree_Baltic_Pine','/Game/MASK/Environment/SilentValley'],True,True)
if not levels.load_level('/Game/MASK/Maps/SilentValley/L_SilentValley_Blockout'):raise RuntimeError('Load failed')
editor=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors=editor.get_all_level_actors()
lib=unreal.EditorAssetLibrary;edit=unreal.MaterialEditingLibrary
folder='/Game/MASK/Environment/SilentValley/Materials/'
def find(label):return next(a for a in actors if a.get_actor_label()==label)
water=find('SV_Lake_Surface_v1');water.static_mesh_component.set_collision_profile_name('NoCollision')
water.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
name='M_SV_LakeWater_v2'
mat=lib.load_asset(folder+name) if lib.does_asset_exist(folder+name) else lib.duplicate_asset(folder+'M_SV_LakeWater_v1',folder+name)
if not mat:raise RuntimeError('Water copy failed')
if not any(n.get_editor_property('desc')=='SV_CALM_WATER_V2' for n in edit.get_material_expressions(mat)):
    changes={.006:.0011,.011:.0017,.008:.0013,.055:.009,.05:.007,.14:.23,.15:.028,.11:.021,.12:.025}
    for node in edit.get_material_expressions(mat):
        if isinstance(node,unreal.MaterialExpressionConstant):
            value=node.get_editor_property('r')
            for old,new in changes.items():
                if abs(value-old)<1e-7:node.set_editor_property('r',new);break
    position=edit.create_material_expression(mat,unreal.MaterialExpressionWorldPosition)
    noise=edit.create_material_expression(mat,unreal.MaterialExpressionNoise)
    noise.set_editor_property('scale',.002);noise.set_editor_property('quality',1);noise.set_editor_property('levels',1)
    noise.set_editor_property('output_min',-.12);noise.set_editor_property('output_max',.12)
    edit.connect_material_expressions(position,'',noise,'World Position')
    for wave in list(edit.get_material_expressions(mat)):
        if not isinstance(wave,(unreal.MaterialExpressionSine,unreal.MaterialExpressionCosine)):continue
        phase=edit.get_inputs_for_material_expression(mat,wave)[0]
        offset=edit.create_material_expression(mat,unreal.MaterialExpressionAdd)
        offset.set_editor_property('desc','SV_CALM_WATER_V2')
        edit.connect_material_expressions(phase,'',offset,'A');edit.connect_material_expressions(noise,'',offset,'B')
        edit.connect_material_expressions(offset,'',wave,'Input')
    edit.recompile_material(mat)
if not lib.save_loaded_asset(mat,False):raise RuntimeError('Water save failed')
water.static_mesh_component.set_material(0,mat)

fixed=[]
textures='/Game/Megaplant_Library/Tree_Baltic_Pine/Textures/'
for suffix in ['Bark','Bark_Young']:
    instance=lib.load_asset(folder+'MI_SV_Env_MI_Baltic_Pine_01_'+suffix+'_SK_v1')
    if not instance:raise RuntimeError('Missing local bark instance')
    bark='T_Baltic_Pine_Sapling_Bark_' if suffix.endswith('Young') else 'T_Baltic_PineBark_02_'
    for parameter,tex in [('Base Color',bark+'C'),('Normal',bark+'NAH'),('Branch Base Color',bark+'C'),('Branch Normal',bark+'NAH')]:
        texture=lib.load_asset(textures+tex)
        if not texture:raise RuntimeError('Missing imported texture '+tex)
        edit.set_material_instance_texture_parameter_value(instance,parameter,texture)
    edit.update_material_instance(instance);lib.save_loaded_asset(instance,False);fixed.append(instance.get_name())

sun=find('SV_Sun').light_component;sun.set_editor_property('intensity',75000.)
sun.set_editor_property('temperature',6000.);sun.set_editor_property('light_source_angle',.65)
sun.set_editor_property('cast_cloud_shadows',True)
find('SV_AmbientFill').light_component.set_editor_property('intensity',.45)
find('SV_Skylight').light_component.set_editor_property('intensity',1.)
cloud=find('SV_VolumetricClouds').get_component_by_class(unreal.VolumetricCloudComponent)
cloud.set_editor_property('layer_height',1.8);cloud.set_editor_property('view_sample_count_scale',1.)
cloudmat=cloud.get_editor_property('material')
edit.set_material_instance_scalar_parameter_value(cloudmat,'Cloud_GlobalCoverage',-.12)
edit.set_material_instance_scalar_parameter_value(cloudmat,'Layout_CloudGlobalScale',128.)
edit.update_material_instance(cloudmat);lib.save_loaded_asset(cloudmat,False)
fog=find('SV_DistanceHaze').get_component_by_class(unreal.ExponentialHeightFogComponent)
fog.set_editor_property('fog_density',.0015);fog.set_editor_property('fog_height_falloff',.13)
fog.set_editor_property('enable_volumetric_fog',True)
exposure=next((a for a in actors if a.get_actor_label()=='SV_EnvironmentExposure_v1'),None)
if not exposure:
    exposure=editor.spawn_actor_from_class(unreal.PostProcessVolume,unreal.Vector(0,0,0))
    exposure.set_actor_label('SV_EnvironmentExposure_v1');exposure.tags=[unreal.Name('SV_GENERATED'),unreal.Name('SV_ENVIRONMENT_V1')]
exposure.set_editor_property('unbound',True);exposure.set_editor_property('priority',5.)
settings=exposure.get_editor_property('settings')
settings.set_editor_property('override_auto_exposure_method',True)
settings.set_editor_property('auto_exposure_method',unreal.AutoExposureMethod.AEM_HISTOGRAM)
for name,value in {'auto_exposure_min_brightness':.3,'auto_exposure_max_brightness':10000.,'auto_exposure_bias':-.3,'auto_exposure_speed_up':3.,'auto_exposure_speed_down':2.,'histogram_log_min':-8.,'histogram_log_max':16.}.items():
    settings.set_editor_property('override_'+name,True);settings.set_editor_property(name,value)
exposure.set_editor_property('settings',settings)
if not levels.save_current_level():raise RuntimeError('Map save failed')
(out/'atmosphere.json').write_text(json.dumps({'passed':True,'sun_lux':75000,'cloud_layer_bottom_km':2.2,'cloud_layer_height_km':1.8,'water_material':mat.get_path_name(),'water_collision_profile':str(water.static_mesh_component.get_collision_profile_name()),'bark_materials_rebound':fixed,'visual_validation':'pending rendered comparison'},indent=2),encoding='utf-8')
