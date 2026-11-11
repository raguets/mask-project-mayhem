"""Original road paint shader, real Editor assets, no vehicle or collision change."""
import unreal,shutil,datetime
from pathlib import Path
root=Path(unreal.Paths.project_dir());map_path='/Game/MASK/Maps/SilentValley/L_SilentValley_Blockout'
out=root/'Saved/SilentValley/backups';out.mkdir(parents=True,exist_ok=True)
shutil.copy2(root/'Content/MASK/Maps/SilentValley/L_SilentValley_Blockout.umap',out/('BeforeRoadPaint-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.umap'))
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not levels.load_level(map_path):raise RuntimeError('Map load failed')
lib=unreal.EditorAssetLibrary;edit=unreal.MaterialEditingLibrary;assets=unreal.AssetToolsHelpers.get_asset_tools()
folder='/Game/MASK/Environment/SilentValley/Materials';path=folder+'/M_SV_RoadMarked_v2'
mat=unreal.load_asset(path)
if not mat:
    mat=assets.create_asset('M_SV_RoadMarked_v2',folder,unreal.Material,unreal.MaterialFactoryNew())
    def node(cls,**properties):
        n=edit.create_material_expression(mat,cls)
        for k,v in properties.items():n.set_editor_property(k,v)
        return n
    def scalar(v):return node(unreal.MaterialExpressionConstant,r=v)
    def color(r,g,b):return node(unreal.MaterialExpressionConstant3Vector,constant=unreal.LinearColor(r,g,b,1))
    def link(a,b,pin):
        pin={'AGreaterThanB':'A > B','ALessThanB':'A < B','AEqualsB':'A == B'}.get(pin,pin)
        available=list(edit.get_material_expression_input_names(b))
        name=next((str(n) for n in available if str(n).replace(' ','')==pin.replace(' ','')),pin)
        if len(available)==1 and str(available[0])=='None':name=''
        if not edit.connect_material_expressions(a,'',b,name):raise RuntimeError('Cannot connect '+pin+'; available '+str(available))
    def binary(cls,a,b):
        n=node(cls);link(a,n,'A');link(b,n,'B');return n
    def less(a,value):
        n=node(unreal.MaterialExpressionIf);link(a,n,'A');link(scalar(value),n,'B');link(scalar(0),n,'AGreaterThanB');link(scalar(1),n,'ALessThanB');link(scalar(1),n,'AEqualsB');return n
    uv=node(unreal.MaterialExpressionTextureCoordinate)
    y=node(unreal.MaterialExpressionComponentMask,r=False,g=True,b=False,a=False);link(uv,y,'Input')
    x=node(unreal.MaterialExpressionComponentMask,r=True,g=False,b=False,a=False);link(uv,x,'Input')
    distance=node(unreal.MaterialExpressionAbs);link(binary(unreal.MaterialExpressionSubtract,y,scalar(.5)),distance,'Input')
    center=less(distance,.009)
    dashed=node(unreal.MaterialExpressionFrac);link(binary(unreal.MaterialExpressionMultiply,x,scalar(4)),dashed,'Input')
    center=binary(unreal.MaterialExpressionMultiply,center,less(dashed,.55))
    edge=binary(unreal.MaterialExpressionSubtract,less(distance,.475),less(distance,.46))
    base=node(unreal.MaterialExpressionLinearInterpolate);link(color(.035,.04,.045),base,'A');link(color(.85,.6,.04),base,'B');link(center,base,'Alpha')
    painted=node(unreal.MaterialExpressionLinearInterpolate);link(base,painted,'A');link(color(.7,.72,.65),painted,'B');link(edge,painted,'Alpha')
    edit.connect_material_property(painted,'',unreal.MaterialProperty.MP_BASE_COLOR);edit.connect_material_property(scalar(.9),'',unreal.MaterialProperty.MP_ROUGHNESS)
    mat.set_editor_property('two_sided',True);mat.set_editor_property('used_with_spline_meshes',True);edit.recompile_material(mat)
if not lib.save_loaded_asset(mat,False):raise RuntimeError('Road material save failed')
road=next(a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors() if isinstance(a,unreal.SilentValleyRoad))
road.set_editor_property('road_material',mat)
for segment in road.get_editor_property('segments'):segment.set_material(0,mat)
for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    # Coincident road/apron faces caused alternating triangles in the quarry
    # and ridge screenshots. Three centimetres separates the surfaces without
    # creating a vehicle-sized step; absolute positions keep reruns idempotent.
    targets={'SV_Quarry_Apron':unreal.Vector(65000,97000,9947),'SV_NorthRidge_Turnaround':unreal.Vector(-55000,125000,15947)}
    if actor.get_actor_label() in targets:actor.set_actor_location(targets[actor.get_actor_label()],False,True)
if not levels.save_current_level():raise RuntimeError('Map save failed')
unreal.log('SV_ROAD_PAINT_COMPLETE; visual-only material, collision unchanged')
