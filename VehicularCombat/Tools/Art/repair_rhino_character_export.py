"""MCP repair of cached hidden-mask frames and six-wheel rear physics export."""
import bpy,json,traceback,shutil
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path('G:/DEV/mask-project-mayhem');PROJECT=ROOT/'VehicularCombat';OUT=PROJECT/'SourceArt/MASK/Rhino'
REPORT=PROJECT/'Saved/Art/rhino-character-export-repair.json'

def game_exports(corrections,report):
    scene=bpy.data.scenes['Rhino_GameReady'];window=bpy.context.window_manager.windows[0];window.scene=scene
    with bpy.context.temp_override(window=window,scene=scene,view_layer=scene.view_layers[0]):
        for name,matrix in corrections.items():
            mesh=bpy.data.objects[name+'Mask'].data
            if max(v.co.z for v in mesh.vertices)<1.2:
                mesh.transform(matrix);report[name]['correction_applied']=True
            else:report[name]['correction_applied']=False
        manifest=json.loads((OUT/'manifest.json').read_text());wheels=[w for w in manifest['wheels'] if w['pod']]
        arm=bpy.data.armatures.new('RH_RearPhysicsSkeleton');rig=bpy.data.objects.new('RH_RearPhysicsRig',arm);scene.collection.objects.link(rig)
        scene.view_layers[0].update();bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);scene.view_layers[0].objects.active=rig
        bpy.ops.object.mode_set(mode='EDIT');root=arm.edit_bones.new('root');root.head=(0,0,0);root.tail=(0,0,.25)
        for w in wheels:
            p=w['position_cm'];bone=arm.edit_bones.new('wheel_'+w['label']);bone.head=(p[0]/100+2.6,-p[1]/100,p[2]/100);bone.tail=bone.head+Vector((0,0,.25));bone.parent=root
        bpy.ops.object.mode_set(mode='OBJECT')
        vertices=[(sx*1.45,sy*1.35,.75+sz*.5) for sx,sy,sz in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
        mesh=bpy.data.meshes.new('RH_RearPhysicsMesh');mesh.from_pydata(vertices,[],[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]);mesh.update();mesh.uv_layers.new(name='GameAtlas')
        proxy=bpy.data.objects.new('RH_RearPhysicsChassis',mesh);scene.collection.objects.link(proxy);proxy.vertex_groups.new(name='root').add(list(range(8)),1.,'REPLACE')
        mod=proxy.modifiers.new('PhysicsSkin','ARMATURE');mod.object=rig;proxy.parent=rig;proxy.hide_render=True;proxy.display_type='WIRE';proxy.hide_set(True);rig.hide_render=True;rig.hide_set(True)
        bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'art_source/GameReady/Rhino/Rhino_GameReady_v3.blend'))
        scene.unit_settings.scale_length=.01;scale=Matrix.Diagonal((100.,100.,100.,1.))
        def export(source,mesh,name):
            cm=source.copy();cm.data=source.data.copy();scene.collection.objects.link(cm);cm.name=source.name+'_CM';cm.animation_data_clear();cm.data.transform(scale);cm.matrix_world=Matrix.Identity(4);cm.hide_set(False);cm.data.pose_position='REST'
            for bone in cm.pose.bones:bone.matrix_basis=Matrix.Identity(4)
            ob=mesh.copy();ob.data=mesh.data.copy();scene.collection.objects.link(ob);ob.data.transform(scale);ob.parent=cm;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_world=Matrix.Identity(4);ob.hide_set(False)
            for mod in ob.modifiers:
                if mod.type=='ARMATURE':mod.object=cm
            target=OUT/(name+'.fbx');archive=PROJECT/'Saved/Art/rhino-before-mask-repair';archive.mkdir(parents=True,exist_ok=True)
            if target.exists():shutil.copy2(target,archive/target.name)
            bpy.ops.object.select_all(action='DESELECT');cm.select_set(True);ob.select_set(True);scene.view_layers[0].objects.active=cm
            bpy.ops.export_scene.fbx(filepath=str(target),use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',add_leaf_bones=False,bake_anim=False,mesh_smooth_type='FACE',use_tspace=True)
        for name in ('Alex','Bruce'):export(bpy.data.objects[name+'_GameRig'],bpy.data.objects[name+'Mask'],name+'Mask')
        export(rig,proxy,'RhinoRear_Physics');report['passed']=True

def run():
    report={'passed':False}
    try:
        with bpy.context.temp_override(window=bpy.context.window_manager.windows[0]):bpy.ops.wm.save_as_mainfile(filepath=str(PROJECT/'Saved/Art/Rhino_before_export_repair_session.blend'),copy=True)
        bpy.ops.wm.open_mainfile(filepath=str(ROOT/'art_source/Rhino/Rhino_V3.blend'))
        corrections={}
        with bpy.context.temp_override(window=bpy.context.window_manager.windows[0]):
            for name,prefix in [('Alex','AS'),('Bruce','BS')]:
                rig=bpy.data.objects['AlexSector_Rig' if name=='Alex' else 'BruceSato_Rig'];masks=list(bpy.data.collections[prefix+'_Mask'].objects);before={o.name:o.matrix_world.copy() for o in masks if o.type=='MESH'}
                rig['mask_on']=True;rig.update_tag()
                for ob in masks:
                    try:ob.driver_remove('hide_viewport')
                    except (TypeError,RuntimeError):pass
                    ob.hide_viewport=False;ob.hide_set(False);ob.update_tag()
                bpy.context.scene.frame_set(1);bpy.context.view_layer.update();values=[]
                for ob in masks:
                    if ob.type=='MESH':values.append(rig.matrix_world.inverted() @ ob.matrix_world @ before[ob.name].inverted() @ rig.matrix_world)
                if any((m.translation-values[0].translation).length>.001 for m in values):raise RuntimeError('Nonuniform mask frame correction; inspect before editing.')
                corrections[name]=values[0];report[name]={'local_correction_m':list(values[0].translation),'parts':len(values)}
        bpy.ops.wm.open_mainfile(filepath=str(ROOT/'art_source/GameReady/Rhino/Rhino_GameReady.blend'))
        game_exports(corrections,report)
        bpy.ops.wm.open_mainfile(filepath=str(ROOT/'art_source/Rhino/Rhino_V3.blend'))
    except Exception:report['error']=traceback.format_exc()
    REPORT.write_text(json.dumps(report,indent=2));return None
bpy.app.timers.register(run,first_interval=.5)
