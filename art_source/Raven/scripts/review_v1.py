import json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Raven'
hidecar=['RV_Body','RV_RunningGear','RV_Interior','RV_Weapons']
def char(p=0,m=False):return {'CalhounBurns_Rig':{'properties':{'driving_pose':p,'mask_on':m},'location':[0,0,0]}}
RENDER_JOB={'rig':'Raven_Control','rig_properties':['transform','hover_height','disc_launch'],'floor':'RV_ReviewFloor','actors':{'CalhounBurns_Rig':['driving_pose','mask_on']},'output_dir':str(A/'renders/v1_review'),'samples':24,'width':1200,'height':900,'device':json.loads((A/'pose_inventory_v1.json').read_text())['render_device'],'views':[
{'name':'01_road_front','frame':1,'properties':{'hover_height':0},'camera':[6,-6,3.0],'target':[0,0,.65],'lens':53,'hide_collections':['CB_Character','CB_Mask']},
{'name':'02_deployed_front','frame':151,'properties':{'hover_height':.6},'camera':[6,-6,4.0],'target':[0,0,1.0],'lens':51,'hide_collections':['CB_Character','CB_Mask']},
{'name':'03_road_rear','frame':1,'properties':{'hover_height':0},'camera':[-6,6,2.6],'target':[-.2,0,.65],'lens':55,'hide_collections':['CB_Character','CB_Mask']},
{'name':'04_deployed_rear','frame':151,'properties':{'hover_height':.6},'camera':[-6,6,3.0],'target':[-.2,0,1.0],'lens':54,'hide_collections':['CB_Character','CB_Mask']},
{'name':'05_calhoun_standing','frame':1,'properties':{'hover_height':0},'object_states':char(),'camera':[2.8,-3.7,1.95],'target':[0,0,.93],'lens':61,'hide_collections':hidecar},
{'name':'06_calhoun_mask','frame':1,'properties':{'hover_height':0},'object_states':char(m=True),'camera':[2.8,-3.7,1.95],'target':[0,0,.93],'lens':61,'hide_collections':hidecar},
{'name':'07_face','frame':1,'properties':{},'object_states':char(),'camera':[1.2,-1.35,1.9],'target':[0,0,1.68],'lens':70,'hide_collections':hidecar},
{'name':'08_mask_profile','frame':1,'properties':{},'object_states':char(m=True),'camera':[.9,-1.5,1.85],'target':[.02,0,1.69],'lens':74,'hide_collections':hidecar}
]}
exec(compile((P/'.agents/skills/mask-asset-production/scripts/render_review_queue.py').read_text(encoding='utf-8'),'<review>','exec'))
