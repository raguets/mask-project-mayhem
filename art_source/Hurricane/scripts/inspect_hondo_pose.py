import bpy,json
r=bpy.data.objects['HondoMacLean_Rig'];S=bpy.context.scene;result={}
for p in [0,1]:
    r['driving_pose']=p;r.update_tag();S.frame_set(1);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();items={}
    for name in ['HMC_Head_AnatomicalSurface','HMC_GloveSkin_L','HMC_GloveSkin_R','HMC_BootUpper_L','HMC_ContinuousFlightSuit']:
        o=bpy.data.objects[name];e=o.evaluated_get(dg);m=e.to_mesh();v=[e.matrix_world@x.co for x in m.vertices];items[name]={'min':[min(x[i] for x in v) for i in range(3)],'max':[max(x[i] for x in v) for i in range(3)]};e.to_mesh_clear()
    result[p]=items
r['driving_pose']=0;r.update_tag();bpy.context.view_layer.update();print(json.dumps(result))
