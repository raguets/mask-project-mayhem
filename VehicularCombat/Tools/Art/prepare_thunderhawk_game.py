"""Run via the installed Blender MCP. Work on a new scene, never save over V14.

Evaluated rigid parts retain their source world geometry and sampled pivot deltas.
Matt's deform weights and both source poses are exported on the SAME skeleton.
"""
import bpy, json, traceback, math
from pathlib import Path
from mathutils import Matrix, Vector

ROOT = Path('G:/DEV/mask-project-mayhem')
OUT = ROOT/'VehicularCombat/SourceArt/MASK/Thunderhawk'
WORK = ROOT/'art_source/GameReady/Thunderhawk'
OUT.mkdir(parents=True, exist_ok=True)
WORK.mkdir(parents=True, exist_ok=True)

def write(name, data):
    (OUT/name).write_text(json.dumps(data, indent=2), encoding='utf-8')

def select(objects):
    bpy.ops.object.select_all(action='DESELECT')
    for ob in objects:
        ob.hide_set(False)
        ob.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]

def join(objects, name):
    select(objects)
    bpy.ops.object.join()
    ob = bpy.context.object
    ob.name = name
    return ob

def export(objects, name, skeletal=False, animations=False):
    select(objects)
    bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')), use_selection=True,
        object_types={'ARMATURE','MESH'} if skeletal else {'MESH'},
        axis_forward='-Y', axis_up='Z', add_leaf_bones=False,
        use_mesh_modifiers=True, bake_anim=animations,
        mesh_smooth_type='FACE',use_tspace=True,
        bake_anim_use_all_actions=animations, bake_anim_use_nla_strips=False,
        bake_anim_simplify_factor=0.0, path_mode='COPY', embed_textures=False)

def unwrap(ob):
    select([ob])
    # Keep source label UVs available to the material while baking into a NEW atlas.
    original=next((uv for uv in ob.data.uv_layers if uv.active_render),None)
    for slot in ob.material_slots:
        mat=slot.material
        if not mat or not mat.use_nodes or not original:continue
        for node in list(mat.node_tree.nodes):
            if node.type=='TEX_IMAGE' and not node.inputs['Vector'].is_linked:
                uv=mat.node_tree.nodes.new('ShaderNodeUVMap');uv.uv_map=original.name
                mat.node_tree.links.new(uv.outputs['UV'],node.inputs['Vector'])
    layer=ob.data.uv_layers.new(name='GameAtlas')
    ob.data.uv_layers.active=layer;layer.active_render=True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(70), island_margin=0.008)
    bpy.ops.object.mode_set(mode='OBJECT')

def triangulate(ob):
    select([ob])
    mod=ob.modifiers.new('GameTriangulation','TRIANGULATE')
    bpy.ops.object.modifier_apply(modifier=mod.name)

def reduce(ob, maximum):
    ob.data.calc_loop_triangles()
    n=len(ob.data.loop_triangles)
    if n > maximum:
        select([ob])
        mod=ob.modifiers.new('GameBudget','DECIMATE')
        mod.ratio=maximum/n
        bpy.ops.object.modifier_apply(modifier=mod.name)

def material_contract(materials):
    result=[]
    for mat in materials:
        if not mat: continue
        p=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if mat.use_nodes else None
        item={'name':mat.name,'base_color':list(mat.diffuse_color),'metallic':0.,'roughness':0.5,'glass':'Glass' in mat.name,
              'linked_inputs':[]}
        if p:
            item.update(base_color=list(p.inputs['Base Color'].default_value),metallic=p.inputs['Metallic'].default_value,
                        roughness=p.inputs['Roughness'].default_value)
            item['linked_inputs']=[s.name for s in p.inputs if s.is_linked]
        for n in mat.node_tree.nodes if mat.use_nodes else []:
            if n.type=='TEX_IMAGE' and n.image:
                # Preserve source label/logo textures in addition to the baked atlas.
                image_path=OUT/(n.image.name.replace('/','_')+'.png')
                n.image.save_render(str(image_path))
                item.setdefault('source_images',[]).append(image_path.name)
        result.append(item)
    return result

