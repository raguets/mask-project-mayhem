"""Save the existing blockout material's required spline usage, without changing geometry."""
import unreal
mat=unreal.load_asset('/Game/MASK/Environment/SilentValley/Materials/M_SV_Asphalt_Blockout')
if not mat:raise RuntimeError('Expected generated asphalt material is missing')
mat.set_editor_property('used_with_spline_meshes',True)
unreal.MaterialEditingLibrary.recompile_material(mat)
if not unreal.EditorAssetLibrary.save_loaded_asset(mat,False):raise RuntimeError('Asphalt save failed')
unreal.log('SV_ASPHALT_SPLINE_USAGE_SAVED')
