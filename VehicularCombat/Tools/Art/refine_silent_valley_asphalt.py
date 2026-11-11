"""Original asphalt surface variation; preserves paint, road mesh and collision.
Run in the real Editor. Keeps v2 and a dated map backup. No acquired assets.
"""
import unreal,json,shutil,datetime
from pathlib import Path
root=Path(unreal.Paths.project_dir());out=root/'Saved/SilentValley/asphalt-v3';out.mkdir(parents=True,exist_ok=True)
backup=root/'Saved/SilentValley/backups';backup.mkdir(exist_ok=True)
shutil.copy2(root/'Content/MASK/Maps/SilentValley/L_SilentValley_Blockout.umap',backup/('BeforeAsphalt-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.umap'))
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not levels.load_level('/Game/MASK/Maps/SilentValley/L_SilentValley_Blockout'):raise RuntimeError('Map load failed')
edit=unreal.MaterialEditingLibrary;lib=unreal.EditorAssetLibrary
folder='/Game/MASK/Environment/SilentValley/Materials';path=folder+'/M_SV_RoadMarked_v3'
mat=unreal.load_asset(path)
if not mat:
    mat=lib.duplicate_asset(folder+'/M_SV_RoadMarked_v2',path)
    if not mat:raise RuntimeError('Material duplication failed')
    base=edit.get_material_property_input_node(mat,unreal.MaterialProperty.MP_BASE_COLOR)
    def node(cls,**properties):
        n=edit.create_material_expression(mat,cls)
        for k,v in properties.items():n.set_editor_property(k,v)
        return n
    def link(a,b,pin):
        names=list(edit.get_material_expression_input_names(b))
        if len(names)==1 and str(names[0])=='None':pin=''
        if not edit.connect_material_expressions(a,'',b,pin):raise RuntimeError('Shader pin '+pin)
    def scalar(v):return node(unreal.MaterialExpressionConstant,r=v)
    def binary(cls,a,b):
        n=node(cls);link(a,n,'A');link(b,n,'B');return n
    def lerp(a,b,t):
        n=node(unreal.MaterialExpressionLinearInterpolate);link(a,n,'A');link(b,n,'B');link(t,n,'Alpha');return n
    pos=node(unreal.MaterialExpressionWorldPosition)
    def noise(scale):
        n=node(unreal.MaterialExpressionNoise,scale=scale,levels=1,quality=1,output_min=0.,output_max=1.);link(pos,n,'World Position');return n
    # World coordinates avoid restarting the grain on every spline segment.
    grain=noise(.25);macro=noise(.0015)
    variation=binary(unreal.MaterialExpressionMultiply,lerp(scalar(.75),scalar(1.13),grain),lerp(scalar(.94),scalar(1.04),macro))
    finish=binary(unreal.MaterialExpressionMultiply,base,variation)
    edit.connect_material_property(finish,'',unreal.MaterialProperty.MP_BASE_COLOR)
    edit.connect_material_property(lerp(scalar(.82),scalar(.97),grain),'',unreal.MaterialProperty.MP_ROUGHNESS)
    edit.recompile_material(mat)
if not lib.save_loaded_asset(mat,False):raise RuntimeError('Material save failed')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
road=next(a for a in actors if isinstance(a,unreal.SilentValleyRoad));length=road.route_length_cm()
road.set_editor_property('road_material',mat)
segments=road.get_editor_property('segments')
for segment in segments:segment.set_material(0,mat)
for actor in actors:
    if isinstance(actor,unreal.DirectionalLight):
        actor.light_component.set_editor_property('forward_shading_priority',0 if unreal.Name('SV_AMBIENT_FILL') in actor.tags else 1)
if not levels.save_current_level():raise RuntimeError('Map save failed')
report={'saved':True,'material':mat.get_path_name(),'segments':len(segments),'route_m':length/100,'geometry_changed':False,'new_external_assets':False,'visual_inspection':'required separately'}
(out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
