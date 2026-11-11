"""Inspect the existing Boulder Hill V6 through Blender MCP, preserving the session."""
import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path('G:/DEV/mask-project-mayhem');out=root/'VehicularCombat/Saved/SilentValley'
bpy.ops.wm.save_as_mainfile(filepath=str(out/'blender-session-before-boulder.blend'),copy=True)
bpy.ops.wm.open_mainfile(filepath=str(root/'art_source/Boulder_Hill/BoulderHill_V6_Base.blend'))
bpy.context.scene.frame_set(211);bpy.context.view_layer.update()
objects=[]
for ob in bpy.context.scene.objects:
    if ob.type=='MESH':
        ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());points=[ev.matrix_world@Vector(p) for p in ev.bound_box]
        objects.append({'name':ob.name,'parent':ob.parent.name if ob.parent else None,'vertices':len(ob.data.vertices),'min':[min(p[i] for p in points) for i in range(3)],'max':[max(p[i] for p in points) for i in range(3)],'hidden':ob.hide_render})
report={'source':bpy.data.filepath,'frame':bpy.context.scene.frame_current,'controls':{o.name:{k:str(o[k]) for k in o.keys()} for o in bpy.context.scene.objects if o.type=='EMPTY' and 'Control' in o.name},'meshes':objects}
(out/'boulder-inspection.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('BOULDER_INSPECTED '+str(len(objects))+' meshes; source left open for export, session backup preserved')
