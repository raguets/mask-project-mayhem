from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
RENDER_JOB={'rig':'BoulderHill_Control','rig_properties':['battle_mode','gate_open','thunderhawk_exit','rhino_exit'],'output_dir':str(P/'art_source/Boulder_Hill/renders/v5'),'samples':20,'width':1300,'height':900,'device':'GPU','views':[
{'name':'01_station_mountain','frame':1,'properties':{},'camera':[63,-82,43],'target':[0,17,12],'lens':46},
{'name':'02_defense','frame':211,'properties':{},'camera':[33,-43,20],'target':[0,-2,7],'lens':43}
]}
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(encoding='utf-8'),'<review>','exec'))
