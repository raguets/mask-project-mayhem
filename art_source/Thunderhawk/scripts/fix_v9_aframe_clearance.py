"""Apply the matching generator correction to the current V9, once."""
import bpy
for side,sg in [('L',1),('R',-1)]:
    ob=bpy.data.objects['THK_DoorAFrame_'+side]
    if ob.get('clearance_revision')==2:continue
    uv=ob.data.uv_layers.active;weights={}
    for p in ob.data.polygons:
        for li in p.loop_indices:weights[ob.data.loops[li].vertex_index]=uv.data[li].uv.y
    for vi,v in weights.items():ob.data.vertices[vi].co.x-=.006*v;ob.data.vertices[vi].co.y+=sg*.006*v
    ob['clearance_revision']=2;ob.data.update()
bpy.ops.wm.save_as_mainfile(filepath='G:/DEV/mask-project-mayhem/art_source/Thunderhawk/Thunderhawk_V9.blend',compress=True)
print('AFRAME_CLEARANCE_REV2')
