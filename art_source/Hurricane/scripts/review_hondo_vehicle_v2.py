from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
hide=['HU_Body','HU_RunningGear','HU_Interior','HU_Weapons']
RENDER_JOB={'rig':'Hurricane_Control','rig_properties':['battle_mode','spare_eject'],'actors':{'HondoMacLean_Rig':['driving_pose','in_vehicle','mask_on']},'output_dir':str(P/'art_source/Hurricane/renders/v2_review'),'samples':20,'width':1200,'height':900,'device':'GPU','views':[
{'name':'01_road','frame':1,'properties':{},'object_states':{'HondoMacLean_Rig':{'properties':{'driving_pose':1,'in_vehicle':1,'mask_on':False}}},'camera':[8.1,-7.6,4.2],'target':[0,0,.85],'lens':52},
{'name':'02_battle','frame':151,'properties':{},'object_states':{'HondoMacLean_Rig':{'properties':{'driving_pose':1,'in_vehicle':1,'mask_on':True}}},'camera':[8,-8,5.1],'target':[0,0,1.55],'lens':49},
{'name':'03_hondo_standing','frame':1,'properties':{},'object_states':{'HondoMacLean_Rig':{'properties':{'driving_pose':0,'in_vehicle':0,'mask_on':False}}},'camera':[2.6,-3.1,1.9],'target':[0,0,.94],'lens':58,'hide_collections':hide},
{'name':'04_hondo_mask','frame':1,'properties':{},'object_states':{'HondoMacLean_Rig':{'properties':{'driving_pose':0,'in_vehicle':0,'mask_on':True}}},'camera':[2.6,-3.1,1.9],'target':[0,0,.94],'lens':58,'hide_collections':hide},
{'name':'05_gunner_close','frame':151,'properties':{},'object_states':{'HondoMacLean_Rig':{'properties':{'driving_pose':1,'in_vehicle':1,'mask_on':False}}},'camera':[3.2,-3.2,3.4],'target':[.1,0,2.6],'lens':55}
]}
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(encoding='utf-8'),'<review>','exec'))
