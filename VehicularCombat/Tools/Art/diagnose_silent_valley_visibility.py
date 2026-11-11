"""Diagnostic of plane backface visibility; preserve prior material asset first."""
import unreal,shutil
from pathlib import Path
root=Path(unreal.Paths.project_dir());source=root/'Content/MASK/Environment/SilentValley/Materials/M_SV_Asphalt_Blockout.uasset'
backup=root/'Saved/SilentValley/backups/Asphalt-before-two-sided.uasset'
if not backup.exists():shutil.copy2(source,backup)
mat=unreal.load_asset('/Game/MASK/Environment/SilentValley/Materials/M_SV_Asphalt_Blockout')
mat.set_editor_property('two_sided',True);mat.set_editor_property('used_with_spline_meshes',True)
unreal.MaterialEditingLibrary.recompile_material(mat)
if not unreal.EditorAssetLibrary.save_loaded_asset(mat,False):raise RuntimeError('Material save failed')
