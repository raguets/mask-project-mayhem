import json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
RENDER_JOB={'output_dir':str(P/'art_source/Rhino/renders/v1_vehicle'),'rig':'Rhino_Control','rig_properties':['battle_mode','rear_detach','bullbar','cannons','rear_open','launcher_up'],'floor':'Review_Floor','samples':24,'width':1200,'height':850,'device':'GPU','views':[]}
for name,cam,target,lens,frame in [
 ('road_front',(12,11,7),(.3,0,2),52,1),
 ('road_profile',(0,16,6),(.3,0,2),54,1),
 ('road_rear',(-10,10,7),(0,0,2),52,1),
 ('transformed',(12,16,11),(-1.9,-.9,1.9),46,151),
 ('transformed_rear',(-13,12,10),(-1.9,-.9,1.9),48,151)]:
 RENDER_JOB['views'].append({'name':name,'camera':cam,'target':target,'lens':lens,'frame':frame,'properties':{}})
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(encoding='utf-8'),'<render_review_queue>','exec'))
