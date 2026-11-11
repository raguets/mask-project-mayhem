import bpy
from pathlib import Path
from mathutils import Vector
s=bpy.context.scene
for prefix,sizex,sizey,energy in [('Review_Key',3.3,.65,1000),('Review_Fill',2.2,.5,650),('Review_Rim',2.8,.7,650)]:
    for ob in s.objects:
        if ob.type=='LIGHT' and ob.name.startswith(prefix):
            ob.data.shape='RECTANGLE';ob.data.size=sizex;ob.data.size_y=sizey;ob.data.energy=energy
s['THK13_Studio']='Narrow rectangular softboxes replace large disks that obscured glazing with white reflections.'
bpy.ops.wm.save_as_mainfile(filepath='G:/DEV/mask-project-mayhem/art_source/Thunderhawk/Thunderhawk_V13.blend',compress=True)
print('V13_NARROW_STUDIO_REFLECTIONS_SAVED')
