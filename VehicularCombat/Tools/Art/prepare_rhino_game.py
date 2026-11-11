"""Run in installed Blender MCP; derive game meshes without altering Rhino V3."""
import bpy,json,traceback,re,math
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path('G:/DEV/mask-project-mayhem');PROJECT=ROOT/'VehicularCombat'
OUT=PROJECT/'SourceArt/MASK/Rhino';WORK=ROOT/'art_source/GameReady/Rhino'
OUT.mkdir(parents=True,exist_ok=True);WORK.mkdir(parents=True,exist_ok=True)
exec((PROJECT/'Tools/Art/blender_game_export_helpers.py').read_text(encoding='utf-8-sig'))

def prepare():
    try:
        source=bpy.context.scene;source.frame_set(1)
        control=bpy.data.objects['Rhino_Control'];control.animation_data.action=None
        controllers=[o for o in source.objects if o.type=='EMPTY']
        control['battle_mode']=0.;control.update_tag();bpy.context.view_layer.update()
        rest={o.name:o.matrix_world.copy() for o in controllers}
        conversion=Matrix.Diagonal((100.,-100.,100.,1.));tracks={o.name:[] for o in controllers}
        for frame in range(97):
            control['battle_mode']=frame/96.;control.update_tag();bpy.context.view_layer.update()
            for o in controllers:
                t,q,s=(conversion @ o.matrix_world @ rest[o.name].inverted() @ conversion.inverted()).decompose()
                tracks[o.name].append({'t':list(t),'q':[q.x,q.y,q.z,q.w],'s':list(s)})
        control['battle_mode']=0.;control.update_tag();bpy.context.view_layer.update()
        vehicles=[o for o in source.objects if o.type=='MESH' and any(c.name in ('Rhino_Truck','Rhino_Interior','Rhino_RearVehicle') for c in o.users_collection) and not o.hide_render]
        wheels=[]
        for o in vehicles:
            if o.name.endswith('_Tire'):
                points=[o.matrix_world @ Vector(c) for c in o.bound_box];center=sum(points,Vector())/8
                wheels.append({'prefix':o.name[:-5],'label':'W'+str(len(wheels)),'position_cm':[center.x*100,-center.y*100,center.z*100],
                    'radius_cm':o.dimensions.z*50,'pod':o.parent.name=='Rhino_RearVehicle_Root'})
        actors=[]
        for name,prefix in [('Alex','AS'),('Bruce','BS')]:
            rig=bpy.data.objects['AlexSector_Rig' if name=='Alex' else 'BruceSato_Rig'];poses={}
            try:rig.driver_remove('["driving_pose"]')
            except (RuntimeError,TypeError):pass
            for pose,v in [('Standing',0.),('Driving',1.)]:
                rig['driving_pose']=v;rig['mask_on']=False;rig.update_tag(refresh={'OBJECT','DATA','TIME'});source.frame_set(1);bpy.context.view_layer.update()
                ev=rig.evaluated_get(bpy.context.evaluated_depsgraph_get());poses[pose]={b.name:b.matrix_basis.copy() for b in ev.pose.bones}
            rig['driving_pose']=0.;rig['mask_on']=False;rig.update_tag();bpy.context.view_layer.update()
            body=[o for o in source.objects if o.type=='MESH' and any(c.name==prefix+'_Character' for c in o.users_collection)]
            mask=[o for o in source.objects if o.type=='MESH' and any(c.name==prefix+'_Mask' for c in o.users_collection)]
            actors.append({'name':name,'rig':rig,'world':rig.matrix_world.copy(),'poses':poses,'body':body,'mask':mask})
        all_meshes=vehicles+[o for a in actors for o in a['body']+a['mask']]
        # Hidden viewport objects can retain stale matrix_world values. Expose
        # selected export sources in memory before evaluating their rest meshes.
        for ob in [o for a in actors for o in a['body']+a['mask']]:
            try:ob.driver_remove('hide_viewport')
            except (TypeError,RuntimeError):pass
            ob.hide_viewport=False;ob.hide_set(False);ob.update_tag()
        bpy.context.view_layer.update()
        materials=material_contract(sorted({s.material for o in all_meshes for s in o.material_slots if s.material},key=lambda m:m.name))
        game=bpy.data.scenes.new('Rhino_GameReady');bpy.context.window.scene=game
        material_copies={};jobs=[];parts=[]
        for a in actors:a['rig'].data.pose_position='REST'
        bpy.context.window.scene=source;bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
        def copy_mesh(o,actor=None):
            states=[(m,m.show_viewport) for m in o.modifiers]
            for m,_ in states:
                if m.type in ('SUBSURF','ARMATURE'):m.show_viewport=False
            bpy.context.view_layer.update();me=bpy.data.meshes.new_from_object(o.evaluated_get(deps),preserve_all_data_layers=True,depsgraph=deps)
            for m,v in states:m.show_viewport=v
            me.transform(actor['world'].inverted() @ o.matrix_world if actor else o.matrix_world)
            ob=bpy.data.objects.new(o.name+'_Game',me);game.collection.objects.link(ob)
            for group in o.vertex_groups:ob.vertex_groups.new(name=group.name)
            if actor and not len(ob.vertex_groups):ob.vertex_groups.new(name='head').add(list(range(len(me.vertices))),1.,'REPLACE')
            for i,mat in enumerate(me.materials):
                if mat:
                    if mat.name not in material_copies:
                        material_copies[mat.name]=mat.copy();material_copies[mat.name].name='M_Game_'+mat.name.split('.')[0]
                    me.materials[i]=material_copies[mat.name]
            return ob
        groups={}
        for o in vehicles:
            parent=o.parent
            while parent and parent.name not in rest:parent=parent.parent
            owner=parent.name if parent else 'Rhino_Control'
            wheel=next((w for w in wheels if o.name.startswith(w['prefix']+'_')),None)
            glass=any(s.material and 'Glass' in s.material.name for s in o.material_slots)
            key=('SM_RH_'+wheel['label']) if wheel else 'SM_'+owner+('_Glass' if glass else '')
            groups.setdefault(key,{'meshes':[],'control':owner,'wheel':wheel['label'] if wheel else '', 'glass':glass,'pod':owner in ('Rhino_RearVehicle_Root','RH_PodSeatBackFold')})['meshes'].append(copy_mesh(o))
        bpy.context.window.scene=game
        for name,g in groups.items():
            ob=join(g['meshes'],name);reduce(ob,60000 if g['control']=='Rhino_Control' and not g['wheel'] else 16000);triangulate(ob)
            if not g['glass']:jobs.append((ob,ob.name+'_BaseColor',2048 if name=='SM_Rhino_Control' else 1024))
            else:unwrap(ob)
            parts.append({'name':name,'control':g['control'],'wheel':g['wheel'],'glass':g['glass'],'pod':g['pod'],'samples':tracks[g['control']]})
        for a in actors:
            bpy.context.window.scene=game
            rig=a['rig'].copy();rig.data=a['rig'].data.copy();game.collection.objects.link(rig);rig.name=a['name']+'_GameRig';rig.animation_data_clear();rig.matrix_world=Matrix.Identity(4)
            for b in rig.pose.bones:
                b.matrix_basis=Matrix.Identity(4)
                for c in list(b.constraints):b.constraints.remove(c)
            rig.data.pose_position='REST';a['game_rig']=rig;a['meshes']={}
            for kind,objects in [('Body',[o for o in a['body'] if 'Hair' not in o.name]),('Hair',[o for o in a['body'] if 'Hair' in o.name]),('Mask',a['mask'])]:
                if not objects:continue
                bpy.context.window.scene=source;copies=[]
                for o in objects:
                    ob=copy_mesh(o,a);bpy.context.window.scene=game;reduce(ob,25000 if 'ContinuousFlightSuit' in o.name else 12000);copies.append(ob);bpy.context.window.scene=source
                bpy.context.window.scene=game;ob=join(copies,a['name']+kind);triangulate(ob)
                mod=ob.modifiers.new('SourceSkeleton','ARMATURE');mod.object=rig;ob.parent=rig;a['meshes'][kind]=ob
                jobs.append((ob,ob.name+'_BaseColor',2048 if kind=='Body' else 1024))
            rig.data.pose_position='POSE'
            for pose,sample in a['poses'].items():
                action=bpy.data.actions.new(a['name']+'_'+pose);action.use_fake_user=True;rig.animation_data_create();rig.animation_data.action=action
                for f in (1,25):
                    for n,m in sample.items():
                        b=rig.pose.bones[n];b.rotation_mode='QUATERNION';b.matrix_basis=m
                        for prop in ('location','rotation_quaternion','scale'):b.keyframe_insert(data_path=prop,frame=f,group=n)
            rig.data.pose_position='REST'
        for ob,name,size in jobs:
            write('progress.json',{'stage':'baking','current':name});bake_color(ob,name,size)
        export([bpy.data.objects[p['name']] for p in parts],'Rhino_Visual')
        # Physics proxy uses the four persistent truck tires, independently of the six pod tires.
        truck_wheels=[w for w in wheels if not w['pod']]
        arm=bpy.data.armatures.new('RH_PhysicsSkeleton');physics=bpy.data.objects.new('RH_PhysicsRig',arm);game.collection.objects.link(physics)
        select([physics]);bpy.ops.object.mode_set(mode='EDIT');root=arm.edit_bones.new('root');root.head=(0,0,0);root.tail=(0,0,.25)
        for w in truck_wheels:
            p=w['position_cm'];b=arm.edit_bones.new('wheel_'+w['label']);b.head=(p[0]/100,-p[1]/100,p[2]/100);b.tail=b.head+Vector((0,0,.25));b.parent=root
        bpy.ops.object.mode_set(mode='OBJECT');bpy.ops.mesh.primitive_cube_add(size=1,location=(1.3,0,1.55));proxy=bpy.context.object;proxy.name='RH_PhysicsChassis';proxy.dimensions=(6.4,2.35,2.05)
        bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);proxy.vertex_groups.new(name='root').add(list(range(len(proxy.data.vertices))),1.,'REPLACE')
        mod=proxy.modifiers.new('ChassisSkin','ARMATURE');mod.object=physics;proxy.parent=physics;unwrap(proxy)
        game.frame_start=1;game.frame_end=25
        proxy.hide_render=True;proxy.display_type='WIRE';proxy.hide_set(True);physics.hide_render=True
        manifest={'source':'Rhino_V3 / AlexSector_V1 / BruceSato_V1','fps':24,'duration':5.,'parts':parts,'materials':materials,'wheels':wheels,
            'crew':[{'name':a['name'],'location_cm':[a['world'].translation.x*100,-a['world'].translation.y*100,a['world'].translation.z*100], 'meshes':list(a['meshes'])} for a in actors],
            'pod_track':tracks['Rhino_RearVehicle_Root'],'geometry_interpretation':'Existing supplied toy-based V3, preserved estimated dimensions and kinematics.'}
        write('manifest.json',manifest)
        bpy.ops.wm.save_as_mainfile(filepath=str(WORK/'Rhino_GameReady.blend'))
        # Export centimetre copies with unit armature roots; never change source geometry.
        game.unit_settings.system='METRIC';game.unit_settings.scale_length=.01;scale=Matrix.Diagonal((100.,100.,100.,1.))
        def cm_rig(original):
            rig=original.copy();rig.data=original.data.copy();game.collection.objects.link(rig);rig.name=original.name+'_CM';rig.animation_data_clear();rig.data.transform(scale);rig.matrix_world=Matrix.Identity(4);rig.data.pose_position='REST'
            for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4)
            return rig
        def cm_mesh(source,rig):
            ob=source.copy();ob.data=source.data.copy();game.collection.objects.link(ob);ob.data.transform(scale);ob.parent=rig;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_world=Matrix.Identity(4)
            for m in ob.modifiers:
                if m.type=='ARMATURE':m.object=rig
            return ob
        def cm_export(obs,name,animation=False):
            select(obs);bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',add_leaf_bones=False,bake_anim=animation,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0.,mesh_smooth_type='FACE',use_tspace=True)
        for a in actors:
            rig=cm_rig(a['game_rig'])
            for kind,ob in a['meshes'].items():cm_export([rig,cm_mesh(ob,rig)],a['name']+kind)
            rig.data.pose_position='POSE'
            for pose,sample in a['poses'].items():
                action=bpy.data.actions.new(a['name']+'_CM_'+pose);rig.animation_data_create();rig.animation_data.action=action
                for f in (1,25):
                    for n,m in sample.items():
                        matrix=m.copy();matrix.translation*=100;b=rig.pose.bones[n];b.rotation_mode='QUATERNION';b.matrix_basis=matrix
                        for prop in ('location','rotation_quaternion','scale'):b.keyframe_insert(data_path=prop,frame=f,group=n)
                game.frame_set(1);bpy.context.view_layer.update();cm_export([rig],a['name']+'_'+pose,True)
        rig=cm_rig(physics);cm_export([rig,cm_mesh(proxy,rig)],'Rhino_Physics')
        write('progress.json',{'stage':'COMPLETE','parts':len(parts),'tires':len(wheels),'crew':2})
        bpy.ops.wm.open_mainfile(filepath=str(ROOT/'art_source/Rhino/Rhino_V3.blend'))
    except Exception:write('ERROR.json',{'error':traceback.format_exc()});print(traceback.format_exc())
    finally:bpy.app.driver_namespace.pop('_mask_asset_review_active',None)
    return None

def run():
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'art_source/Rhino/Rhino_V3.blend'))
    with bpy.context.temp_override(window=bpy.context.window_manager.windows[0]):prepare()
    return None
if bpy.app.driver_namespace.get('_mask_asset_review_active'):raise RuntimeError('An art job is active')
bpy.app.driver_namespace['_mask_asset_review_active']=True
bpy.app.timers.register(run,first_interval=1.)
print('RHINO_GAME_PREPARATION_QUEUED')
