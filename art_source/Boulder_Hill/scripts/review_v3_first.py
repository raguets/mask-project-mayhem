from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
RENDER_JOB={'rig':'BoulderHill_Control','rig_properties':['battle_mode','gate_open','thunderhawk_exit','rhino_exit'], 'output_dir':str(P/'docs/qa/boulder_v3_first'),'samples':16,'width':1250,'height':900,'device':'GPU','views':[
{'name':'01_station_mountain','frame':1,'properties':{},'camera':[72,-95,56],'target':[0,28,16],'lens':45},
{'name':'02_defense_prism','frame':211,'properties':{},'camera':[34,-43,19],'target':[0,-3,7],'lens':43},
{'name':'03_prism_halfway','frame':65,'properties':{},'camera':[-19,-29,11],'target':[-5,-9,3],'lens':47}
]}
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(encoding='utf-8'),'<review>','exec'))
