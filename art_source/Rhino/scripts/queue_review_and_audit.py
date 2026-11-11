"""Continue serialized Blender jobs only after their completion markers."""
import bpy,traceback,json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Rhino';steps=[
 ('vehicle_initial',A/'renders/v1/COMPLETE',None),
 ('fit_launcher',None,A/'scripts/fit_launcher_v1.py'),
 ('alex_review',P/'art_source/Alex_Sector/renders/v1_final/COMPLETE',A/'scripts/review_alex_v1.py'),
 ('bruce_review',P/'art_source/Bruce_Sato/renders/v1_final/COMPLETE',A/'scripts/review_bruce_v1.py'),
 ('geometry_audit',A/'validation_v1_COMPLETE',A/'scripts/validate_rhino_v1.py')]
state={'index':0,'started':False}
def advance():
 try:
  if state['index']>=len(steps):(A/'review_pipeline_COMPLETE').write_text('Character reviews and geometric audit completed. Inspect reports.');return None
  name,marker,script=steps[state['index']]
  if not state['started']:
   if script:exec(compile(script.read_text(encoding='utf-8'),str(script),'exec'),{'__name__':'__main__'})
   state['started']=True;(A/'review_pipeline_progress.json').write_text(json.dumps({'stage':name}))
  error=marker.parent/('ERROR.json' if 'renders' in str(marker) else 'validation_v1_ERROR.json') if marker else None
  if error and error.exists():raise RuntimeError(error.read_text())
  if marker and not marker.exists():return .6
  state['index']+=1;state['started']=False;return .6
 except Exception:
  (A/'review_pipeline_ERROR.json').write_text(json.dumps({'stage':steps[state['index']][0],'error':traceback.format_exc()}));return None
bpy.app.timers.register(advance,first_interval=.4);print('RHINO_SERIAL_REVIEW_PIPELINE_QUEUED')
