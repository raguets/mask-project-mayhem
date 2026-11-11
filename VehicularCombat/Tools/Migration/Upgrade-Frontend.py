"""Run once through UE's installed PythonScriptPlugin commandlet after C++ build.

Reparents the original menu to its native extension. Its original designer tree,
Host/Join/Settings graphs and asset path remain intact. Original revision is in Git.
"""
import unreal

menu = unreal.load_asset('/Game/UI/WBP_MainMenu')
parent = unreal.load_class(None, '/Script/VehicularCombat.MainMenuWidget')
if not menu or not parent:
    raise RuntimeError('Original menu or compiled MainMenuWidget class is missing')
if not unreal.MathLibrary.class_is_child_of(menu.generated_class(), parent):
    unreal.BlueprintEditorLibrary.reparent_blueprint(menu, parent)
unreal.BlueprintEditorLibrary.compile_blueprint(menu)
if not unreal.EditorAssetLibrary.save_loaded_asset(menu, only_if_is_dirty=False):
    raise RuntimeError('Could not save the extended original menu')
unreal.log('VC_FRONTEND_UPGRADED /Game/UI/WBP_MainMenu')
