import bpy,json
R=bpy.data.objects['VanessaWarfield_Rig'];S=bpy.context.scene;rows=[]
for pose,mask in [(0,False),(1,True),(0,True),(1,False)]:
 R['driving_pose']=float(pose);R['in_vehicle']=float(pose);R['mask_on']=mask
 for o in S.objects:o.update_tag(refresh={'OBJECT','DATA','TIME'})
 S.frame_set(2);S.frame_set(1);bpy.context.view_layer.update()
 rows.append({'requested':[pose,mask],'actual_props':{k:R[k] for k in ['driving_pose','in_vehicle','mask_on']},'location':list(R.matrix_world.translation),'bones':{b.name:list(b.rotation_quaternion) for b in R.pose.bones if b.name in ['thigh.L','upper_arm.L','thigh_L']},'mask':[(o.name,o.hide_render,o.hide_viewport) for o in bpy.data.collections['Whip_Mask'].objects][:3]})
print(json.dumps(rows))
