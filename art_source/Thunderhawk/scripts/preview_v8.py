import bpy
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1]
s=bpy.context.scene
s.cycles.samples=16
s.render.resolution_x=1000; s.render.resolution_y=700
for fr,name,loc,target in [(1,'preview_road',(5.9,-6.6,3.7),(0,0,.7)),(97,'preview_flight',(5.9,-6.6,3.7),(0,0,.9)),(97,'preview_rear',(-5.6,-5.8,2.7),(-.4,0,.7)),(97,'preview_front_flight',(8,0,1),(0,0,1))]:
    s.frame_set(fr); s.camera.location=loc
    s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler()
    s.camera.data.type='ORTHO' if name=='preview_front_flight' else 'PERSP'
    s.camera.data.ortho_scale=5.3
    s.render.filepath=str(root/'renders'/'v8'/(name+'.png'))
    bpy.ops.render.render(write_still=True)

