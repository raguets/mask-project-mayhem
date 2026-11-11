"""Reopen/normalize each standalone source, verify controls and return to V13."""
import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');T=P/'art_source/Thunderhawk';A=P/'art_source/Matt_Trakker';out={}
paths=[A/'MattTrakker_V4.blend',T/'Thunderhawk_V13_Vehicle.blend',A/'Spectrum_V3.blend']
try:
    for path in paths:
        bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;entry={'reopened':True,'objects':len(s.objects)}
        if path.name.startswith('Matt'):
            assert not bpy.data.objects.get('THK_Hood');assert sum(o.type=='ARMATURE' for o in s.objects)==1
            r=bpy.data.objects['MattTrakker_Rig'];head=bpy.data.objects['MT_Head_AnatomicalSurface'];identity=head.data.as_pointer();states=[]
            for pose in [0,1]:
                for masked in [False,True]:
                    r['driving_pose']=pose;r['mask_on']=masked;r.update_tag();s.frame_set(1+pose);bpy.context.view_layer.update()
                    visible=sum(not o.hide_render for o in bpy.data.collections['Spectrum11_Asset'].objects)
                    assert (visible>0)==masked and not head.hide_render and head.data.as_pointer()==identity
                    states.append({'driving_pose':pose,'mask_on':masked,'visible_mask_parts':visible,'same_head':True})
            r['driving_pose']=0;r['mask_on']=False;r.update_tag();s.frame_set(1);bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT');r.select_set(True);bpy.context.view_layer.objects.active=r
            entry.update({'one_character_one_rig_one_head':True,'four_states':states,'vehicle_dependency':False})
            focus=(0,0,.94);distance=3.2
        elif path.name.startswith('Thunderhawk'):
            assert not any(o.type=='ARMATURE' for o in s.objects);assert not bpy.data.objects.get('MattTrakker_Rig')
            for name in ['THK_DoorCannon_L','THK_DoorCannon_R','THK_ParcelShelf','THK_RearPlate_MASK_Logo']:assert bpy.data.objects.get(name)
            assert bpy.data.materials.get('THK13_LightlyTintedGlass')
            s.frame_set(1);entry.update({'character_dependency':False,'parcel_shelf_and_MASK_plate':True,'tinted_glazing':True});focus=(0,0,.7);distance=6
        else:
            assert not any(o.type=='ARMATURE' for o in s.objects);assert not bpy.data.objects.get('MattTrakker_Rig');assert bpy.data.objects.get('Spectrum_HeadSocket')
            for ob in s.objects:
                if 'canonical_part_name' in ob:ob.name=ob['canonical_part_name']
                assert not ob.animation_data
                assert not any(mod.type=='ARMATURE' for mod in ob.modifiers)
            entry.update({'character_dependency':False,'vehicle_dependency':False,'standalone_socket':True});focus=(0,0,.14);distance=.9
        for screen in bpy.data.screens:
            for area in screen.areas:
                if area.type=='VIEW_3D':
                    space=area.spaces.active;space.overlay.show_extras=False;space.shading.type='MATERIAL';space.region_3d.view_location=focus;space.region_3d.view_distance=distance;space.region_3d.view_rotation=(Vector((3,4,2))-Vector(focus)).to_track_quat('Z','Y')
                elif area.type=='PROPERTIES' and path.name.startswith('Matt'):area.spaces.active.context='OBJECT';area.spaces.active.pin_id=r
        bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);entry['regular_main_file_saved']=True;out[path.name]=entry
    for path in paths:
        bpy.ops.wm.open_mainfile(filepath=str(path));assert len(bpy.context.scene.objects)>10;out[path.name]['reopened_after_save']=True
finally:
    bpy.ops.wm.open_mainfile(filepath=str(T/'Thunderhawk_V13.blend'));(T/'standalone_validation_v13.json').write_text(json.dumps(out,indent=2))
print('V13_STANDALONE_ASSETS_REOPENED',json.dumps(out))
