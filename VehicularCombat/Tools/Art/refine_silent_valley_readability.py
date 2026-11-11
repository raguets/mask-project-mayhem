"""Refine existing blockout materials, lighting and signs; no new modeled asset.
Preserves route, Landscape geometry, vehicles, PCG, original materials and maps.
Run in Unreal's Python commandlet. Visual inspection remains a separate gate.
"""
import unreal, json, math, shutil, datetime, traceback
from pathlib import Path

ROOT=Path(unreal.Paths.project_dir()).resolve()
OUT=ROOT/'Saved/SilentValley/readability-v1';OUT.mkdir(parents=True,exist_ok=True)
MAP='/Game/MASK/Maps/SilentValley/L_SilentValley_Blockout'
FOLDER='/Game/MASK/Environment/SilentValley/Materials'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
editor=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
lib=unreal.EditorAssetLibrary;edit=unreal.MaterialEditingLibrary
report={'passed':False,'geometry_changed':False,'stage':'start'}

def find(label):return next((a for a in editor.get_all_level_actors() if a.get_actor_label()==label),None)
def owned(actor):
    if not actor or unreal.Name('SV_GENERATED') not in actor.tags:raise RuntimeError('Missing/unowned actor: '+str(actor))
    return actor
def spawn(cls,label,location,rotation):
    actor=find(label)
    if actor:owned(actor)
    else:
        actor=editor.spawn_actor_from_class(cls,location,rotation);actor.set_actor_label(label);actor.tags=[unreal.Name('SV_GENERATED')]
    actor.set_actor_location_and_rotation(location,rotation,False,True)
    return actor

