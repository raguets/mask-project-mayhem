import bpy,json,traceback,shutil
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Rhino'
steps=[('audit_v2',A/'validation_v2_COMPLETE',None),('Bruce_rebound',P/'art_source/Bruce_Sato/renders/v1_final/COMPLETE','review_bruce_v1.py'),('Rhino_v2',A/'renders/v2/COMPLETE','review_final_v2.py')];state={'i':0,'started':False}
def advance():
 try:
  if state['i']==len(steps):(A/'final_reviews_v2_COMPLETE').write_text('Final V2 vehicle and rebound Bruce views complete. Inspect PNGs.');return None
  name,marker,script=steps[state['i']]
  if not state['started']:
   if script:
    if name=='Bruce_rebound':
     backup=marker.parent.with_name('v1_before_knee_rebind')
     if not backup.exists():shutil.copytree(marker.parent,backup)
    path=A/'scripts'/script;exec(compile(path.read_text(encoding='utf-8'),str(path),'exec'),{'__name__':'__main__'})
   state['started']=True;(A/'final_reviews_v2_progress.json').write_text(json.dumps({'stage':name}))
  error=marker.parent/('ERROR.json' if script else 'validation_v2_ERROR.json')
  if error.exists():raise RuntimeError(error.read_text())
  if not marker.exists():return .6
  if name=='audit_v2':
   data=json.loads((A/'validation_v2.json').read_text())
   if data['collision_frames']:raise RuntimeError('V2 mechanism intersections require inspection: '+str(data['collision_frames'][:10]))
   if not data['launcher_order_ok']:raise RuntimeError('V2 launcher interlock failed')
  state['i']+=1;state['started']=False;return .6
 except Exception:
  (A/'final_reviews_v2_ERROR.json').write_text(json.dumps({'stage':steps[state['i']][0],'error':traceback.format_exc()}));return None
bpy.app.timers.register(advance,first_interval=.5);print('RHINO_V2_SERIAL_REVIEWS_QUEUED')
