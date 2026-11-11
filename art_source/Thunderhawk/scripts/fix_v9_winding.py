"""Resolve four inconsistent open-surface cages found by the topology audit."""
import bpy,bmesh,json
from mathutils import Vector
changed=[]
for side,sg in [('L',1),('R',-1)]:
    for prefix,direction in [('THK_DoorAFrame_',Vector((0,sg,1))),('THK_DoorReturnFront_',Vector((1,0,0)))]:
        ob=bpy.data.objects[prefix+side];bm=bmesh.new();bm.from_mesh(ob.data)
        bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
        if sum(f.normal.dot(direction)*f.calc_area() for f in bm.faces)<0:bmesh.ops.reverse_faces(bm,faces=bm.faces)
        bm.to_mesh(ob.data);bm.free();ob.data.update();changed.append(ob.name)
bpy.ops.wm.save_as_mainfile(filepath='G:/DEV/mask-project-mayhem/art_source/Thunderhawk/Thunderhawk_V9.blend',compress=True)
print(json.dumps({'consistent_winding_corrected':changed}))
