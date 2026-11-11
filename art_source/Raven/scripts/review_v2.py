import json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Raven'
hidecar=['RV_Body','RV_RunningGear','RV_Interior','RV_Weapons']
def actor(d=1,a=1,m=False):return {'CalhounBurns_Rig':{'properties':{'driving_pose':d,'in_vehicle':a,'mask_on':m}}}
RENDER_JOB={'rig':'Raven_Control','rig_properties':['transform','hover_height','disc_launch'],'floor':'RV_ReviewFloor','actors':{'CalhounBurns_Rig':['driving_pose','in_vehicle','mask_on']},'output_dir':str(A/'renders/v2_review'),'samples':24,'width':1200,'height':900,'device':'GPU','views':[
{'name':'01_road_front','frame':1,'properties':{'hover_height':0},'object_states':actor(),'camera':[6,-6,3.0],'target':[0,0,.65],'lens':53},
{'name':'02_deployed_front','frame':151,'properties':{'hover_height':.6},'object_states':actor(m=True),'camera':[6,-6,4.0],'target':[0,0,1.0],'lens':51},
{'name':'03_road_rear','frame':1,'properties':{'hover_height':0},'object_states':actor(),'camera':[-6,6,2.6],'target':[-.2,0,.65],'lens':55},
{'name':'04_deployed_rear','frame':151,'properties':{'hover_height':.6},'object_states':actor(m=True),'camera':[-6,6,3.0],'target':[-.2,0,1.0],'lens':54},
{'name':'05_calhoun_standing','frame':1,'properties':{},'object_states':actor(0,0),'camera':[2.8,-3.7,1.95],'target':[0,0,.93],'lens':61,'hide_collections':hidecar},
{'name':'06_calhoun_mask','frame':1,'properties':{},'object_states':actor(0,0,True),'camera':[2.8,-3.7,1.95],'target':[0,0,.93],'lens':61,'hide_collections':hidecar},
{'name':'07_calhoun_driving','frame':1,'properties':{},'object_states':actor(1,0),'camera':[2.8,-3.7,1.5],'target':[0,0,.65],'lens':67,'hide_collections':hidecar},
{'name':'08_calhoun_driving_mask','frame':1,'properties':{},'object_states':actor(1,0,True),'camera':[2.8,-3.7,1.5],'target':[0,0,.65],'lens':67,'hide_collections':hidecar},
{'name':'09_mask_detail','frame':1,'properties':{},'object_states':actor(0,0,True),'camera':[1.0,-1.3,1.85],'target':[.02,0,1.69],'lens':74,'hide_collections':hidecar},
{'name':'10_cockpit_cutaway','frame':1,'properties':{},'object_states':actor(m=True),'camera':[2.3,3.0,1.9],'target':[-.15,.35,.68],'lens':65,'hide_objects':['RV_RoofTarga','RV_Windshield','RV_DoorWing_Glass_L','RV_DoorWing_Panel_L','RV_DoorWing_InnerSkin_L','RV_RearHatchGlass']},
{'name':'11_half_transform','frame':76,'properties':{'hover_height':.6},'object_states':actor(m=True),'camera':[5.7,-6.5,3.8],'target':[0,0,1.0],'lens':51},
{'name':'12_disc_launch','frame':151,'properties':{'hover_height':.6,'disc_launch':.25},'object_states':actor(m=True),'camera':[6.4,-6.2,3.4],'target':[.55,0,.95],'lens':51}
]}
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(encoding='utf-8'),'<review>','exec'))
