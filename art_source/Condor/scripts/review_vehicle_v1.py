from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
RENDER_JOB={'rig':'Condor_Control','rig_properties':['transform','rotor_angle','forward_flight','hover_height'],'output_dir':str(P/'art_source/Condor/renders/v1_vehicle'),'width':1000,'height':800,'samples':20,'device':'GPU','views':[
{'name':'road_threequarter','frame':1,'properties':{},'camera':[3.8,-4.5,2.6],'target':[0,0,.72],'lens':55},
{'name':'flight_threequarter','frame':121,'properties':{},'camera':[3.8,-4.5,2.8],'target':[0,0,.85],'lens':48},
{'name':'flight_side','frame':121,'properties':{},'camera':[0,-6,1.8],'target':[0,0,.85],'lens':52},
{'name':'transition','frame':61,'properties':{},'camera':[3,-4,2.6],'target':[0,0,.85],'lens':48}]}
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(),'<review>','exec'))
