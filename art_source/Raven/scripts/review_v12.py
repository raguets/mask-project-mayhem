from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Raven'
def actor(d=1,a=1,m=False):return {'CalhounBurns_Rig':{'properties':{'driving_pose':d,'in_vehicle':a,'mask_on':m}}}
RENDER_JOB={'rig':'Raven_Control','rig_properties':['transform','hover_height','disc_launch'],'floor':'RV_ReviewFloor','actors':{'CalhounBurns_Rig':['driving_pose','in_vehicle','mask_on']},'output_dir':str(A/'renders/v12_review'),'samples':28,'width':1280,'height':960,'device':'GPU','views':[
{'name':'01_road_front','frame':1,'properties':{},'object_states':actor(),'camera':[6,-6,3.0],'target':[0,0,.65],'lens':53},
{'name':'02_road_rear','frame':1,'properties':{},'object_states':actor(),'camera':[-6,6,2.6],'target':[-.2,0,.65],'lens':55},
{'name':'03_deployed_front','frame':151,'properties':{'hover_height':.6},'object_states':actor(m=True),'camera':[6,-6,4.0],'target':[0,0,1.0],'lens':51},
{'name':'04_deployed_rear','frame':151,'properties':{'hover_height':.6},'object_states':actor(m=True),'camera':[-6,6,3.0],'target':[-.2,0,1.0],'lens':54},
{'name':'05_hood_flush','frame':1,'properties':{},'object_states':actor(),'camera':[4.3,-2.8,2.6],'target':[1.0,0,.70],'lens':65},
{'name':'06_canopy_flow','frame':1,'properties':{},'object_states':actor(),'camera':[1.6,-3.2,2.1],'target':[-.35,0,1.0],'lens':60},
{'name':'07_reactor_cassette','frame':151,'properties':{'hover_height':.6},'object_states':actor(m=True),'camera':[-4.3,2.6,2.2],'target':[-1.95,0,1.37],'lens':72},
{'name':'08_wider_rim_guns','frame':151,'properties':{'hover_height':.6},'object_states':actor(m=True),'camera':[2.8,-3.6,3.2],'target':[1.1,-.4,1.45],'lens':75},
{'name':'09_front_roll','frame':61,'properties':{'hover_height':.6},'object_states':actor(m=True),'camera':[5.7,-6.5,3.8],'target':[0,0,1.0],'lens':51},
{'name':'10_secondary_wheels','frame':106,'properties':{'hover_height':.6},'object_states':actor(m=True),'camera':[5.7,-6.5,3.8],'target':[0,0,1.0],'lens':51},
{'name':'11_shortened_footwell','frame':1,'properties':{},'object_states':actor(m=True),'camera':[2.3,3.0,1.9],'target':[-.05,.35,.57],'lens':65,'hide_objects':['RV_RoofTarga','RV_Windshield','RV_DoorWing_Glass_L','RV_DoorWing_Panel_L','RV_DoorWing_InnerSkin_L','RV_DoorPanelReturns_L','RV_RearHatchGlass']},
{'name':'12_seated_mask','frame':1,'properties':{},'object_states':actor(1,0,True),'camera':[2.8,-3.7,1.5],'target':[0,0,.65],'lens':67,'hide_collections':['RV_Body','RV_RunningGear','RV_Interior','RV_Weapons']},
{'name':'13_seated_unmasked','frame':1,'properties':{},'object_states':actor(1,0,False),'camera':[2.8,-3.7,1.5],'target':[0,0,.65],'lens':67,'hide_collections':['RV_Body','RV_RunningGear','RV_Interior','RV_Weapons']}
]}
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(encoding='utf-8'),'<review>','exec'))
