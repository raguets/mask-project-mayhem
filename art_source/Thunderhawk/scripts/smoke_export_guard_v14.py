"""Exercise dirty-session preservation and source reload using a real component."""
import bpy,json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');Q=P/'docs/qa/export_helper_smoke';Q.mkdir(parents=True,exist_ok=True)
job=json.loads((P/'art_source/Thunderhawk/scripts/export_v14_job.json').read_text());component=job['components'][1].copy();component['output']=str(Q/'vehicle.blend')
job['components']=[component];job['session_backup']=str(Q/'unsaved_session.blend');job['manifest']=str(Q/'manifest.json')
source=Path(job['source_blend']);bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.scene['QA_UNSAVED_EXPORT_GUARD']='preserve-only-in-session-copy'
# Direct RNA writes do not always set is_dirty immediately. The session copy
# must therefore protect the actual state without relying only on that flag.
EXPORT_JOB=job
exec(compile((P/'art_source/shared_tools/export_components.py').read_text(),'export_components.py','exec'))
assert bpy.data.filepath==str(source) and 'QA_UNSAVED_EXPORT_GUARD' not in bpy.context.scene
bpy.ops.wm.open_mainfile(filepath=str(Q/'unsaved_session.blend'));assert bpy.context.scene['QA_UNSAVED_EXPORT_GUARD']=='preserve-only-in-session-copy'
bpy.ops.wm.open_mainfile(filepath=str(Q/'vehicle.blend'));assert not bpy.data.objects.get('MattTrakker_Rig');assert 'QA_UNSAVED_EXPORT_GUARD' not in bpy.context.scene
bpy.ops.wm.open_mainfile(filepath=str(source))
(Q/'validation.json').write_text(json.dumps({'dirty_session_copy_verified':True,'export_uses_saved_source':True,'vehicle_has_no_character_dependency':True,'source_reloaded':True},indent=2))
print('EXPORT_HELPER_DIRTY_SESSION_GUARD_VERIFIED')
