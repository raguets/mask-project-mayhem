from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
RENDER_JOB={'rig':'BoulderHill_Control','rig_properties':['battle_mode','gate_open','thunderhawk_exit','rhino_exit'], 'output_dir':str(P/'docs/qa/boulder_v1'),'samples':24,'width':1400,'height':1000,'device':'GPU','views':[
{'name':'01_station','frame':1,'properties':{},'camera':[39,-48,30],'target':[1,0,5],'lens':47},
{'name':'02_defense','frame':181,'properties':{},'camera':[39,-48,30],'target':[1,0,5],'lens':47},
{'name':'03_gate_open','frame':211,'properties':{},'camera':[29,-35,16],'target':[2,-3,3.8],'lens':45},
{'name':'04_interior','frame':211,'properties':{},'camera':[23,2,46],'target':[0,16,0],'lens':41,'hide_collections':['BH_Rock'],'hide_objects':['BH_HangarCeiling']+['BH_HangarRoofBeam_'+str(y) for y in [2,9,16,23,30,37]]}
]}
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(encoding='utf-8'),'<review>','exec'))
