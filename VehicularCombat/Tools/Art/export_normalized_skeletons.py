"""MCP: centimetre skeletal exports with unit root scale, without changing metre sources.

Chaos LocateBoneOffset inverse-transforms by the root body's reference matrix.
A Blender FBX armature root scaled 100 collapses its suspension offsets by 100.
"""
import bpy,json,traceback,shutil
from pathlib import Path
from mathutils import Matrix
ROOT=Path('G:/DEV/mask-project-mayhem');OUT=ROOT/'VehicularCombat/SourceArt/MASK/Thunderhawk'
REPORT=ROOT/'VehicularCombat/Saved/Art/normalized-skeleton-export.json'

def run():
    report={};temporary=[];renamed=[]
    try:
        if bpy.app.driver_namespace.get('_mask_asset_review_active'):raise RuntimeError('Review queue active')
        bpy.ops.wm.open_mainfile(filepath=str(ROOT/'art_source/GameReady/Thunderhawk/Thunderhawk_GameReady.blend'))
        with bpy.context.temp_override(window=bpy.context.window_manager.windows[0]):
            scene=bpy.context.scene;unit=scene.unit_settings.scale_length
            original=bpy.data.objects['Matt_GameRig'];poses={}
            for pose in ('Standing','Driving'):
                action=bpy.data.actions['Matt_'+pose];original.animation_data.action=action
                original.animation_data.action_slot=action.slots[0];scene.frame_set(1);bpy.context.view_layer.update()
                ev=original.evaluated_get(bpy.context.evaluated_depsgraph_get())
                poses[pose]={b.name:b.matrix_basis.copy() for b in ev.pose.bones}
            scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.01
            scale=Matrix.Diagonal((100.,100.,100.,1.))
            archive=ROOT/'VehicularCombat/Saved/Art/fbx-before-normalization';archive.mkdir(parents=True,exist_ok=True)
            def export(objects,filename,animate=False):
                target=OUT/(filename+'.fbx')
                if target.exists() and not (archive/target.name).exists():shutil.copy2(target,archive/target.name)
                bpy.ops.object.select_all(action='DESELECT')
                for ob in objects:ob.select_set(True)
                bpy.context.view_layer.objects.active=objects[0]
                bpy.ops.export_scene.fbx(filepath=str(target),use_selection=True,object_types={'ARMATURE','MESH'},
                    axis_forward='-Y',axis_up='Z',add_leaf_bones=False,bake_anim=animate,bake_anim_use_all_actions=False,
                    bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0.,mesh_smooth_type='FACE',use_tspace=True)
            def rig_copy(source):
                name=source.name;source.name=name+'_MetreSource';renamed.append((source,name))
                rig=source.copy();rig.data=source.data.copy();scene.collection.objects.link(rig);rig.name=name
                rig.animation_data_clear();rig.data.transform(scale);rig.matrix_world=Matrix.Identity(4)
                for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4)
                temporary.append(rig);return rig
            def mesh_copy(name,rig):
                source=bpy.data.objects[name];ob=source.copy();ob.data=source.data.copy();scene.collection.objects.link(ob)
                ob.data.transform(scale);ob.parent=rig;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_world=Matrix.Identity(4)
                for m in ob.modifiers:
                    if m.type=='ARMATURE':m.object=rig
                temporary.append(ob);return ob
            rig=rig_copy(original);rig.data.pose_position='REST'
            for name in ('MattBody','MattHair','Spectrum'):
                ob=mesh_copy(name,rig);export([rig,ob],name)
            rig.data.pose_position='POSE';scene.frame_start=1;scene.frame_end=25
            for pose,sample in poses.items():
                action=bpy.data.actions.new('ExportCM_'+pose);rig.animation_data_create();rig.animation_data.action=action
                for frame in (1,25):
                    for name,matrix in sample.items():
                        m=matrix.copy();m.translation*=100.
                        b=rig.pose.bones[name];b.rotation_mode='QUATERNION';b.matrix_basis=m
                        for prop in ('location','rotation_quaternion','scale'):b.keyframe_insert(data_path=prop,frame=frame,group=name)
                scene.frame_set(1);bpy.context.view_layer.update()
                export([rig],'Matt_'+pose,True)
                ev=rig.evaluated_get(bpy.context.evaluated_depsgraph_get())
                report[pose]={'head_cm':list(ev.pose.bones['head'].matrix.translation)}
            physics=rig_copy(bpy.data.objects['THK_PhysicsRig']);physics.data.pose_position='REST'
            ob=mesh_copy('THK_PhysicsChassis',physics);export([physics,ob],'Thunderhawk_Physics')
            report.update(passed=True,root_object_scale=list(physics.scale),fbx_scene_unit_metres=.01)
            manifest=json.loads((OUT/'manifest.json').read_text(encoding='utf-8'))
            manifest['skeletal_export']='Centimetre copies, root scale 1; source blend remains metres. Explicit standing/driving animation-only clips.'
            (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
            scene.unit_settings.scale_length=unit
            for ob in reversed(temporary):bpy.data.objects.remove(ob,do_unlink=True)
            for ob,name in renamed:ob.name=name
    except Exception:report['error']=traceback.format_exc()
    REPORT.write_text(json.dumps(report,indent=2),encoding='utf-8')
    return None

bpy.app.timers.register(run,first_interval=1.)
print('NORMALIZED_SKELETON_EXPORT_QUEUED')
