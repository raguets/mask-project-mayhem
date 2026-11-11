"""Read-only Blender MCP geometry probe; restore the current session afterwards."""
import bpy,json
from pathlib import Path
ROOT=Path('G:/DEV/mask-project-mayhem/VehicularCombat')
folder=ROOT/'Saved/Art/onfoot';backup=folder/'ground-session.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(backup),copy=True)
report=[]
try:
    for actor in ('Matt','Alex','Bruce','Hondo'):
        bpy.ops.wm.open_mainfile(filepath=str(ROOT/'SourceArt/MASK/OnFoot'/actor/(actor+'_Locomotion.blend')))
        rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
        rig.animation_data.action=bpy.data.actions[actor+'_OnFoot_Idle'];bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
        body=next(o for o in bpy.context.scene.objects if o.type=='MESH' and 'body' in o.name.lower())
        ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
        points=[ev.matrix_world@v.co for v in mesh.vertices];ev.to_mesh_clear()
        report.append({'actor':actor,'lowest_world_z_m':min(p.z for p in points),'rig_location':list(rig.location),'foot_L_head_m':list(rig.pose.bones['foot.L'].head),'foot_R_head_m':list(rig.pose.bones['foot.R'].head)})
finally:
    (folder/'ground-blender.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    bpy.ops.wm.open_mainfile(filepath=str(backup))
print(json.dumps(report))
