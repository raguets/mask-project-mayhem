import json,bpy
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');code=REVIEW_CHARACTER
rig='AlexSector_Rig' if code=='AS' else 'BruceSato_Rig';other='BS' if code=='AS' else 'AS'
hidden=['Rhino_Truck','Rhino_RearVehicle','Rhino_Interior',other+'_Character',other+'_Mask']
RENDER_JOB={'output_dir':str(P/('art_source/Alex_Sector' if code=='AS' else 'art_source/Bruce_Sato')/'renders/v1_final'),'rig':rig,'rig_properties':['driving_pose','mask_on'],'floor':'Review_Floor','samples':24,'width':900,'height':1000,'device':'GPU','views':[]}
for name,cam,target,lens,pose,mask in [
 ('standing',(3.4,2.9,2.0),(0,0,.94),65,0,False),
 ('portrait',(.88,.49,1.69),(.01,0,1.645),78,0,False),
 ('mask_front',(.91,.06,1.68),(.01,0,1.635),78,0,True),
 ('mask_profile',(.25,.89,1.69),(.01,0,1.64),78,0,True),
 ('seated',(2.6,2.7,1.7),(0,0,.65),62,1,False),
 ('seated_mask',(2.6,2.7,1.7),(0,0,.65),62,1,True)]:
 RENDER_JOB['views'].append({'name':name,'camera':cam,'target':target,'lens':lens,'frame':1,'properties':{'driving_pose':pose,'mask_on':mask},'rig_location':[0,0,0],'hide_collections':hidden})
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(encoding='utf-8'),'<render_review_queue>','exec'))
