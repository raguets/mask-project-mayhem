import bpy,os
from mathutils import Vector
s=bpy.context.scene; root=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); s.cycles.samples=12
for fr,name,loc,target in [(1,'preview_road',(6,-7,4),(0,0,.65)),(97,'preview_flight',(6,-7,4),(0,0,.65)),(45,'preview_independent',(-6,-5,3.1),(-1.15,0,.75)),(97,'preview_rear',(-6,-5,3.1),(-1.15,0,.75))]:
 s.frame_set(fr); s.camera.location=loc; s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler(); s.render.filepath=os.path.join(root,'renders','v4',name+'.png'); bpy.ops.render.render(write_still=True)

