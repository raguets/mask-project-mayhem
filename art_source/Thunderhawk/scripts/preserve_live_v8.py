import bpy, json
from pathlib import Path
out=Path('G:/DEV/mask-project-mayhem/art_source/Thunderhawk/Thunderhawk_V8_live_before_rebuild.blend')
if out.exists():
    raise RuntimeError('Existing live backup must not be overwritten')
state={'original_path':bpy.data.filepath,'dirty_before':bpy.data.is_dirty,'frame':bpy.context.scene.frame_current}
bpy.ops.wm.save_as_mainfile(filepath=str(out),copy=True)
state.update({'copy':str(out),'bytes':out.stat().st_size,'active_path_after':bpy.data.filepath})
print(json.dumps(state))
