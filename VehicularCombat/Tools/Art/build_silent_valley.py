"""G1 Unreal Editor build. Real assets only, isolated namespace, resumable stages.
Never modifies the original maps, vehicle assets or Blender sources.
"""
import unreal,json,math,traceback,shutil,datetime
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir()).resolve();OUT=ROOT/'Saved/SilentValley';OUT.mkdir(parents=True,exist_ok=True)
MAP='/Game/MASK/Maps/SilentValley/L_SilentValley_Blockout';ENV='/Game/MASK/Environment/SilentValley'
lib=unreal.EditorAssetLibrary;assets=unreal.AssetToolsHelpers.get_asset_tools();edit=unreal.MaterialEditingLibrary
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
report={'passed':False,'stage':'start','map':MAP}
registry=unreal.AssetRegistryHelpers.get_asset_registry();registry.search_all_assets(True);registry.scan_paths_synchronous(['/Game/Core','/Game/Fab','/Game/MASK'],True,True)
def mark(stage):
    report['stage']=stage;(OUT/'build-report.json').write_text(json.dumps(report,indent=2,default=str),encoding='utf-8');unreal.log('SV_BUILD_STAGE '+stage)
def asset(name,folder,cls,factory):
    path=folder+'/'+name
    return lib.load_asset(path) if lib.does_asset_exist(path) else assets.create_asset(name,folder,cls,factory)
def constant(mat,value):
    node=edit.create_material_expression(mat,unreal.MaterialExpressionConstant);node.set_editor_property('r',value);return node
def material(name,color,roughness=.85,metallic=0):
    path=ENV+'/Materials/'+name
    if lib.does_asset_exist(path):return lib.load_asset(path)
    mat=asset(name,ENV+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
    node=edit.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector);node.set_editor_property('constant',unreal.LinearColor(*color,1))
    edit.connect_material_property(node,'',unreal.MaterialProperty.MP_BASE_COLOR)
    edit.connect_material_property(constant(mat,roughness),'',unreal.MaterialProperty.MP_ROUGHNESS)
    edit.connect_material_property(constant(mat,metallic),'',unreal.MaterialProperty.MP_METALLIC);edit.recompile_material(mat);lib.save_loaded_asset(mat);return mat
def find(label):return next((a for a in actors.get_all_level_actors() if a.get_actor_label()==label),None)
def spawn(cls,label,location,rotation=(0,0,0)):
    ob=find(label)
    orientation=unreal.Rotator(pitch=rotation[0],yaw=rotation[1],roll=rotation[2])
    if ob:
        if unreal.Name('SV_GENERATED') not in ob.tags:raise RuntimeError('Refusing to modify an untagged actor: '+label)
        ob.set_actor_location_and_rotation(unreal.Vector(*location),orientation,False,True)
        return ob
    ob=actors.spawn_actor_from_class(cls,unreal.Vector(*location),orientation);ob.set_actor_label(label);ob.tags=[unreal.Name('SV_GENERATED')];return ob
def box(label,position,size,mat):
    ob=spawn(unreal.StaticMeshActor,label,position);component=ob.static_mesh_component;component.set_static_mesh(lib.load_asset('/Engine/BasicShapes/Cube'))
    component.set_material(0,mat);component.set_collision_profile_name('BlockAll');ob.set_actor_scale3d(unreal.Vector(*(v/100 for v in size)));return ob
def label(text,position,yaw=0,size=180):
    ob=spawn(unreal.TextRenderActor,'SV_Label_'+text,position,(0,yaw,0));component=ob.get_component_by_class(unreal.TextRenderComponent)
    component.set_text(text);component.set_world_size(size);component.set_text_render_color(unreal.Color(230,217,170,255));return ob
