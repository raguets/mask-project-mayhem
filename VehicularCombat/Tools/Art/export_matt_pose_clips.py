"""MCP: explicit animation-only FBX clips on the existing Matt skeleton."""
import bpy,json,traceback
from pathlib import Path
ROOT=Path('G:/DEV/mask-project-mayhem');OUT=ROOT/'VehicularCombat/SourceArt/MASK/Thunderhawk'

def run():
    report={}
    try:
        if bpy.app.driver_namespace.get('_mask_asset_review_active'):raise RuntimeError('Review queue active')
        bpy.ops.wm.open_mainfile(filepath=str(ROOT/'art_source/GameReady/Thunderhawk/Thunderhawk_GameReady.blend'))
        with bpy.context.temp_override(window=bpy.context.window_manager.windows[0]):
            rig=bpy.data.objects['Matt_GameRig'];scene=bpy.context.scene;rig.data.pose_position='POSE'
            for pose in ('Standing','Driving'):
                action=bpy.data.actions['Matt_'+pose];rig.animation_data.action=action
                rig.animation_data.action_slot=action.slots[0]
                scene.frame_start=1;scene.frame_end=25;scene.frame_set(1);rig.update_tag(refresh={'OBJECT','DATA','TIME'});bpy.context.view_layer.update()
                ev=rig.evaluated_get(bpy.context.evaluated_depsgraph_get())
                report[pose]={'head':list(ev.pose.bones['head'].matrix.translation),'pelvis':list(ev.pose.bones['pelvis'].matrix.translation)}
                bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
                bpy.ops.export_scene.fbx(filepath=str(OUT/('Matt_'+pose+'.fbx')),use_selection=True,object_types={'ARMATURE'},
                    axis_forward='-Y',axis_up='Z',add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=False,
                    bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0.,bake_anim_force_startend_keying=True)
            report['passed']=abs(report['Standing']['head'][2]-report['Driving']['head'][2])>.2
    except Exception:report['error']=traceback.format_exc()
    (ROOT/'VehicularCombat/Saved/Art/pose-clips-export.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return None

bpy.app.timers.register(run,first_interval=1.)
print('POSE_CLIPS_EXPORT_QUEUED')
