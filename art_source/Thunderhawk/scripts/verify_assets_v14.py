"""Reopen and verify independently editable V14/Matt V5/Spectrum V4 sources."""
import bpy,json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');T=P/'art_source/Thunderhawk';A=P/'art_source/Matt_Trakker';out={}
try:
    for path in [A/'MattTrakker_V5.blend',T/'Thunderhawk_V14_Vehicle.blend',A/'Spectrum_V4.blend']:
        bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;entry={'reopened':True,'scene_objects':len(s.objects)}
        if path.name.startswith('Matt'):
            assert not bpy.data.objects.get('THK_Hood');assert sum(ob.type=='ARMATURE' for ob in s.objects)==1
            r=bpy.data.objects['MattTrakker_Rig'];head=bpy.data.objects['MT_Head_AnatomicalSurface'];pointer=head.data.as_pointer();states=[]
            for drive in [0,1]:
                for masked in [False,True]:
                    r['driving_pose']=drive;r['mask_on']=masked;r.update_tag();s.frame_set(1+drive);bpy.context.view_layer.update();visible=sum(not ob.hide_render for ob in bpy.data.collections['Spectrum11_Asset'].objects)
                    assert (visible>0)==masked and head.data.as_pointer()==pointer and not head.hide_render
                    states.append({'drive':drive,'mask':masked,'visible_mask_parts':visible,'same_head':True})
            entry.update({'one_character_one_armature_one_head':True,'four_states':states,'no_vehicle_dependency':True})
        elif path.name.startswith('Thunderhawk'):
            assert not bpy.data.objects.get('MattTrakker_Rig')
            for name in ['THK_DoorCannon_L','THK_DoorCannon_R','THK_ParcelShelf','THK_RearPlate_MASK_Logo']:assert bpy.data.objects.get(name)
            entry.update({'no_character_dependency':True,'previous_vehicle_parts_retained':True})
        else:
            assert not any(ob.type=='ARMATURE' for ob in s.objects);assert not bpy.data.objects.get('MattTrakker_Rig');assert not bpy.data.objects.get('THK_Hood')
            socket=bpy.data.objects['Spectrum_HeadSocket'];assert len(socket['rest_bind_origin'])==3
            skirt=bpy.data.objects['Spectrum_NeckSealConnectingBody'];assert 'head' in skirt.vertex_groups and len(skirt.vertex_groups)>1
            assert not any(ob.animation_data for ob in bpy.data.collections['Spectrum11_Asset'].objects)
            assert not any(mod.type=='ARMATURE' for ob in s.objects for mod in ob.modifiers)
            entry.update({'no_character_or_vehicle_dependency':True,'head_socket':True,'flexible_collar_weights_retained':True,'bind_origin':list(socket['rest_bind_origin'])})
        out[path.name]=entry
finally:
    bpy.ops.wm.open_mainfile(filepath=str(T/'Thunderhawk_V14.blend'));(T/'standalone_validation_v14.json').write_text(json.dumps(out,indent=2))
assert len(out)==3
print('V14_INDEPENDENT_ASSETS_REOPENED',json.dumps(out))
