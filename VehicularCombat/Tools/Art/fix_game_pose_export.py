"""MCP: repair only pose baking in the existing game copy; preserve V14 and UV atlases."""
import bpy,json,traceback
from pathlib import Path
from mathutils import Matrix
ROOT=Path('G:/DEV/mask-project-mayhem');OUT=ROOT/'VehicularCombat/SourceArt/MASK/Thunderhawk'
REPORT=ROOT/'VehicularCombat/Saved/Art/pose-export-repair.json'

def run():
    report={}
    try:
        bpy.ops.wm.open_mainfile(filepath=str(ROOT/'art_source/Thunderhawk/Thunderhawk_V14.blend'))
        poses={}
        with bpy.context.temp_override(window=bpy.context.window_manager.windows[0]):
            rig=bpy.data.objects['MattTrakker_Rig'];scene=bpy.context.scene
            try:rig.driver_remove('["driving_pose"]')
            except (TypeError,RuntimeError):pass
            for name,value in [('Standing',0.),('Driving',1.)]:
                rig['driving_pose']=value;rig.update_tag(refresh={'OBJECT','DATA','TIME'});scene.frame_set(1);bpy.context.view_layer.update()
                ev=rig.evaluated_get(bpy.context.evaluated_depsgraph_get())
                poses[name]={b.name:b.matrix_basis.copy() for b in ev.pose.bones}
                report[name]={'head':list(ev.pose.bones['head'].matrix.translation),'pelvis':list(ev.pose.bones['pelvis'].matrix.translation)}
        bpy.ops.wm.open_mainfile(filepath=str(ROOT/'art_source/GameReady/Thunderhawk/Thunderhawk_GameReady.blend'))
        with bpy.context.temp_override(window=bpy.context.window_manager.windows[0]):
            rig=bpy.data.objects['Matt_GameRig'];rig.data.pose_position='POSE'
            for name,sample in poses.items():
                action=bpy.data.actions.get('Matt_'+name) or bpy.data.actions.new('Matt_'+name)
                action.use_fake_user=True;rig.animation_data_create();rig.animation_data.action=action
                for frame in (1,25):
                    for bone_name,matrix in sample.items():
                        bone=rig.pose.bones[bone_name];bone.rotation_mode='QUATERNION';bone.matrix_basis=matrix
                        for prop in ('location','rotation_quaternion','scale'):bone.keyframe_insert(data_path=prop,frame=frame,group=bone_name)
            for name in ('MattBody','MattHair','Spectrum'):
                bpy.ops.object.select_all(action='DESELECT')
                for ob in [rig,bpy.data.objects[name]]:ob.select_set(True)
                bpy.context.view_layer.objects.active=rig
                bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,object_types={'ARMATURE','MESH'},
                    axis_forward='-Y',axis_up='Z',add_leaf_bones=False,use_mesh_modifiers=True,bake_anim=name=='MattBody',
                    bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0.)
            bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'art_source/GameReady/Thunderhawk/Thunderhawk_GameReady.blend'))
            report['passed']=abs(report['Standing']['head'][2]-report['Driving']['head'][2])>.2
    except Exception:
        report['error']=traceback.format_exc()
    REPORT.write_text(json.dumps(report,indent=2),encoding='utf-8')
    return None

bpy.app.timers.register(run,first_interval=1.)
print('POSE_REPAIR_QUEUED')
