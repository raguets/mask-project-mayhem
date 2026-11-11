from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
RENDER_JOB={'rig':'BoulderHill_Control','rig_properties':['battle_mode','gate_open','thunderhawk_exit','rhino_exit'], 'output_dir':str(P/'docs/qa/boulder_v2'),'samples':20,'width':1300,'height':900,'device':'GPU','views':[
{'name':'01_station','frame':1,'properties':{},'camera':[37,-52,23],'target':[1,-1,5.7],'lens':49},
{'name':'02_defense','frame':211,'properties':{},'camera':[37,-52,28],'target':[1,0,5.4],'lens':47},
{'name':'03_thunderhawk_exit','frame':293,'properties':{},'camera':[25,-34,10.5],'target':[5,-7,3],'lens':45},
{'name':'04_rhino_exit','frame':490,'properties':{},'camera':[27,-34,11],'target':[6,-7,3.5],'lens':45},
{'name':'05_hangar_cutaway','frame':211,'properties':{},'camera':[29,-6,49],'target':[0,15,0],'lens':40,'hide_collections':['BH_Rock','BH_Turret'],'hide_objects':['BH_HangarCeiling']+['BH_HangarRoofBeam_'+str(y) for y in [2,9,16,23,30,37]]},
{'name':'06_facade_mechanisms','frame':181,'properties':{},'camera':[-22,-37,12],'target':[-5,-10,5],'lens':48},
{'name':'07_turret','frame':181,'properties':{},'camera':[15,-5,18],'target':[7,5.5,12.2],'lens':58}
]}
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(encoding='utf-8'),'<review>','exec'))
