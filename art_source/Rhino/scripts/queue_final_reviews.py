import bpy,json,traceback,shutil
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Rhino'
steps=[('audit',A/'validation_v1_COMPLETE',None),('Alex',P/'art_source/Alex_Sector/renders/v1_final/COMPLETE','review_alex_v1.py'),('Bruce',P/'art_source/Bruce_Sato/renders/v1_final/COMPLETE','review_bruce_v1.py'),('Rhino',A/'renders/v1/COMPLETE','review_final_v1.py')];state={'i':0,'started':False}
def advance():
 try:
  if state['i']==len(steps):(A/'final_reviews_COMPLETE').write_text('Serialized final image batches complete; inspect PNGs.');return None
  name,marker,script=steps[state['i']]
  if not state['started']:
   if script:
    backup=marker.parent.with_name(marker.parent.name+'_before_final_fit')
    if marker.parent.exists() and not backup.exists():shutil.copytree(marker.parent,backup)
    path=A/'scripts'/script;exec(compile(path.read_text(encoding='utf-8'),str(path),'exec'),{'__name__':'__main__'})
   state['started']=True;(A/'final_reviews_progress.json').write_text(json.dumps({'stage':name}))
  error=marker.parent/('ERROR.json' if script else 'validation_v1_ERROR.json')
  if error.exists():raise RuntimeError(error.read_text())
  if not marker.exists():return .6
  if name=='audit':
   report=json.loads((A/'validation_v1.json').read_text())
   if report['collision_frames']:raise RuntimeError('Mechanical surface intersections require correction before final review: '+str(report['collision_frames'][:10]))
  state['i']+=1;state['started']=False;return .6
 except Exception:
  (A/'final_reviews_ERROR.json').write_text(json.dumps({'stage':steps[state['i']][0],'error':traceback.format_exc()}));return None
bpy.app.timers.register(advance,first_interval=.5);print('RHINO_FINAL_REVIEW_BATCHES_QUEUED')
