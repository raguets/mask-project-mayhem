from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
RENDER_JOB={'rig':'BoulderHill_Control','rig_properties':['battle_mode','gate_open','thunderhawk_exit','rhino_exit'],'output_dir':str(P/'art_source/Boulder_Hill/renders/v4'),'samples':20,'width':1300,'height':900,'device':'GPU','views':[
{'name':'01_station_mountain','frame':1,'properties':{},'camera':[63,-82,43],'target':[0,17,12],'lens':46},
{'name':'02_defense','frame':211,'properties':{},'camera':[33,-43,20],'target':[0,-2,7],'lens':43},
{'name':'03_prism_halfway','frame':65,'properties':{},'camera':[-20,-29,12],'target':[-5,-9,3],'lens':47},
{'name':'04_thunderhawk_exit','frame':285,'properties':{},'camera':[24,-31,10.5],'target':[5,-7,3],'lens':45},
{'name':'05_rhino_exit','frame':510,'properties':{},'camera':[24,-31,10.5],'target':[5,-7,3.5],'lens':45},
{'name':'06_hangar_cutaway','frame':211,'properties':{},'camera':[29,-6,49],'target':[0,15,0],'lens':40,'hide_collections':['BH_Rock','BH_Turret'],'hide_objects':['BH_HangarCeiling']+['BH_HangarRoofBeam_'+str(y) for y in [2,9,16,23,30,37]]},
{'name':'07_turret_integrated','frame':181,'properties':{},'camera':[18,-5,19],'target':[7,5.5,11.8],'lens':55},
{'name':'08_left_facade','frame':181,'properties':{},'camera':[-24,-32,12],'target':[-5,-7,5.3],'lens':44}
]}
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(encoding='utf-8'),'<review>','exec'))
