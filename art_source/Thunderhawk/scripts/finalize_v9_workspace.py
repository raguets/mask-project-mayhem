"""Portable image links and a useful review viewport; geometry unchanged."""
import bpy,json
from mathutils import Vector
from pathlib import Path
root=Path('G:/DEV/mask-project-mayhem/art_source/Thunderhawk')
for ob in bpy.data.collections['THK9_Reference'].objects:
    if ob.type=='EMPTY' and getattr(ob,'data',None):ob.data.filepath='//Images reference/'+Path(bpy.path.abspath(ob.data.filepath)).name
s=bpy.context.scene;s.frame_set(1)
for screen in bpy.data.screens:
    for ar in screen.areas:
        if ar.type=='VIEW_3D':
            view=ar.spaces.active.region_3d
            view.view_rotation=(Vector((6.7,-6.9,3.5))-Vector((.05,0,.66))).to_track_quat('Z','Y')
            view.view_location=(.05,0,.66);view.view_distance=6.5;view.view_perspective='PERSP'
            ar.spaces.active.overlay.show_extras=False
bpy.ops.wm.save_as_mainfile(filepath=str(root/'Thunderhawk_V9.blend'),compress=True)
print(json.dumps({'file':bpy.data.filepath,'frame':s.frame_current,'references':len(bpy.data.collections['THK9_Reference'].objects)}))
