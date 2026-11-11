from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');hide=['HU_Body','HU_RunningGear','HU_Interior','HU_Weapons']
def actor(d=1,a=1,m=False):return {'HondoMacLean_Rig':{'properties':{'driving_pose':d,'in_vehicle':a,'mask_on':m}}}
RENDER_JOB={'rig':'Hurricane_Control','rig_properties':['battle_mode','spare_eject'],'actors':{'HondoMacLean_Rig':['driving_pose','in_vehicle','mask_on']},'output_dir':str(P/'art_source/Hurricane/renders/v6_review'),'samples':24,'width':1280,'height':960,'device':'GPU','views':[
{'name':'01_road','frame':1,'properties':{},'object_states':actor(),'camera':[8.1,-7.6,4.2],'target':[0,0,.85],'lens':52},
{'name':'02_battle','frame':151,'properties':{},'object_states':actor(m=True),'camera':[8,-8,5.1],'target':[0,0,1.45],'lens':49},
{'name':'03_profile','frame':151,'properties':{},'object_states':actor(),'camera':[.15,-11,2.9],'target':[0,0,1.4],'lens':54},
{'name':'04_rear_eject','frame':191,'properties':{},'object_states':actor(m=True),'camera':[-9,7,4.3],'target':[-1.1,0,1.25],'lens':48},
{'name':'05_hondo_stand','frame':1,'properties':{},'object_states':actor(d=0,a=0),'camera':[3,-3.6,2.0],'target':[0,0,.91],'lens':58,'hide_collections':hide},
{'name':'06_hondo_stand_mask','frame':1,'properties':{},'object_states':actor(d=0,a=0,m=True),'camera':[3,-3.6,2.0],'target':[0,0,.91],'lens':58,'hide_collections':hide},
{'name':'07_hondo_seated','frame':1,'properties':{},'object_states':actor(a=0),'camera':[2.8,-3,1.65],'target':[.0,0,.62],'lens':58,'hide_collections':hide},
{'name':'08_hondo_seated_mask','frame':1,'properties':{},'object_states':actor(a=0,m=True),'camera':[2.8,-3,1.65],'target':[.0,0,.62],'lens':58,'hide_collections':hide},
{'name':'09_gunner','frame':151,'properties':{},'object_states':actor(),'camera':[3.3,-3.5,3.7],'target':[.1,0,2.5],'lens':55},
{'name':'10_gunner_mask','frame':151,'properties':{},'object_states':actor(m=True),'camera':[-2.3,-3.4,3.5],'target':[.1,0,2.5],'lens':55},
{'name':'11_chassis','frame':151,'properties':{},'object_states':actor(m=True),'camera':[.1,-7.3,1.4],'target':[0,0,.6],'lens':65},
{'name':'12_right_cannon','frame':151,'properties':{},'object_states':actor(m=True),'camera':[4.2,-4.8,2.8],'target':[1,-.25,1.4],'lens':62}
]}
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(encoding='utf-8'),'<review>','exec'))
