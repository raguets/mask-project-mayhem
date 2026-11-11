"""Reopen the three reusable assets in Blender MCP; return to the assembly."""
import bpy,json,traceback
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');T=P/'art_source/Thunderhawk';A=P/'art_source/Matt_Trakker';out={}
files=[A/'MattTrakker_V3.blend',T/'Thunderhawk_V12_Vehicle.blend',A/'Spectrum_V2.blend']
try:
    for path in files:
        bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
        entry={'reopened':True,'scene':s.name,'objects':len(s.objects)}
        if path.name.startswith('Matt'):
            assert not any(o.name.startswith('THK_') for o in s.objects),'Vehicle object leaked into character asset'
            assert sum(o.type=='ARMATURE' for o in s.objects)==1
            rig=bpy.data.objects['MattTrakker_Rig'];head=bpy.data.objects['MT_Head_AnatomicalSurface'];identity=head.data.as_pointer();states=[];poses=[]
            for drive in [0,1]:
                for masked in [False,True]:
                    rig['driving_pose']=drive;rig['mask_on']=masked;rig.update_tag();s.frame_set(1+drive);bpy.context.view_layer.update()
                    visible=sum(not o.hide_render for o in bpy.data.collections['Spectrum11_Asset'].objects)
                    assert (visible>0)==masked and head.data.as_pointer()==identity and not head.hide_render
                    states.append({'drive':drive,'mask':masked,'visible_mask_parts':visible})
                poses.append(tuple(rig.pose.bones['foot.L'].head))
            assert (Vector(poses[0])-Vector(poses[1])).length>.2,'Driving pose did not evaluate'
            entry.update({'one_rig_one_head':True,'four_states':states,'vehicle_dependency':False,'foot_pose_changes':True})
        elif path.name.startswith('Thunderhawk'):
            assert not any(o.type=='ARMATURE' for o in s.objects)
            assert not any(o.name.startswith(('MT_','Spectrum_','MattTrakker')) for o in s.objects),'Character object leaked into vehicle asset'
            assert bpy.data.objects.get('THK_DoorCannon_L') and bpy.data.objects.get('THK_DoorCannon_R')
            for frame in range(1,194):
                s.frame_set(frame);bpy.context.view_layer.update()
                z=bpy.data.objects['THK_RearPanel_Lift'].location.z
                for side in ['L','R']:
                    assert bpy.data.objects['THK_Reactor_Deploy_'+side].location.x>=-.00001 or abs(z-.215)<1e-5
            entry.update({'character_dependency':False,'reactor_order_frames_checked':193,'two_named_cannons':True})
        else:
            assert not any(o.type=='ARMATURE' for o in s.objects)
            assert bpy.data.objects.get('Spectrum_HeadSocket')
            assert not any(o.name.startswith(('MT_','THK_','MattTrakker')) for o in s.objects)
            entry.update({'character_dependency':False,'vehicle_dependency':False,'standalone_socket':True,'unchanged_version':'V2'})
        if path.name!='Spectrum_V2.blend':
            # Turn the scoped datablock library into a regular editable main file,
            # including usable window/workspace state after the first reopen.
            s.frame_set(1)
            if path.name.startswith('Matt'):
                rig['driving_pose']=0;rig['mask_on']=False;rig.update_tag();bpy.context.view_layer.update()
            bpy.ops.object.select_all(action='DESELECT')
            for screen in bpy.data.screens:
                for area in screen.areas:
                    if area.type=='VIEW_3D':
                        area.spaces.active.overlay.show_extras=False
                        view=area.spaces.active.region_3d
                        view.view_location=(0,0,.94 if path.name.startswith('Matt') else .7)
                        view.view_distance=3.2 if path.name.startswith('Matt') else 6
                        view.view_rotation=(Vector((3,4,2))-view.view_location).to_track_quat('Z','Y')
                        area.spaces.active.shading.color_type='MATERIAL'
            bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
            entry['regular_main_file_saved']=True
        out[str(path.relative_to(P))]=entry
    for path in files[:2]:
        bpy.ops.wm.open_mainfile(filepath=str(path))
        assert len(bpy.context.scene.objects)>100
        out[str(path.relative_to(P))]['reopened_after_regular_save']=True
finally:
    bpy.ops.wm.open_mainfile(filepath=str(T/'Thunderhawk_V12.blend'))
    (T/'standalone_validation_v12.json').write_text(json.dumps(out,indent=2))
print('V12_STANDALONE_REOPEN_VALIDATION',json.dumps(out))
