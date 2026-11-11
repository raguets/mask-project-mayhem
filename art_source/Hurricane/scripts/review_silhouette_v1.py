from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
RENDER_JOB={'rig':'Hurricane_Control','rig_properties':['battle_mode','spare_eject'],'output_dir':str(P/'art_source/Hurricane/renders/v1_silhouette'),'samples':16,'width':1200,'height':800,'device':'GPU','views':[
{'name':'01_road_front','frame':1,'properties':{},'camera':[8.1,-7.6,4.2],'target':[0,0,.85],'lens':52},
{'name':'02_road_profile','frame':1,'properties':{},'camera':[.15,-10.5,2.8],'target':[0,0,.85],'lens':58},
{'name':'03_deployed_rear','frame':151,'properties':{},'camera':[-8,7.3,4.6],'target':[0,0,1.3],'lens':50}
]}
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(encoding='utf-8'),'<review>','exec'))