def bake_color(ob, name, size):
    """Bake the actual procedural color, without lights, into exported UV0."""
    unwrap(ob)
    image=bpy.data.images.new(name,width=size,height=size,alpha=False)
    image.filepath_raw=str(OUT/(name+'.png')); image.file_format='PNG'
    used=[]
    for slot in ob.material_slots:
        mat=slot.material
        if not mat: continue
        mat.use_nodes=True
        node=mat.node_tree.nodes.new('ShaderNodeTexImage'); node.image=image
        mat.node_tree.nodes.active=node
        p=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
        output=next((n for n in mat.node_tree.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output),None)
        emission=mat.node_tree.nodes.new('ShaderNodeEmission')
        saved=[(l.from_socket,l.to_socket) for l in list(output.inputs['Surface'].links)] if output else []
        if p:
            source=list(p.inputs['Base Color'].links)
            if source:mat.node_tree.links.new(source[0].from_socket,emission.inputs['Color'])
            else:emission.inputs['Color'].default_value=p.inputs['Base Color'].default_value
        if output:mat.node_tree.links.new(emission.outputs[0],output.inputs['Surface'])
        used.append((mat,node,emission,saved))
    scene=bpy.context.scene
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=1
    scene.render.bake.use_pass_direct=False;scene.render.bake.use_pass_indirect=False;scene.render.bake.use_pass_color=True
    scene.render.bake.margin=12
    select([ob])
    # Diffuse baking attenuates metals and makes the silver helmet/rims black.
    bpy.ops.object.bake(type='EMIT')
    image.save()
    for mat,node,emission,saved in used:
        mat.node_tree.nodes.remove(emission)
        for source,target in saved:mat.node_tree.links.new(source,target)
        mat.node_tree.nodes.remove(node)
    # Runtime TextureSample uses UV0. Export only the atlas, not the old label UVs.
    for layer in list(ob.data.uv_layers):
        if layer.name!='GameAtlas':ob.data.uv_layers.remove(layer)
    return image.name

