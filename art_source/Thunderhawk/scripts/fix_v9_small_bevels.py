import bpy
for side in 'LR':
    ob=bpy.data.objects['THK_DoorHandleRecess_'+side]
    for m in ob.modifiers:
        if m.type=='BEVEL':m.width=.001
bpy.ops.wm.save_as_mainfile(filepath='G:/DEV/mask-project-mayhem/art_source/Thunderhawk/Thunderhawk_V9.blend',compress=True)
print('THK9_HANDLE_BEVELS_BOUNDED')
