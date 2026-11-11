import bpy,json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Boulder_Hill'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
report={'independent':{},'assembly':{}}
for kind,name in [('independent','BoulderHill_V6_Base.blend'),('assembly','BoulderHill_V6_Assembly.blend')]:
    bpy.ops.wm.open_mainfile(filepath=str(A/name));S=bpy.context.scene;R=bpy.data.objects['BoulderHill_Control'];states=[]
    demos=[o.name for o in S.objects if o.name.startswith(('BH_Thunderhawk','BH_Rhino','THK','RH_'))]
    if kind=='independent':assert not demos,demos[:10]
    for frame in [1,65,181,211,285,510,541,211]:
        S.frame_set(frame);bpy.context.view_layer.update()
        bad=[o.name+':'+f.data_path for o in S.objects if o.animation_data for f in o.animation_data.drivers if not f.driver.is_valid]
        prism=bpy.data.objects['BH_StorefrontPivot'];garage=bpy.data.objects['BH_GarageQuarterPivot'];cap=bpy.data.objects['BH_FallingBoulder'];turret=bpy.data.objects['BH_TurretLift']
        states.append({'frame':frame,'prism_angle_x':prism.rotation_euler.x,'garage_angle_z':garage.rotation_euler.z,'cap_location':list(cap.location),'turret_z':turret.location.z,'invalid_drivers':bad})
        assert not bad,bad
        if frame==1:assert abs(prism.rotation_euler.x)<.001 and abs(garage.rotation_euler.z)<.001
        if frame==181:assert abs(prism.rotation_euler.x-1.57079632679)<.001 and turret.location.z>12
    deps=[]
    for o in S.objects:
        if o.animation_data:
            for f in o.animation_data.drivers:
                for v in f.driver.variables:
                    for t in v.targets:
                        if t.id is None:deps.append(o.name+': missing target')
    assert not deps,deps
    assert bpy.data.objects.get('BH_SoftDayFill') is not None
    assert abs(bpy.data.materials['BH_Sandstone'].diffuse_color[0]-.21)<.0001
    report[kind]={'file':str(A/name),'scene_objects':len(S.objects),'demo_objects':len(demos),'linked_libraries':[l.filepath for l in bpy.data.libraries],'missing_driver_targets':deps,'states':states}
    if kind=='assembly':
        bpy.ops.object.select_all(action='DESELECT');R.select_set(True);bpy.context.view_layer.objects.active=R
        text=bpy.data.texts.get('ASSET_README');text.clear();text.write((A/'README.md').read_text(encoding='utf-8'))
        S.frame_set(211);bpy.ops.wm.save_as_mainfile(filepath=str(A/name),compress=True)
(P/'docs/qa/boulder_standalone_v6.json').write_text(json.dumps(report,indent=2))
print('REOPEN_VALIDATED',[(k,v['scene_objects'],v['demo_objects']) for k,v in report.items()])
