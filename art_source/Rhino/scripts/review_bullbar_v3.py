import bpy
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
assert (P/'art_source/Rhino/bullbar_validation_v3_COMPLETE').exists()
RENDER_JOB={'output_dir':str(P/'art_source/Rhino/renders/v3'),'rig':'Rhino_Control','rig_properties':['battle_mode','bullbar'],'floor':'Review_Floor','width':1100,'height':900,'samples':20,'device':'GPU','reference':'Images de reference/rhino/rhino pare buffle.jpg','views':[
 {'name':'bullbar_front_road','camera':[9.4,0,1.85],'target':[4.7,0,1.70],'lens':65,'frame':1,'properties':{}},
 {'name':'bullbar_three_quarter','camera':[8.0,3.0,3.3],'target':[4.70,0,1.65],'lens':65,'frame':1,'properties':{}},
 {'name':'bullbar_deployed','camera':[8.5,3.1,3.25],'target':[5.10,0,1.65],'lens':65,'frame':151,'properties':{}},
 {'name':'road_front','camera':[12,11,7],'target':[.3,0,2],'lens':52,'frame':1,'properties':{}},
 {'name':'transformed','camera':[13,16,10],'target':[-1.9,-.9,1.9],'lens':47,'frame':151,'properties':{}}]}
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(encoding='utf-8'),'<render_review_queue>','exec'))
