import bpy,json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Raven';C=P/'art_source/Calhoun_Burns'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
source=A/'Raven_V5_Assembly.blend';report={'files':[]}
try:
    for kind,path in [('vehicle',A/'Raven_V5_Vehicle.blend'),('character',C/'CalhounBurns_V1.blend'),('mask',C/'CalhounMask_V1.blend')]:
        bpy.ops.wm.open_mainfile(filepath=str(path));S=bpy.context.scene
        rigs=[o for o in S.objects if o.type=='ARMATURE'];checks={};record={'kind':kind,'file':str(path),'objects':len(S.objects)}
        if kind=='vehicle':
            checks['no_character_armature']=not rigs;checks['four_persistent_tires']=sum('Tire_' in o.name for o in S.objects)==4
            root=bpy.data.objects['Raven_Control'];names=[o.data.name for o in S.objects if 'Tire_' in o.name];states=[]
            for frame in [1,76,151]:
                S.frame_set(frame);bpy.context.view_layer.update();cover=bpy.data.objects['RV_ReactorCover_VerticalSlide'];states.append({'frame':frame,'transform':root['transform'],'cover_rotation':list(cover.rotation_euler),'cover_location':list(cover.location)})
                assert names==[o.data.name for o in S.objects if 'Tire_' in o.name]
            checks['cover_no_rotation_all_sampled_states']=all(max(abs(v) for v in s['cover_rotation'])<1e-6 for s in states)
            checks['half_transform_is_continuous']=abs(states[1]['transform']-.5)<1e-5
            checks['cover_vertical_travel_032m']=abs(states[2]['cover_location'][2]-states[0]['cover_location'][2]-.32)<1e-5
            record['states']=states
        elif kind=='character':
            checks['one_armature']=len(rigs)==1;checks['one_face']=sum(o.name=='CB_Head_AnatomicalSurface' for o in S.objects)==1
            checks['no_vehicle_control']=bpy.data.objects.get('Raven_Control') is None
            rig=bpy.data.objects['CalhounBurns_Rig'];head=bpy.data.objects['CB_Head_AnatomicalSurface'];suit=bpy.data.objects['CB_ContinuousFlightSuit'];ids=(head.data.as_pointer(),suit.data.as_pointer());states=[]
            for d in [0.,1.]:
                for mask in [False,True]:
                    rig['driving_pose']=d;rig['mask_on']=mask;rig.update_tag();bpy.context.view_layer.update()
                    states.append({'driving':d,'mask':mask,'same_meshes':ids==(head.data.as_pointer(),suit.data.as_pointer()),'mask_hidden':bpy.data.objects['CB_ClosedHelmetShell'].hide_render})
            checks['same_meshes_four_states']=all(s['same_meshes'] for s in states)
            checks['mask_visibility_four_states']=all(s['mask_hidden']!=s['mask'] for s in states)
            checks['weights_preserved']=len(suit.vertex_groups)>10 and any(m.type=='ARMATURE' for m in suit.modifiers)
            checks['bone_pose_drivers_preserved']=sum(f.data_path.startswith('pose.bones[') for f in rig.animation_data.drivers)>50
            record['states']=states
        else:
            checks['no_armature']=not rigs;checks['no_face_or_vehicle']=not any(o.name in ['CB_Head_AnatomicalSurface','Raven_Control','CalhounBurns_Rig'] for o in S.objects)
            checks['head_socket_origin']=bool(bpy.data.objects['CalhounMask_HeadSocket'].get('rest_bind_origin'))
            checks['no_rig_modifiers']=not any(m.type=='ARMATURE' for o in S.objects for m in o.modifiers)
        bad=[]
        for o in S.objects:
            if not o.animation_data:continue
            for f in o.animation_data.drivers:
                if not f.driver.is_valid:bad.append(o.name+':'+f.data_path)
                for v in f.driver.variables:
                    if any(t.id is None for t in v.targets):bad.append(o.name+':missing_target')
        checks['no_invalid_or_missing_driver_targets']=not bad;record['bad_drivers']=bad;record['checks']=checks;record['passed']=all(checks.values());report['files'].append(record)
finally:bpy.ops.wm.open_mainfile(filepath=str(source))
report['passed']=len(report['files'])==3 and all(f['passed'] for f in report['files']);(A/'standalone_validation_v5.json').write_text(json.dumps(report,indent=2))
assert report['passed'],report
print('THREE_INDEPENDENT_SOURCES_REOPENED_AND_CHECKED')