try:
    backup=ROOT/'Saved/SilentValley/backups';backup.mkdir(exist_ok=True)
    shutil.copy2(ROOT/'Content/MASK/Maps/SilentValley/L_SilentValley_Blockout.umap',backup/('BeforeReadability-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.umap'))
    if not levels.load_level(MAP):raise RuntimeError('Cannot load isolated level')
    road=next(a for a in editor.get_all_level_actors() if isinstance(a,unreal.SilentValleyRoad))
    before=road.route_length_cm()
    report['stage']='surface'
    mat=unreal.load_asset(FOLDER+'/M_SV_ValleySurface_v4')
    if not mat:
        mat=unreal.AssetToolsHelpers.get_asset_tools().create_asset('M_SV_ValleySurface_v4',FOLDER,unreal.Material,unreal.MaterialFactoryNew())
        def node(cls,**properties):
            n=edit.create_material_expression(mat,cls)
            for k,v in properties.items():n.set_editor_property(k,v)
            return n
        def link(a,b,pin):
            names=list(edit.get_material_expression_input_names(b))
            if len(names)==1 and str(names[0])=='None':pin=''
            if not edit.connect_material_expressions(a,'',b,pin):raise RuntimeError('Shader connection '+pin+' '+str(names))
        def scalar(v):return node(unreal.MaterialExpressionConstant,r=v)
        def color(v):return node(unreal.MaterialExpressionConstant3Vector,constant=unreal.LinearColor(*v,1))
        def binary(cls,a,b):
            n=node(cls);link(a,n,'A');link(b,n,'B');return n
        def lerp(a,b,t):
            n=node(unreal.MaterialExpressionLinearInterpolate);link(a,n,'A');link(b,n,'B');link(t,n,'Alpha');return n
        pos=node(unreal.MaterialExpressionWorldPosition)
        def noise(scale):
            n=node(unreal.MaterialExpressionNoise,scale=scale,levels=1,quality=1,output_min=0.,output_max=1.);link(pos,n,'World Position');return n
        macro=noise(.0003);detail=noise(.035)
        meadow=lerp(color((.09,.125,.045)),color((.125,.145,.065)),macro)
        grain=lerp(scalar(.94),scalar(1.04),detail)
        meadow=binary(unreal.MaterialExpressionMultiply,meadow,grain)
        normal=node(unreal.MaterialExpressionVertexNormalWS)
        nz=node(unreal.MaterialExpressionComponentMask,r=False,g=False,b=True,a=False);link(normal,nz,'Input')
        weight=binary(unreal.MaterialExpressionMultiply,binary(unreal.MaterialExpressionSubtract,scalar(.94),nz),scalar(5.))
        slope=node(unreal.MaterialExpressionSaturate);link(weight,slope,'Input')
        rock=lerp(color((.15,.14,.11)),color((.175,.16,.13)),noise(.002))
        finish=lerp(meadow,rock,slope)
        edit.connect_material_property(finish,'',unreal.MaterialProperty.MP_BASE_COLOR)
        edit.connect_material_property(lerp(scalar(.82),scalar(.98),detail),'',unreal.MaterialProperty.MP_ROUGHNESS)
        edit.recompile_material(mat)
        if not lib.save_loaded_asset(mat,False):raise RuntimeError('Material save failed')
    landscape=owned(next(a for a in editor.get_all_level_actors() if isinstance(a,unreal.Landscape)))
    landscape.set_editor_property('landscape_material',mat)
    report['stage']='signs'
    signs=[]
    for cp in [a for a in editor.get_all_level_actors() if isinstance(a,unreal.SilentValleyCheckpoint)]:
        index=cp.get_editor_property('zone_index');name=cp.get_editor_property('zone_name')
        # ClosestDistance is native-only; sample the unchanged route for editor use.
        distance=min(range(4500,int(road.route_length_cm()),500),key=lambda d:(road.route_location(d)-cp.get_actor_location()).length_squared())-1800.
        distance=max(4500.,distance)
        p=road.route_location(distance);yaw=road.route_rotation(distance).yaw
        angle=math.radians(yaw);forward=unreal.Vector(math.cos(angle),math.sin(angle),0);right=unreal.Vector(-math.sin(angle),math.cos(angle),0)
        center=p+right*900+unreal.Vector(0,0,280)
        board=owned(find('SV_Sign_'+str(index)))
        board.set_actor_location_and_rotation(center,unreal.Rotator(yaw=yaw+180),False,True)
        board.set_actor_scale3d(unreal.Vector(.25,4.2,1.4))
        board.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        text=owned(find('SV_Label_'+name));tc=text.get_component_by_class(unreal.TextRenderComponent)
        text.set_actor_location_and_rotation(center-forward*16,unreal.Rotator(yaw=yaw+180),False,True)
        tc.set_world_size(50);tc.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER);tc.set_vertical_alignment(unreal.VerticalTextAligment.EVRTA_TEXT_CENTER)
        tc.set_text_render_color(unreal.Color(238,239,218,255))
        # Independent reverse face gives readable destinations on the return leg.
        back=spawn(unreal.TextRenderActor,'SV_Label_Return_'+str(index),center+forward*16,unreal.Rotator(yaw=yaw))
        bc=back.get_component_by_class(unreal.TextRenderComponent);bc.set_text(name);bc.set_world_size(50)
        bc.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER);bc.set_vertical_alignment(unreal.VerticalTextAligment.EVRTA_TEXT_CENTER)
        bc.set_text_render_color(unreal.Color(238,239,218,255))
        for side in (-1,1):
            post=spawn(unreal.StaticMeshActor,'SV_SignPost_'+str(index)+'_'+str(side),p+right*(900+side*170)+forward*20+unreal.Vector(0,0,120),unreal.Rotator(yaw=yaw))
            post.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'))
            post.static_mesh_component.set_material(0,unreal.load_asset(FOLDER+'/M_SV_Steel_Blockout'))
            post.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
            post.set_actor_scale3d(unreal.Vector(.12,.12,2.4))
        signs.append({'zone':name,'distance_m':distance/100,'center':[center.x,center.y,center.z],'yaw':yaw+180})
    report['stage']='lighting'
    sky=owned(find('SV_Skylight'));sky.light_component.set_editor_property('intensity',2.2)
    fill=spawn(unreal.DirectionalLight,'SV_AmbientFill',unreal.Vector(0,0,60000),unreal.Rotator(pitch=-35,yaw=-135))
    fill.tags=[unreal.Name('SV_GENERATED'),unreal.Name('SV_AMBIENT_FILL')]
    fill.light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
    fill.light_component.set_editor_property('intensity',.85);fill.light_component.set_editor_property('cast_shadows',False)
    fill.light_component.set_editor_property('atmosphere_sun_light',False)
    if abs(before-road.route_length_cm())>.01:raise RuntimeError('Route changed')
    if not levels.save_current_level():raise RuntimeError('Level save failed')
    report.update(passed=True,stage='SAVED',signs=signs,material=mat.get_path_name(),route_length_m=before/100,visual_validation='pending; no photorealism claim')
except Exception:
    report['error']=traceback.format_exc();unreal.log_error(report['error']);raise
finally:
    (OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