def prepare():
    try:
        if bpy.app.driver_namespace.get('_mask_asset_review_active'):
            raise RuntimeError('A render queue is active')
        bpy.app.driver_namespace['_mask_asset_review_active']=True
        scene=bpy.context.scene
        scene.frame_set(1)
        rig=bpy.data.objects['MattTrakker_Rig']
        # Record articulated rigid-controller delta samples before creating the game scene.
        controllers=[o for o in scene.objects if o.type=='EMPTY' and o.name.startswith('THK_')]
        rest={o.name:o.matrix_world.copy() for o in controllers}
        convert=Matrix.Diagonal((100.,-100.,100.,1.))
        tracks={o.name:[] for o in controllers}
        for frame in range(1,98):
            scene.frame_set(frame)
            for o in controllers:
                loc,q,sc=(convert @ (o.matrix_world @ rest[o.name].inverted()) @ convert.inverted()).decompose()
                tracks[o.name].append({'t':list(loc),'q':[q.x,q.y,q.z,q.w],'s':list(sc)})
        scene.frame_set(1)
        pose_samples={}
        # Remove only the assembly-level driving_pose driver; preserve driven bones while sampling.
        try:rig.driver_remove('["driving_pose"]')
        except (TypeError,RuntimeError):pass
        for name,value in [('Standing',0.),('Driving',1.)]:
            rig['driving_pose']=value;rig['mask_on']=False
            rig.update_tag(refresh={'OBJECT','DATA','TIME'});scene.frame_set(1);bpy.context.view_layer.update()
            evaluated_rig=rig.evaluated_get(bpy.context.evaluated_depsgraph_get())
            pose_samples[name]={b.name:b.matrix_basis.copy() for b in evaluated_rig.pose.bones}
        rig['driving_pose']=0.;rig['mask_on']=False;bpy.context.view_layer.update()
        rig_world=rig.matrix_world.copy()
        vehicle=[o for o in scene.objects if o.type=='MESH' and any(c.name in ('THK9_Exterior','THK11_Interior') for c in o.users_collection) and not o.hide_render]
        body=[o for o in scene.objects if o.type=='MESH' and any(c.name=='MT11_Character' for c in o.users_collection)
              and (not o.hide_render or o.name.startswith('MT_Hair_'))]
        masks=[o for o in scene.objects if o.type=='MESH' and any(c.name=='Spectrum11_Asset' for c in o.users_collection)]
        mats={s.material for o in vehicle+body+masks for s in o.material_slots if s.material}
        material_data=material_contract(sorted(mats,key=lambda m:m.name))
        # Independent working scene, evaluated copies; references and obsolete sources are excluded.
        game=bpy.data.scenes.new('Thunderhawk_GameReady');bpy.context.window.scene=game
        newrig=rig.copy();newrig.data=rig.data.copy();game.collection.objects.link(newrig)
        newrig.name='Matt_GameRig';newrig.animation_data_clear();newrig.matrix_world=Matrix.Identity(4)
        for b in newrig.pose.bones:
            b.matrix_basis=Matrix.Identity(4)
            for c in list(b.constraints):b.constraints.remove(c)
        newrig.data.pose_position='REST'
        generated=[];parts=[];character_parts={};bake_jobs=[];material_copies={}
        # Temporarily make original rig REST while baking undeformed weighted geometry.
        rig.data.pose_position='REST';bpy.context.window.scene=scene;bpy.context.view_layer.update()
        deps=bpy.context.evaluated_depsgraph_get()
        def copy_mesh(o,name,character=False):
            # Disable subdivisions for game copies; weights remain on the base cage.
            states=[(m,m.show_viewport) for m in o.modifiers]
            for m,_ in states:
                if m.type in ('SUBSURF','ARMATURE'):m.show_viewport=False
            bpy.context.view_layer.update()
            ev=o.evaluated_get(deps)
            me=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=deps)
            for m,state in states:m.show_viewport=state
            transform=rig_world.inverted() @ o.matrix_world if character else o.matrix_world
            me.transform(transform)
            obj=bpy.data.objects.new(name,me);game.collection.objects.link(obj)
            for group in o.vertex_groups:obj.vertex_groups.new(name=group.name)
            # Deep copies avoid modifying source materials during atlas baking.
            for index,mat in enumerate(me.materials):
                if mat:
                    if mat.name not in material_copies:
                        material_copies[mat.name]=mat.copy()
                        material_copies[mat.name].name='M_Game_'+mat.name.split('.')[0]
                    me.materials[index]=material_copies[mat.name]
            generated.append(obj)
            return obj
        grouped={}
        for o in vehicle:
            parent=o.parent
            while parent and parent.name not in rest:parent=parent.parent
            control=parent.name if parent else 'THK_Root'
            glass=any(s.material and 'Glass' in s.material.name for s in o.material_slots)
            key=control+('_Glass' if glass else '')
            grouped.setdefault(key,[]).append(copy_mesh(o,o.name+'_Game'))
        for key,objects in grouped.items():
            bpy.context.window.scene=game
            ob=join(objects,key.replace('THK_','SM_THK_'))
            reduce(ob,50000 if key=='THK_Root' else 16000)
            triangulate(ob)
            if not key.endswith('_Glass'):bake_jobs.append((ob,ob.name+'_BaseColor',2048 if key=='THK_Root' else 1024))
            else:unwrap(ob)
            parts.append({'name':ob.name,'control':key.removesuffix('_Glass'),'glass':key.endswith('_Glass'),
                          'wheel':key.split('_')[-1] if 'WheelPivot' in key else '', 'samples':tracks[key.removesuffix('_Glass')]})
        bpy.context.window.scene=scene
        for name,objects in [('MattBody',[o for o in body if 'Hair' not in o.name]),('MattHair',[o for o in body if 'Hair' in o.name]),('Spectrum',masks)]:
            copies=[copy_mesh(o,o.name+'_Game',True) for o in objects]
            bpy.context.window.scene=game
            for ob in copies:
                if not len(ob.vertex_groups):
                    ob.vertex_groups.new(name='head').add(list(range(len(ob.data.vertices))),1.,'REPLACE')
                reduce(ob,30000 if 'ContinuousFlightSuit' in ob.name else 14000 if 'DenseGroom' in ob.name else 22000)
            ob=join(copies,name);triangulate(ob)
            mod=ob.modifiers.new('SameMattSkeleton','ARMATURE');mod.object=newrig
            ob.parent=newrig;character_parts[name]=ob
            bake_jobs.append((ob,name+'_BaseColor',2048 if name=='MattBody' else 1024))
            bpy.context.window.scene=scene
        bpy.context.window.scene=game
        # Bone animations are baked from the existing driver's two poses, not new mannequins.
        newrig.data.pose_position='POSE'
        for name,sample in pose_samples.items():
            action=bpy.data.actions.new('Matt_'+name);action.use_fake_user=True;newrig.animation_data_create();newrig.animation_data.action=action
            for frame in (1,25):
                for bone_name,matrix in sample.items():
                    b=newrig.pose.bones[bone_name];b.rotation_mode='QUATERNION';b.matrix_basis=matrix
                    for prop in ('location','rotation_quaternion','scale'):b.keyframe_insert(data_path=prop,frame=frame,group=bone_name)
        scene.frame_set(1)
        game.frame_start=1;game.frame_end=25
        write('progress.json',{'stage':'atlas_baking','jobs':[n for _,n,_ in bake_jobs]})
        # Disable armature during texture baking to retain the exported rest UV charts.
        newrig.data.pose_position='REST'
        for ob,name,size in bake_jobs:
            write('progress.json',{'stage':'atlas_baking','current':name})
            bake_color(ob,name,size)
        write('progress.json',{'stage':'exporting'})
        export([bpy.data.objects[p['name']] for p in parts],'Thunderhawk_Visual')
        # Export only the three joined weighted meshes, with a common bind skeleton.
        for name,ob in character_parts.items():
            newrig.data.pose_position='POSE'
            export([newrig,ob],name,True,name=='MattBody')
        # Purpose-built Chaos physics chassis: five bones, no old car geometry/collision.
        arm=bpy.data.armatures.new('THK_PhysicsSkeleton');chassis=bpy.data.objects.new('THK_PhysicsRig',arm);game.collection.objects.link(chassis)
        select([chassis]);bpy.ops.object.mode_set(mode='EDIT')
        root=arm.edit_bones.new('root');root.head=(0,0,0);root.tail=(0,0,.25)
        for label,x,y in [('FL',1.40,.818),('FR',1.40,-.818),('RL',-1.42,.818),('RR',-1.42,-.818)]:
            b=arm.edit_bones.new('wheel_'+label);b.head=(x,y,.328);b.tail=(x,y,.528);b.parent=root
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,.61));proxy=bpy.context.object;proxy.name='THK_PhysicsChassis'
        proxy.dimensions=(4.35,1.72,.58);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
        proxy.vertex_groups.new(name='root').add(list(range(len(proxy.data.vertices))),1.,'REPLACE')
        mod=proxy.modifiers.new('ChassisSkin','ARMATURE');mod.object=chassis;proxy.parent=chassis;unwrap(proxy)
        export([chassis,proxy],'Thunderhawk_Physics',True)
        write('manifest.json',{'source':'Thunderhawk_V14 / MattTrakker_V5 / Spectrum_V4','fps':24,'duration':4.,
            'coordinate_conversion':'Blender(X,Y,Z)m -> UE(X,-Y,Z)cm','parts':parts,'materials':material_data,
            'driver_location_cm':[rig_world.translation.x*100,-rig_world.translation.y*100,rig_world.translation.z*100],
            'wheel_radius_cm':32.8,'wheel_centers_cm':[[140,-81.8,32.8],[140,81.8,32.8],[-142,-81.8,32.8],[-142,81.8,32.8]],
            'pose_source':'Same 17-bone source rig, sampled driven standing/driving poses',
            'limitations':['Source dimensions and physics envelope estimated','LOD silhouette and texture fidelity require Unreal render review']})
        bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'Thunderhawk_GameReady.blend'))
        write('progress.json',{'stage':'COMPLETE','blend':bpy.data.filepath})
        bpy.ops.wm.open_mainfile(filepath=str(ROOT/'art_source/Thunderhawk/Thunderhawk_V14.blend'))
    except Exception:
        write('ERROR.json',{'traceback':traceback.format_exc()})
        print(traceback.format_exc())
    finally:
        bpy.app.driver_namespace.pop('_mask_asset_review_active',None)
    return None

def run():
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'art_source/Thunderhawk/Thunderhawk_V14.blend'))
    # MCP and timer callbacks have no implicit UI window. Use the existing app window.
    with bpy.context.temp_override(window=bpy.context.window_manager.windows[0]):
        prepare()
    return None

if not bpy.app.driver_namespace.get('_mask_asset_review_active'):
    bpy.app.timers.register(run,first_interval=1.0)
    print('GAME_PREPARATION_QUEUED')
else:
    raise RuntimeError('Existing preparation/render queue is active')
