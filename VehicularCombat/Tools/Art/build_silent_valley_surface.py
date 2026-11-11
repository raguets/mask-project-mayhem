"""Original dry-meadow/slope material foundation. No displacement or collision edits.
This is a procedural base coat, not a claim of a finished photorealistic surface.
"""
import unreal, shutil, datetime, json
from pathlib import Path

root = Path(unreal.Paths.project_dir())
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
lib = unreal.EditorAssetLibrary
edit = unreal.MaterialEditingLibrary
folder = '/Game/MASK/Environment/SilentValley/Materials'
path = folder + '/M_SV_ValleySurface_v2'
backup = root / 'Saved/SilentValley/backups'
backup.mkdir(parents=True, exist_ok=True)
shutil.copy2(root / 'Content/MASK/Maps/SilentValley/L_SilentValley_Blockout.umap',
             backup / ('BeforeSurface-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '.umap'))
if not levels.load_level('/Game/MASK/Maps/SilentValley/L_SilentValley_Blockout'):
    raise RuntimeError('Cannot load generated map')
material = unreal.load_asset(path)
if not material:
    material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        'M_SV_ValleySurface_v2', folder, unreal.Material, unreal.MaterialFactoryNew())

    def node(cls, **properties):
        result = edit.create_material_expression(material, cls)
        for key, value in properties.items():
            result.set_editor_property(key, value)
        return result

    def link(source, target, pin):
        available = list(edit.get_material_expression_input_names(target))
        if len(available) == 1 and str(available[0]) == 'None':
            pin = ''
        if not edit.connect_material_expressions(source, '', target, pin):
            raise RuntimeError('Material connection failed: ' + pin + ', inputs=' + str(available))

    def scalar(value):
        return node(unreal.MaterialExpressionConstant, r=value)

    def color(value):
        return node(unreal.MaterialExpressionConstant3Vector, constant=unreal.LinearColor(*value, 1))

    def binary(cls, a, b):
        result = node(cls)
        link(a, result, 'A')
        link(b, result, 'B')
        return result

    position = node(unreal.MaterialExpressionWorldPosition)
    noise = node(unreal.MaterialExpressionNoise, scale=.00008, levels=2, quality=1,
                 output_min=0., output_max=1.)
    link(position, noise, 'World Position')
    meadow = node(unreal.MaterialExpressionLinearInterpolate)
    link(color((.13, .17, .065)), meadow, 'A')
    link(color((.17, .19, .085)), meadow, 'B')
    link(noise, meadow, 'Alpha')
    normal = node(unreal.MaterialExpressionVertexNormalWS)
    vertical = node(unreal.MaterialExpressionComponentMask, r=False, g=False, b=True, a=False)
    link(normal, vertical, 'Input')
    slope = binary(unreal.MaterialExpressionSubtract, scalar(.93), vertical)
    slope = binary(unreal.MaterialExpressionMultiply, slope, scalar(4.))
    weight = node(unreal.MaterialExpressionSaturate)
    link(slope, weight, 'Input')
    finish = node(unreal.MaterialExpressionLinearInterpolate)
    link(meadow, finish, 'A')
    link(color((.21, .18, .135)), finish, 'B')
    link(weight, finish, 'Alpha')
    if not edit.connect_material_property(finish, '', unreal.MaterialProperty.MP_BASE_COLOR):
        raise RuntimeError('Cannot connect base color')
    edit.connect_material_property(scalar(.96), '', unreal.MaterialProperty.MP_ROUGHNESS)
    edit.recompile_material(material)
if not lib.save_loaded_asset(material, False):
    raise RuntimeError('Cannot save landscape material')
landscape = next(a for a in actors.get_all_level_actors() if isinstance(a, unreal.Landscape))
if unreal.Name('SV_GENERATED') not in landscape.tags:
    raise RuntimeError('Refusing to edit an unowned Landscape')
landscape.set_editor_property('landscape_material', material)
if not levels.save_current_level():
    raise RuntimeError('Cannot save landscape material assignment')
(root / 'Saved/SilentValley/surface-material.json').write_text(json.dumps({
    'saved': True, 'material': path, 'geometry_changed': False,
    'render_validation': 'pending; save does not prove shader or visual quality'
}, indent=2), encoding='utf-8')
unreal.log('SV_SURFACE_SAVED; rendered validation still required')