try:
    # Resume only this generated map, preserving the on-disk previous stage first.
    if lib.does_asset_exist(MAP):
        file=ROOT/'Content/MASK/Maps/SilentValley/L_SilentValley_Blockout.umap'
        backup=OUT/'backups';backup.mkdir(exist_ok=True)
        if file.exists():shutil.copy2(file,backup/('Blockout-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.umap'))
        if not levels.load_level(MAP):raise RuntimeError('Cannot reload generated map')
    elif not levels.new_level(MAP):raise RuntimeError('Cannot create new map')
    mark('materials')
    grass=lib.load_asset(ENV+'/Materials/M_SV_ValleySurface_v2') if lib.does_asset_exist(ENV+'/Materials/M_SV_ValleySurface_v2') else material('M_SV_BlockoutTerrain',(.13,.18,.075))
    asphalt=material('M_SV_Asphalt_Blockout',(.055,.06,.065));concrete=material('M_SV_Concrete_Blockout',(.24,.25,.23));sign=material('M_SV_SignGreen',(.025,.09,.06));steel=material('M_SV_Steel_Blockout',(.13,.16,.18),.5,.6)
    asphalt.set_editor_property('two_sided',True);asphalt.set_editor_property('used_with_spline_meshes',True);edit.recompile_material(asphalt);lib.save_loaded_asset(asphalt)
    if lib.does_asset_exist(ENV+'/Materials/M_SV_RoadMarked_v2'):asphalt=lib.load_asset(ENV+'/Materials/M_SV_RoadMarked_v2')
    meshpath=ENV+'/Roads/SM_SV_RoadRibbon'
    ribbon=lib.load_asset(meshpath) if lib.does_asset_exist(meshpath) else unreal.SilentValleyEditorLibrary.create_road_ribbon(meshpath)
    if not ribbon:raise RuntimeError('Road mesh creation failed')
    lib.save_loaded_asset(ribbon)
    mark('route')
    # First points follow the existing garage aisle and diagonal gate; units cm.
    local=[(800,-1800,0),(300,-900,0),(300,-300,0),(500,450,0),(950,900,0),(1700,1650,0),(4000,3000,0)]
    points=[unreal.Vector(-135000+x,-110000+y,8000+z) for x,y,z in local]
    world=[(-125000,-104000,8000),(-95000,-83000,8500),(-75000,-78000,9000),(-48000,-108000,10000),(-16000,-100000,10500),(23000,-78000,11500),(65000,-57000,13000),(105000,-15000,15500),(70000,25000,15500),(105000,55000,12500),(90000,93000,10000),(75000,95000,10000),(65000,95000,10000),(55000,95000,10000),(10000,115000,13000),(-45000,122000,16000),(-55000,125000,16000),(-65000,125000,16000),(-115000,90000,13000),(-157000,30000,10000),(-160000,-80000,8000),(-155000,-115000,8000),(-140000,-125000,8000),(-125000,-125000,8000),(-117000,-115000,8000),(-120000,-108000,8000),(-125000,-106000,8000),(-131000,-107000,8000)]
    points += [unreal.Vector(*p) for p in world]
    road=spawn(unreal.SilentValleyRoad,'SV_MainRoad',(0,0,0));road.set_editor_property('waypoints',points);road.set_editor_property('road_mesh',ribbon);road.set_editor_property('road_material',asphalt);road.set_editor_property('width_cm',1000.);road.set_editor_property('closed_route',False);road.rebuild_road()
    report['route_length_m']=road.route_length_cm()/100.;report['road_segments']=len(road.get_editor_property('segments'))
    mark('landscape')
    terrain=unreal.SilentValleyEditorLibrary.create_blockout_landscape(road,grass)
    if not terrain:raise RuntimeError('Native Landscape import failed')
    terrain.tags=[unreal.Name('SV_GENERATED')]
    levels.save_current_level();mark('garage')
    boulderpath=ENV+'/Structures/BoulderHill/SM_BoulderHill_V6_Open_v2'
    source=ROOT/'SourceArt/MASK/BoulderHill/BoulderHill_V6_Open_v2.fbx'
    if source.exists() and not lib.does_asset_exist(boulderpath):
        unreal.SystemLibrary.execute_console_command(None,'Interchange.FeatureFlags.Import.FBX 0')
        task=unreal.AssetImportTask();task.filename=str(source);task.destination_path=ENV+'/Structures/BoulderHill';task.destination_name='SM_BoulderHill_V6_Open_v2';task.automated=True;task.save=True;task.factory=unreal.FbxFactory()
        options=unreal.FbxImportUI();options.automated_import_should_detect_type=False;options.import_as_skeletal=False;options.import_materials=False;options.import_textures=False;options.import_animations=False
        options.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;options.static_mesh_import_data.set_editor_property('combine_meshes',True);options.static_mesh_import_data.set_editor_property('auto_generate_collision',False);task.options=options
        assets.import_asset_tasks([task])
    if lib.does_asset_exist(boulderpath):
        mesh=lib.load_asset(boulderpath)
        # The detailed opened base requires concave collision: do not cap its doorway with a convex hull.
        body=mesh.get_editor_property('body_setup');body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        manifest=json.loads((source.parent/'manifest_v2.json').read_text(encoding='utf-8'))
        slots=mesh.get_editor_property('static_materials')
        for slot in slots:
            key=str(slot.get_editor_property('material_slot_name'));data=manifest['materials'].get(key)
            if data:slot.set_editor_property('material_interface',material('M_BH_'+key,tuple(data['color'][:3]),data['roughness'],data['metallic']))
        mesh.set_editor_property('static_materials',slots)
        lib.save_loaded_asset(mesh);base=spawn(unreal.StaticMeshActor,'SV_BoulderHill_V6_Opened',(-135000,-110000,8000));base.static_mesh_component.set_static_mesh(mesh);base.static_mesh_component.set_collision_profile_name('BlockAll');report['boulder']='Existing V6, opened static pose'
    else:
        # Explicit temporary geometry only; removed once the source import is available.
        box('SV_GaragePlaceholder_Floor',(-134700,-110600,7950),(2600,3800,100),concrete)
        box('SV_GaragePlaceholder_Left',(-136050,-110600,8350),(100,3800,700),steel)
        box('SV_GaragePlaceholder_Right',(-133350,-110600,8350),(100,3800,700),steel)
        box('SV_GaragePlaceholder_Roof',(-134700,-110600,8700),(2800,3900,100),concrete);report['boulder']='PLACEHOLDER; source export/import pending'
    mark('spawns_and_checkpoints')
    for i,distance in enumerate((0.,1300.,2600.)):
        p=road.route_location(distance);r=road.route_rotation(max(1.,distance));start=spawn(unreal.PlayerStart,'SV_PlayerStart_'+str(i),(p.x,p.y,p.z+80),(0,r.yaw,0));start.set_editor_property('player_start_tag',unreal.Name('SV_Start'+str(i)))
    pois=[('Boulder Hill',(-133300,-108350,8000)),('Pinewood Road',(-75000,-78000,9000)),('Eagle Pass',(70000,25000,15500)),('Old Quarry',(65000,95000,10000)),('North Ridge',(-55000,125000,16000))]
    report['points_of_interest']=[]
    for i,(name,p) in enumerate(pois):
        trigger=spawn(unreal.SilentValleyCheckpoint,'SV_CP_'+str(i),p);trigger.set_editor_property('zone_name',name);trigger.set_editor_property('zone_index',i)
        label(name,(p[0]+1700,p[1]-1700,p[2]+600),-60)
        box('SV_Sign_'+str(i),(p[0]+2000,p[1]-1700,p[2]+600),(40,1000,500),sign)
        report['points_of_interest'].append({'name':name,'position_cm':p})
    # Quarry and ridge turning aprons sit level with the continuous road.
    box('SV_Quarry_Apron',(65000,97000,9947),(13000,12000,100),concrete)
    north=box('SV_NorthRidge_Turnaround',(-55000,125000,15947),(9000,8000,100),concrete)
    mark('lighting')
    sun=spawn(unreal.DirectionalLight,'SV_Sun',(0,0,60000),(-28,-35,0));sun.light_component.set_mobility(unreal.ComponentMobility.MOVABLE);sun.light_component.set_editor_property('intensity',6.);sun.light_component.set_editor_property('atmosphere_sun_light',True)
    sky=spawn(unreal.SkyLight,'SV_Skylight',(0,0,60000));sky.light_component.set_mobility(unreal.ComponentMobility.MOVABLE);sky.light_component.set_editor_property('intensity',1.2);sky.light_component.set_editor_property('real_time_capture',True)
    for i,y in enumerate((-110900,-112600)):
        light=spawn(unreal.PointLight,'SV_GarageLight_'+str(i),(-135000,y,8550));light.light_component.set_mobility(unreal.ComponentMobility.MOVABLE)
        light.light_component.set_editor_property('intensity',1500.);light.light_component.set_editor_property('attenuation_radius',2500.);light.light_component.set_editor_property('cast_shadows',False)
    spawn(unreal.SkyAtmosphere,'SV_Atmosphere',(0,0,0));fog=spawn(unreal.ExponentialHeightFog,'SV_DistanceHaze',(0,0,1000));fog.get_component_by_class(unreal.ExponentialHeightFogComponent).set_editor_property('fog_density',.004)
    gm_path=ENV+'/Structures/BP_SilentValleyGameMode'
    original=unreal.load_asset('/Game/Core/BP_CustomGameMode')
    if not original:raise RuntimeError('Existing GameMode cannot be loaded; do not save an unplayable fallback')
    blueprint=unreal.load_asset(gm_path) if lib.does_asset_exist(gm_path) else assets.duplicate_asset('BP_SilentValleyGameMode',ENV+'/Structures',original)
    if not blueprint:raise RuntimeError('New GameMode duplicate missing')
    if unreal.BlueprintEditorLibrary.get_blueprint_parent_class(blueprint).get_name()!='SilentValleyGameMode':unreal.BlueprintEditorLibrary.reparent_blueprint(blueprint,unreal.SilentValleyGameMode)
    unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
    if not blueprint.generated_class() or unreal.BlueprintEditorLibrary.get_blueprint_parent_class(blueprint).get_name()!='SilentValleyGameMode':raise RuntimeError('GameMode reparent failed')
    lib.save_loaded_asset(blueprint)
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();world.get_world_settings().set_editor_property('default_game_mode',blueprint.generated_class())
    mark('save')
    for path in lib.list_assets(ENV,recursive=True,include_folder=False):
        loaded=lib.load_asset(path)
        if loaded:lib.save_loaded_asset(loaded,False)
    if not levels.save_current_level():raise RuntimeError('Map save failed')
    report['actor_count']=len(actors.get_all_level_actors());report['passed']=True;mark('COMPLETE')
except Exception:
    report['error']=traceback.format_exc();mark('ERROR');unreal.log_error(report['error']);raise
