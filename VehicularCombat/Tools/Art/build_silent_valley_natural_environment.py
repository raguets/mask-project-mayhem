"""Natural terrain, lake surface and atmosphere in the isolated saved map.
Colorado photo inspected; layout/dimensions are an authorised interpretation.
No external source asset, vehicle, mission or road mesh is overwritten.
"""
import unreal,json,math,shutil,datetime,traceback
from pathlib import Path
ROOT=Path(unreal.Paths.project_dir());OUT=ROOT/'Saved/SilentValley/environment-v1';OUT.mkdir(parents=True,exist_ok=True)
FOLDER='/Game/MASK/Environment/SilentValley/Materials';MAP='/Game/MASK/Maps/SilentValley/L_SilentValley_Blockout'
LAKE=unreal.Vector(-105000,-55000,5400);RADII=unreal.Vector2D(14000,9000)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);editor=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
lib=unreal.EditorAssetLibrary;edit=unreal.MaterialEditingLibrary;assets=unreal.AssetToolsHelpers.get_asset_tools()
registry=unreal.AssetRegistryHelpers.get_asset_registry();registry.search_all_assets(True)
registry.scan_paths_synchronous(['/Game/Fab','/Game/MASK'],True,True)
report={'passed':False,'stage':'start','interpretation':'Colorado photo reference; estimated lake 280 x 180 m, depth up to 6.5 m. Visual water only; no swimming/buoyancy implemented.'}
def record(stage):
    report['stage']=stage;(OUT/'environment.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
def find(label):return next((a for a in editor.get_all_level_actors() if a.get_actor_label()==label),None)
def owned(actor):
    if not actor or unreal.Name('SV_GENERATED') not in actor.tags:raise RuntimeError('Unowned actor')
    return actor
def spawn(cls,label,p):
    a=find(label)
    if a:owned(a)
    else:
        a=editor.spawn_actor_from_class(cls,p);a.set_actor_label(label);a.tags=[unreal.Name('SV_GENERATED'),unreal.Name('SV_ENVIRONMENT_V1')]
    a.set_actor_location(p,False,True);return a
def ground(p,ignore):
    hits=unreal.SystemLibrary.line_trace_multi(world,unreal.Vector(p.x,p.y,100000),unreal.Vector(p.x,p.y,-100000),unreal.TraceTypeQuery.ECC_VISIBILITY,False,ignore,unreal.DrawDebugTrace.NONE,True)
    return next((h.to_tuple()[5] for h in hits if isinstance(h.to_tuple()[9],unreal.LandscapeProxy)),None)
def shader(name,build):
    path=FOLDER+'/'+name;mat=lib.load_asset(path)
    if mat:return mat
    mat=assets.create_asset(name,FOLDER,unreal.Material,unreal.MaterialFactoryNew())
    def node(cls,**props):
        n=edit.create_material_expression(mat,cls)
        for k,v in props.items():n.set_editor_property(k,v)
        return n
    def link(a,b,pin):
        names=[str(x) for x in edit.get_material_expression_input_names(b)]
        if pin not in names and len(names)==1:pin='' if names[0]=='None' else names[0]
        else:pin=next((x for x in names if x.replace(' ','').lower()==pin.replace(' ','').lower()),pin)
        if not edit.connect_material_expressions(a,'',b,pin):raise RuntimeError('Material pin '+pin+' '+str(names))
    def scalar(v):return node(unreal.MaterialExpressionConstant,r=v)
    def color(v):return node(unreal.MaterialExpressionConstant3Vector,constant=unreal.LinearColor(*v,1))
    def binary(cls,a,b):
        n=node(cls);link(a,n,'A');link(b,n,'B');return n
    def lerp(a,b,t):
        n=node(unreal.MaterialExpressionLinearInterpolate);link(a,n,'A');link(b,n,'B');link(t,n,'Alpha');return n
    def unary(cls,a):
        n=node(cls);link(a,n,'Input');return n
    def mask(a,r=False,g=False,b=False):
        n=node(unreal.MaterialExpressionComponentMask,r=r,g=g,b=b,a=False);link(a,n,'Input');return n
    def prop(a,p):
        if not edit.connect_material_property(a,'',p):raise RuntimeError('Material property '+str(p))
    build(mat,node,link,scalar,color,binary,lerp,unary,mask,prop)
    edit.recompile_material(mat)
    if not lib.save_loaded_asset(mat,False):raise RuntimeError('Material save failed')
    return mat
try:
    backup=ROOT/'Saved/SilentValley/backups';backup.mkdir(exist_ok=True)
    shutil.copy2(ROOT/'Content/MASK/Maps/SilentValley/L_SilentValley_Blockout.umap',backup/('BeforeNaturalEnvironment-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.umap'))
    if not levels.load_level(MAP):raise RuntimeError('Map load failed')
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    road=next(a for a in editor.get_all_level_actors() if isinstance(a,unreal.SilentValleyRoad));landscape=owned(next(a for a in editor.get_all_level_actors() if isinstance(a,unreal.Landscape)))
    probes=[]
    for d in range(5000,int(road.route_length_cm()),5000):
        p=road.route_location(d);yaw=math.radians(road.route_rotation(d).yaw)
        for side in (-1,1):
            q=p+unreal.Vector(-math.sin(yaw)*3000*side,math.cos(yaw)*3000*side,0)
            hit=ground(q,[road])
            if hit:probes.append((q,hit.z))
    record('terrain')
    report['terrain_changed_samples']=unreal.SilentValleyEditorLibrary.refine_natural_landscape(road,LAKE,RADII,LAKE.z)
    if report['terrain_changed_samples']<0:raise RuntimeError('Terrain compatibility rejected')
    deviations=[]
    for p,z in probes:
        hit=ground(p,[road])
        if not hit:raise RuntimeError('Protected terrain probe disappeared')
        deviations.append(abs(hit.z-z))
    report['protected_corridor_probes']=len(probes);report['max_protected_height_delta_cm']=max(deviations,default=0)
    # Rebuilding Chaos heightfield collision changes interpolated query results
    # by a few mm, below the Landscape's 3.125 cm height quantisation. Native
    # code retains the source height samples throughout the protected corridor.
    if not probes or max(deviations)>1.:raise RuntimeError('Protected corridor changed beyond 1 cm query tolerance')
    if not levels.save_current_level():raise RuntimeError('Terrain checkpoint save failed')
    record('terrain_material')
    def terrain_shader(mat,node,link,s,c,op,lerp,unary,mask,prop):
        pos=node(unreal.MaterialExpressionWorldPosition)
        def noise(scale):
            n=node(unreal.MaterialExpressionNoise,scale=scale,quality=1,levels=1,output_min=0.,output_max=1.);link(pos,n,'World Position');return n
        mul=lambda a,b:op(unreal.MaterialExpressionMultiply,a,b)
        sub=lambda a,b:op(unreal.MaterialExpressionSubtract,a,b)
        add=lambda a,b:op(unreal.MaterialExpressionAdd,a,b)
        macro=noise(.00045);grain=noise(.09)
        meadow=mul(lerp(c((.105,.115,.046)),c((.20,.155,.075)),macro),lerp(s(.86),s(1.12),grain))
        normal=mask(node(unreal.MaterialExpressionVertexNormalWS),b=True)
        slope=unary(unreal.MaterialExpressionSaturate,mul(sub(s(.94),normal),s(4)))
        uv=mul(mask(pos,r=True,g=True),s(.0025))
        tex='/Game/Fab/Megascans/3D/Small_Beach_Rock_wd4kfdx/Medium/wd4kfdx_tier_2/Textures/'
        rock=node(unreal.MaterialExpressionTextureSample,texture=lib.load_asset(tex+'T_wd4kfdx_2K_B'));link(uv,rock,'UVs')
        rockcolor=mul(rock,c((.65,.63,.57)))
        surface=lerp(meadow,rockcolor,slope)
        delta=sub(pos,c((LAKE.x,LAKE.y,LAKE.z)))
        rx=mul(mask(delta,r=True),s(1/RADII.x));ry=mul(mask(delta,g=True),s(1/RADII.y))
        radius2=add(mul(rx,rx),mul(ry,ry))
        shore=mul(unary(unreal.MaterialExpressionSaturate,sub(s(2.2),radius2)),unary(unreal.MaterialExpressionSaturate,sub(s(1),mul(unary(unreal.MaterialExpressionAbs,mask(delta,b=True)),s(1/350)))))
        surface=lerp(surface,mul(rockcolor,s(.55)),shore)
        prop(surface,unreal.MaterialProperty.MP_BASE_COLOR)
        n=node(unreal.MaterialExpressionTextureSample,texture=lib.load_asset(tex+'T_wd4kfdx_2K_N'),sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL);link(uv,n,'UVs')
        prop(unary(unreal.MaterialExpressionNormalize,lerp(c((0,0,1)),n,lerp(s(.22),s(.8),slope))),unreal.MaterialProperty.MP_NORMAL)
        prop(lerp(s(.94),s(.65),shore),unreal.MaterialProperty.MP_ROUGHNESS)
    terrainmat=shader('M_SV_NaturalTerrain_v1',terrain_shader);landscape.set_editor_property('landscape_material',terrainmat)
    record('lake')
    def water_shader(mat,node,link,s,c,op,lerp,unary,mask,prop):
        water_model=next(getattr(unreal.MaterialShadingModel,n) for n in dir(unreal.MaterialShadingModel) if 'WATER' in n)
        mat.set_editor_property('shading_model',water_model)
        mat.set_editor_property('blend_mode',unreal.BlendMode.BLEND_MASKED)
        pos=node(unreal.MaterialExpressionWorldPosition);time=node(unreal.MaterialExpressionTime)
        mul=lambda a,b:op(unreal.MaterialExpressionMultiply,a,b)
        add=lambda a,b:op(unreal.MaterialExpressionAdd,a,b)
        sub=lambda a,b:op(unreal.MaterialExpressionSubtract,a,b)
        x=mask(pos,r=True);y=mask(pos,g=True)
        a=unary(unreal.MaterialExpressionSine,add(mul(x,s(.006)),mul(time,s(.15))))
        b=unary(unreal.MaterialExpressionSine,sub(mul(add(x,y),s(.011)),mul(time,s(.11))))
        nx=mul(add(a,mul(b,s(.5))),s(.055))
        ny=mul(unary(unreal.MaterialExpressionCosine,add(mul(y,s(.008)),mul(time,s(.12)))),s(.05))
        normal=unary(unreal.MaterialExpressionNormalize,op(unreal.MaterialExpressionAppendVector,op(unreal.MaterialExpressionAppendVector,nx,ny),s(1)))
        prop(normal,unreal.MaterialProperty.MP_NORMAL);prop(c((.006,.024,.032)),unreal.MaterialProperty.MP_BASE_COLOR)
        prop(s(.14),unreal.MaterialProperty.MP_ROUGHNESS);prop(s(.5),unreal.MaterialProperty.MP_SPECULAR);prop(s(.2),unreal.MaterialProperty.MP_OPACITY)
        dx=mul(sub(x,s(LAKE.x)),s(1/RADII.x));dy=mul(sub(y,s(LAKE.y)),s(1/RADII.y))
        radius=add(mul(dx,dx),mul(dy,dy));edge=node(unreal.MaterialExpressionIf)
        link(radius,edge,'A');link(s(1.69),edge,'B');link(s(1),edge,'A < B');link(s(0),edge,'A > B');link(s(1),edge,'A == B')
        prop(edge,unreal.MaterialProperty.MP_OPACITY_MASK)
        output=node(unreal.MaterialExpressionSingleLayerWaterMaterialOutput)
        link(c((.0014,.0035,.0042)),output,'Scattering Coefficients');link(c((.008,.003,.0012)),output,'Absorption Coefficients')
        link(s(.25),output,'PhaseG');link(c((1,1,1)),output,'Color Scale Behind Water')
    watermat=shader('M_SV_LakeWater_v1',water_shader)
    lake=spawn(unreal.StaticMeshActor,'SV_Lake_Surface_v1',LAKE);lake.static_mesh_component.set_static_mesh(lib.load_asset('/Engine/BasicShapes/Plane'))
    lake.static_mesh_component.set_material(0,watermat);lake.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION);lake.set_actor_scale3d(unreal.Vector(420,300,1))
    record('atmosphere')
    clouds=spawn(unreal.VolumetricCloud,'SV_VolumetricClouds',unreal.Vector(0,0,0)).get_component_by_class(unreal.VolumetricCloudComponent)
    clouds.set_editor_property('layer_bottom_altitude',2.2);clouds.set_editor_property('layer_height',2.8);clouds.set_editor_property('view_sample_count_scale',.65)
    cloudmat=lib.load_asset(FOLDER+'/MI_SV_Clouds_v1') or lib.duplicate_asset('/Engine/EngineSky/VolumetricClouds/m_SimpleVolumetricCloud_Inst',FOLDER+'/MI_SV_Clouds_v1')
    if not cloudmat:raise RuntimeError('Default cloud material unavailable')
    clouds.set_material(cloudmat);lib.save_loaded_asset(cloudmat,False)
    sun=owned(find('SV_Sun')).light_component;sun.set_editor_property('intensity',6.5);sun.set_editor_property('use_temperature',True);sun.set_editor_property('temperature',5700.)
    sun.set_editor_property('light_source_angle',.7);sun.set_editor_property('cast_cloud_shadows',True)
    owned(find('SV_Skylight')).light_component.set_editor_property('intensity',1.4)
    owned(find('SV_AmbientFill')).light_component.set_editor_property('intensity',.45)
    fog=owned(find('SV_DistanceHaze')).get_component_by_class(unreal.ExponentialHeightFogComponent)
    fog.set_editor_property('fog_density',.003);fog.set_editor_property('fog_height_falloff',.08);fog.set_editor_property('start_distance',16000.);fog.set_editor_property('enable_volumetric_fog',True)
    report['lake_center_cm']=[LAKE.x,LAKE.y,LAKE.z];report['lake_radii_cm']=[RADII.x,RADII.y];report['route_m']=road.route_length_cm()/100
    report['terrain_material']=terrainmat.get_path_name();report['water_material']=watermat.get_path_name();report['cloud_material']=cloudmat.get_path_name()
    if not levels.save_current_level():raise RuntimeError('Environment save failed')
    report['passed']=True;record('saved_visual_inspection_pending')
except Exception:
    report['error']=traceback.format_exc();record('error');raise
