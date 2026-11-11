"""Installed Blender MCP: Hurricane V7, one Hondo rig, sampled gunner transition."""
import bpy,json,math,traceback
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path('G:/DEV/mask-project-mayhem');PROJECT=ROOT/'VehicularCombat'
OUT=PROJECT/'SourceArt/MASK/Hurricane';WORK=ROOT/'art_source/GameReady/Hurricane'
OUT.mkdir(parents=True,exist_ok=True);WORK.mkdir(parents=True,exist_ok=True)
exec((PROJECT/'Tools/Art/blender_game_export_helpers.py').read_text(encoding='utf-8-sig'))

def prepare():
    try:
        source=bpy.context.scene;source.frame_set(1);control=bpy.data.objects['Hurricane_Control'];control.animation_data.action=None
        control['battle_mode']=0.;control['spare_eject']=0.;control.update_tag();bpy.context.view_layer.update()
        rig=bpy.data.objects['HondoMacLean_Rig'];rig['mask_on']=True;rig.update_tag()
        vehicles=[o for o in source.objects if o.type=='MESH' and any(c.name in ('HU_Body','HU_Interior','HU_RunningGear','HU_Weapons') for c in o.users_collection) and not o.hide_render]
        body=[o for o in source.objects if o.type=='MESH' and any(c.name=='HMC_Character' for c in o.users_collection)]
        masks=[o for o in source.objects if o.type=='MESH' and any(c.name=='HMC_Mask' for c in o.users_collection)]
        for ob in vehicles+body+masks:
            try:ob.driver_remove('hide_viewport')
            except (TypeError,RuntimeError):pass
            ob.hide_viewport=False;ob.hide_set(False);ob.update_tag()
        bpy.context.view_layer.update();write('progress.json',{'stage':'sampling'})
        controllers=[o for o in source.objects if o.type=='EMPTY'];rest={o.name:o.matrix_world.copy() for o in controllers}
        C=Matrix.Diagonal((100.,-100.,100.,1.));tracks={o.name:[] for o in controllers};bone_frames=[];driver_tracks=[]
        wheels=[]
        for ob in vehicles:
            if ob.name.endswith('_Tire'):
                p=sum((ob.matrix_world @ Vector(c) for c in ob.bound_box),Vector())/8
                wheels.append({'prefix':ob.name[:-5],'label':'W'+str(len(wheels)),'middle':'CentreWheel' in ob.name,
                    'road_position_cm':[p.x*100,-p.y*100,p.z*100],'radius_cm':ob.dimensions.z*50,'object':ob.name})
        for i in range(97):
            control['battle_mode']=i/96.;control.update_tag();rig.update_tag(refresh={'OBJECT','DATA','TIME'});bpy.context.view_layer.update()
            for ob in controllers:
                t,q,s=(C @ ob.matrix_world @ rest[ob.name].inverted() @ C.inverted()).decompose();tracks[ob.name].append({'t':list(t),'q':[q.x,q.y,q.z,q.w],'s':list(s)})
            ev=rig.evaluated_get(bpy.context.evaluated_depsgraph_get());bone_frames.append({b.name:b.matrix_basis.copy() for b in ev.pose.bones})
            t,q,s=(C @ ev.matrix_world @ C.inverted()).decompose();driver_tracks.append({'t':list(t),'q':[q.x,q.y,q.z,q.w],'s':list(s)})
        for w in wheels:
            ob=bpy.data.objects[w['object']];p=sum((ob.matrix_world @ Vector(c) for c in ob.bound_box),Vector())/8
            w['position_cm']=[p.x*100,-p.y*100,p.z*100]
        control['battle_mode']=0.;control.update_tag();bpy.context.view_layer.update()
        for key in ('driving_pose','gunner_pose','vehicle_lift'):
            try:rig.driver_remove('["'+key+'"]')
            except (TypeError,RuntimeError):pass
        rig['in_vehicle']=0.;rig['driving_pose']=0.;rig['gunner_pose']=0.;rig['vehicle_lift']=0.;rig.update_tag(refresh={'OBJECT','DATA','TIME'});bpy.context.view_layer.update()
        standing={b.name:b.matrix_basis.copy() for b in rig.evaluated_get(bpy.context.evaluated_depsgraph_get()).pose.bones}
        rig.data.pose_position='REST';bpy.context.view_layer.update();rig_world=rig.matrix_world.copy()
        materials=material_contract(sorted({s.material for o in vehicles+body+masks for s in o.material_slots if s.material},key=lambda m:m.name))
        game=bpy.data.scenes.new('Hurricane_GameReady');game.render.fps=24;material_copies={};jobs=[];parts=[];generated={}
        deps=bpy.context.evaluated_depsgraph_get()
        def copy_mesh(o,character=False):
            states=[(m,m.show_viewport) for m in o.modifiers]
            for m,_ in states:
                if m.type in ('SUBSURF','ARMATURE'):m.show_viewport=False
            bpy.context.view_layer.update();mesh=bpy.data.meshes.new_from_object(o.evaluated_get(deps),preserve_all_data_layers=True,depsgraph=deps)
            for m,v in states:m.show_viewport=v
            mesh.transform(rig_world.inverted() @ o.matrix_world if character else o.matrix_world)
            ob=bpy.data.objects.new(o.name+'_Game',mesh);game.collection.objects.link(ob)
            for group in o.vertex_groups:ob.vertex_groups.new(name=group.name)
            if character and not len(ob.vertex_groups):ob.vertex_groups.new(name='head').add(list(range(len(mesh.vertices))),1.,'REPLACE')
            for index,mat in enumerate(mesh.materials):
                if mat:
                    if mat.name not in material_copies:
                        material_copies[mat.name]=mat.copy();material_copies[mat.name].name='M_Game_'+mat.name.split('.')[0]
                    mesh.materials[index]=material_copies[mat.name]
            return ob
        groups={}
        for ob in vehicles:
            parent=ob.parent
            while parent and parent.name not in rest:parent=parent.parent
            owner=parent.name if parent else 'Hurricane_Control';wheel=next((w for w in wheels if ob.name.startswith(w['prefix']+'_')),None)
            glass=any(s.material and 'Glass' in s.material.name for s in ob.material_slots)
            key='SM_HU_'+wheel['label'] if wheel else 'SM_'+owner+('_Glass' if glass else '')
            groups.setdefault(key,{'objects':[],'control':owner,'wheel':wheel['label'] if wheel else '','glass':glass})['objects'].append(copy_mesh(ob))
        bpy.context.window.scene=game
        for name,group in groups.items():
            ob=join(group['objects'],name);reduce(ob,70000 if group['control']=='HU_UpperChassisLift' else 30000 if group['control']=='Hurricane_Control' else 12000);triangulate(ob)
            if not group['glass']:jobs.append((ob,name+'_BaseColor',2048 if group['control']=='HU_UpperChassisLift' else 1024))
            else:unwrap(ob)
            parts.append({'name':name,'control':group['control'],'wheel':group['wheel'],'glass':group['glass'],'samples':tracks[group['control']]})
        newrig=rig.copy();newrig.data=rig.data.copy();game.collection.objects.link(newrig);newrig.name='Hondo_GameRig';newrig.animation_data_clear();newrig.matrix_world=Matrix.Identity(4);newrig.data.pose_position='REST'
        for b in newrig.pose.bones:
            b.matrix_basis=Matrix.Identity(4)
            for c in list(b.constraints):b.constraints.remove(c)
        for kind,objects in [('Body',[o for o in body if 'Hair' not in o.name]),('Hair',[o for o in body if 'Hair' in o.name]),('Mask',masks)]:
            if not objects:continue
            bpy.context.window.scene=source;copies=[]
            for ob in objects:
                item=copy_mesh(ob,True);bpy.context.window.scene=game;reduce(item,28000 if 'ContinuousFlightSuit' in ob.name else 12000);copies.append(item);bpy.context.window.scene=source
            bpy.context.window.scene=game;ob=join(copies,'Hondo'+kind);triangulate(ob);mod=ob.modifiers.new('SameHondoSkeleton','ARMATURE');mod.object=newrig;ob.parent=newrig;generated[kind]=ob;jobs.append((ob,ob.name+'_BaseColor',2048 if kind=='Body' else 1024))
        for label,frames in [('Standing',[standing,standing]),('Driving',[bone_frames[0],bone_frames[0]]),('Transform',bone_frames)]:
            action=bpy.data.actions.new('Hondo_'+label);action.use_fake_user=True;newrig.animation_data_create();newrig.animation_data.action=action
            for index,sample in enumerate(frames):
                frame=(1 if index==0 else 25) if label!='Transform' else index+1
                for name,matrix in sample.items():
                    b=newrig.pose.bones[name];b.rotation_mode='QUATERNION';b.matrix_basis=matrix
                    for prop in ('location','rotation_quaternion','scale'):b.keyframe_insert(data_path=prop,frame=frame,group=name)
        for ob,name,size in jobs:write('progress.json',{'stage':'baking','current':name});bake_color(ob,name,size)
        export([bpy.data.objects[p['name']] for p in parts],'Hurricane_Visual')
        arm=bpy.data.armatures.new('HU_PhysicsSkeleton');physics=bpy.data.objects.new('HU_PhysicsRig',arm);game.collection.objects.link(physics)
        select([physics]);bpy.ops.object.mode_set(mode='EDIT');root=arm.edit_bones.new('root');root.head=(0,0,0);root.tail=(0,0,.25)
        for w in wheels:
            p=w['position_cm'];b=arm.edit_bones.new('wheel_'+w['label']);b.head=(p[0]/100,-p[1]/100,p[2]/100);b.tail=b.head+Vector((0,0,.25));b.parent=root
        bpy.ops.object.mode_set(mode='OBJECT')
        verts=[(x*2.55,y*.9,.72+z*.36) for x,y,z in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
        mesh=bpy.data.meshes.new('HU_PhysicsMesh');mesh.from_pydata(verts,[],[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]);mesh.update();mesh.uv_layers.new(name='GameAtlas')
        proxy=bpy.data.objects.new('HU_PhysicsChassis',mesh);game.collection.objects.link(proxy);proxy.vertex_groups.new(name='root').add(list(range(8)),1.,'REPLACE');mod=proxy.modifiers.new('PhysicsSkin','ARMATURE');mod.object=physics;proxy.parent=physics;proxy.hide_render=True;proxy.display_type='WIRE';proxy.hide_set(True);physics.hide_set(True)
        manifest={'source':'Hurricane_V7_Assembly / HondoMacLean_V1','fps':24,'duration':5.,'parts':parts,'materials':materials,'wheels':wheels,'driver_tracks':driver_tracks,'driver_location_cm':driver_tracks[0]['t'],'pose_source':'Same Hondo rig, 97 evaluated driven transformation poses; independent standing/driving clips','spare_control':'HU_SpareEjection','coordinate_conversion':'Blender (X,Y,Z)m -> Unreal (X,-Y,Z)cm'}
        write('manifest.json',manifest);game.frame_start=1;game.frame_end=97;bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'Hurricane_GameReady.blend'))
        game.unit_settings.scale_length=.01;scale=Matrix.Diagonal((100.,100.,100.,1.))
        def cm_rig(source):
            ob=source.copy();ob.data=source.data.copy();game.collection.objects.link(ob);ob.name=source.name+'_CM';ob.animation_data_clear();ob.data.transform(scale);ob.matrix_world=Matrix.Identity(4);ob.hide_set(False);ob.data.pose_position='REST'
            for b in ob.pose.bones:b.matrix_basis=Matrix.Identity(4)
            return ob
        def cm_mesh(source,rig):
            ob=source.copy();ob.data=source.data.copy();game.collection.objects.link(ob);ob.data.transform(scale);ob.parent=rig;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_world=Matrix.Identity(4);ob.hide_set(False)
            for m in ob.modifiers:
                if m.type=='ARMATURE':m.object=rig
            return ob
        def cm_export(objects,name,animation=False):
            select(objects);bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',add_leaf_bones=False,bake_anim=animation,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0.,mesh_smooth_type='FACE',use_tspace=True)
        r=cm_rig(newrig)
        for kind,ob in generated.items():cm_export([r,cm_mesh(ob,r)],'Hondo'+kind)
        r.data.pose_position='POSE'
        for label,frames in [('Standing',[standing,standing]),('Driving',[bone_frames[0],bone_frames[0]]),('Transform',bone_frames)]:
            action=bpy.data.actions.new('Hondo_CM_'+label);r.animation_data_create();r.animation_data.action=action;game.frame_end=97 if label=='Transform' else 25
            for index,sample in enumerate(frames):
                frame=(1 if index==0 else 25) if label!='Transform' else index+1
                for name,matrix in sample.items():
                    m=matrix.copy();m.translation*=100;b=r.pose.bones[name];b.rotation_mode='QUATERNION';b.matrix_basis=m
                    for prop in ('location','rotation_quaternion','scale'):b.keyframe_insert(data_path=prop,frame=frame,group=name)
            game.frame_set(1);bpy.context.view_layer.update();cm_export([r],'Hondo_'+label,True)
        r=cm_rig(physics);cm_export([r,cm_mesh(proxy,r)],'Hurricane_Physics');write('progress.json',{'stage':'COMPLETE','parts':len(parts),'tires':len(wheels),'one_hondo':True})
        bpy.ops.wm.open_mainfile(filepath=str(ROOT/'art_source/Hurricane/Hurricane_V7_Assembly.blend'))
    except Exception:write('ERROR.json',{'error':traceback.format_exc()});print(traceback.format_exc())
    finally:bpy.app.driver_namespace.pop('_mask_asset_review_active',None)
    return None
def run():
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'art_source/Hurricane/Hurricane_V7_Assembly.blend'))
    with bpy.context.temp_override(window=bpy.context.window_manager.windows[0]):prepare()
    return None
if bpy.app.driver_namespace.get('_mask_asset_review_active'):raise RuntimeError('Another art job is active')
bpy.app.driver_namespace['_mask_asset_review_active']=True;bpy.app.timers.register(run,first_interval=.5)
print('HURRICANE_GAME_PREPARATION_QUEUED')
