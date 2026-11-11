import bpy,json,traceback
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Rhino';stage={'i':0}
def advance():
 try:
  if stage['i']==0:
   if not (P/'art_source/Bruce_Sato/renders/v1_final/COMPLETE').exists():return .6
   path=A/'scripts/fit_seats_v2.py';exec(compile(path.read_text(encoding='utf-8'),str(path),'exec'),{'__name__':'__main__'});stage['i']=1;return .5
  if stage['i']==1:
   path=A/'scripts/review_final_v2.py';exec(compile(path.read_text(encoding='utf-8'),str(path),'exec'),{'__name__':'__main__'});stage['i']=2;return .6
  if (A/'renders/v2/ERROR.json').exists():raise RuntimeError((A/'renders/v2/ERROR.json').read_text())
  if not (A/'renders/v2/COMPLETE').exists():return .6
  (A/'final_reviews_v2_COMPLETE').write_text('V2 vehicle final views and static crew fit complete; inspect PNGs.');return None
 except Exception:
  (A/'vehicle_v2_final_pipeline_ERROR.json').write_text(json.dumps({'stage':stage['i'],'error':traceback.format_exc()}));return None
bpy.app.timers.register(advance,first_interval=.5);print('RHINO_V2_VEHICLE_REVIEW_AFTER_ACTIVE_CHARACTER_BATCH_QUEUED')
