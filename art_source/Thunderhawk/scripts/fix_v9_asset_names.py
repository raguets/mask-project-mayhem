"""Match stable generator names; no geometry or animation changes."""
import bpy,json
changed=[]
for side in 'LR':
    for prefix in ('THK_CannonGuide_','THK_CannonSlide_'):
        for old,role in [('-0.53','Rear'),('0.15','Front')]:
            ob=bpy.data.objects.get(prefix+side+old)
            if ob:
                before=ob.name;ob.name=prefix+side+'_'+role;ob.data.name=ob.name+'_Control';changed.append([before,ob.name])
    for old,role in [('-0.65','Rear'),('0.08','Front')]:
        ob=bpy.data.objects.get('THK_RoofHinge_'+side+old)
        if ob:
            before=ob.name;ob.name='THK_RoofHinge_'+side+'_'+role;ob.data.name=ob.name+'_Control';changed.append([before,ob.name])
bpy.ops.wm.save_as_mainfile(filepath='G:/DEV/mask-project-mayhem/art_source/Thunderhawk/Thunderhawk_V9.blend',compress=True)
print(json.dumps({'renamed':changed}))
