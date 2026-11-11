"""Replace the reversed-winding prototype, preserving the playable terrain."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir())
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not levels.load_level('/Game/MASK/Maps/SilentValley/L_SilentValley_Blockout'):raise RuntimeError('Load failed')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
actor=next(a for a in actors if a.get_actor_label()=='SV_Distant_Ridges_v1')
before=str(actor.get_actor_transform())
lib=unreal.EditorAssetLibrary
folder='/Game/MASK/Environment/SilentValley/Materials/'
path=folder+'M_SV_DistantTerrain_v1'
mat=lib.load_asset(path) if lib.does_asset_exist(path) else lib.duplicate_asset(folder+'M_SV_NaturalTerrain_v1',path)
mat.set_editor_property('two_sided',False)
unreal.MaterialEditingLibrary.recompile_material(mat)
if not lib.save_loaded_asset(mat,False):raise RuntimeError('Save material failed')
actor.set_actor_location(unreal.Vector(),False,True)
actor.set_actor_rotation(unreal.Rotator(),False)
actor.set_actor_scale3d(unreal.Vector(1,1,1))
mesh_path='/Game/MASK/Environment/SilentValley/Terrain/SM_SV_DistantTerrain_v2'
mesh=lib.load_asset(mesh_path) if lib.does_asset_exist(mesh_path) else unreal.SilentValleyEditorLibrary.create_distant_terrain(mesh_path)
if not mesh or not lib.save_loaded_asset(mesh,False):raise RuntimeError('Save revised mesh failed')
actor.static_mesh_component.set_static_mesh(mesh)
actor.static_mesh_component.set_material(0,mat)
audit=[{'name':a.get_name(),'label':a.get_actor_label(),'transform':str(a.get_actor_transform()),'bounds':str(a.get_actor_bounds(False))} for a in actors if a.get_name()=='StaticMeshActor_6' or 'Quarry' in a.get_actor_label()]
if not levels.save_current_level():raise RuntimeError('Save level failed')
(root/'Saved/SilentValley/environment-v1/vista-seam.json').write_text(json.dumps({'before_transform':before,'after_transform':str(actor.get_actor_transform()),'two_sided':False,'mesh':mesh_path,'quarry':audit},indent=2),encoding='utf-8')
report_path=root/'Saved/SilentValley/environment-v1/vistas.json'
report=json.loads(report_path.read_text(encoding='utf-8'));report['backdrop_mesh']=mesh.get_path_name();report['visual_validation']='pending corrected-winding captures'
report_path.write_text(json.dumps(report,indent=2),encoding='utf-8')
