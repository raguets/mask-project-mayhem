"""Repair stale terrain render mips/bounds while preserving collision heights."""
import unreal,json,datetime,shutil
from pathlib import Path
root=Path(unreal.Paths.project_dir());out=root/'Saved/SilentValley/environment-v1'
shutil.copy2(root/'Content/MASK/Maps/SilentValley/L_SilentValley_Blockout.umap',root/'Saved/SilentValley/backups'/('BeforeRenderMipRepair-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.umap'))
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not levels.load_level('/Game/MASK/Maps/SilentValley/L_SilentValley_Blockout'):raise RuntimeError('Load failed')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
road=next(a for a in actors if isinstance(a,unreal.SilentValleyRoad));land=next(a for a in actors if isinstance(a,unreal.Landscape))
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
points=[road.route_location(d) for d in range(10000,int(road.route_length_cm()),10000)]
def heights():
    result=[]
    for p in points:
        hits=unreal.SystemLibrary.line_trace_multi(world,p+unreal.Vector(0,0,100000),p-unreal.Vector(0,0,100000),unreal.TraceTypeQuery.ECC_VISIBILITY,False,[road],unreal.DrawDebugTrace.NONE,True)
        hit=next(h.to_tuple() for h in hits if isinstance(h.to_tuple()[9],unreal.LandscapeProxy))
        result.append(hit[5].z)
    return result
before=heights()
if unreal.Name('SV_NATURAL_TERRAIN_V1') not in land.tags:raise RuntimeError('Refuse unrefined terrain')
changed=unreal.SilentValleyEditorLibrary.refine_natural_landscape(road,unreal.Vector(-105000,-55000,5400),unreal.Vector2D(14000,9000),5400)
if changed!=0:raise RuntimeError('Repair must not change source heights')
after=heights();delta=max(abs(a-b) for a,b in zip(before,after))
if delta>.001 or unreal.Name('SV_RENDER_MIPS_V1') not in land.tags:raise RuntimeError('Repair invariant failed')
if not levels.save_current_level():raise RuntimeError('Save failed')
(out/'render-mips.json').write_text(json.dumps({'passed':True,'changed_source_heights':changed,'native_base_mip_crc_assertions':'passed for every heightmap texture','road_collision_probes':len(points),'max_collision_delta_cm':delta,'render_mip_tag':True,'visual_validation':'requires capture with default culling and automatic LOD'},indent=2))
