"""Stop only this task's still-registered review callbacks before serialized restart."""
import bpy,gc,types,json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Rhino';stopped=[];restores=[]
for fn in list(gc.get_objects()):
 if not isinstance(fn,types.FunctionType) or not bpy.app.timers.is_registered(fn):continue
 ns=fn.__globals__
 if fn.__name__=='advance' and str(ns.get('A',''))==str(A):bpy.app.timers.unregister(fn);stopped.append('controller')
 elif fn.__name__=='step' and str(ns.get('job',{}).get('output_dir','')).replace('\\','/').startswith(str(A/'renders').replace('\\','/')):
  bpy.app.timers.unregister(fn);stopped.append(ns['job']['output_dir']);restores.append(ns['restore'])
for restore in restores:restore()
(A/'review_queue_reset_v2.json').write_text(json.dumps({'stopped':stopped,'reason':'Ensure one review file at a time after user revision and static seat fit.'},indent=2));print('RHINO_V2_REVIEW_CALLBACKS_SERIALIZED',stopped)
