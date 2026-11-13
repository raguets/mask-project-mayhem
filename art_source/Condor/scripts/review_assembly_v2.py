from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');views=[]
for n,f,cam in [('road',1,[3.8,-4.5,2.6]),('flight',121,[3.8,-4.5,2.8]),('flight_side',121,[0,-6,1.8]),('transition',61,[3,-4,2.6])]:views.append({'name':n,'frame':f,'properties':{},'camera':cam,'target':[0,0,.85],'lens':48})
for mask in [False,True]:views.append({'name':'brad_standing_'+str(mask),'frame':1,'properties':{},'camera':[3,-3,1.7],'target':[0,0,.94],'lens':65,'hide_collections':['Condor_Vehicle'],'object_states':{'BradTurner_Rig':{'properties':{'driving_pose':0.,'mask_on':mask,'in_vehicle':0.}}}})
views.append({'name':'riding_face','frame':1,'properties':{},'camera':[2.9,-3.5,2.3],'target':[0,0,1.02],'lens':58,'object_states':{'BradTurner_Rig':{'properties':{'mask_on':False}}}})
RENDER_JOB={'rig':'Condor_Control','rig_properties':['transform','rotor_angle','forward_flight','hover_height'],'actors':{'BradTurner_Rig':['driving_pose','mask_on','in_vehicle']},'output_dir':str(P/'art_source/Condor/renders/v2_assembly'),'width':1100,'height':900,'samples':24,'device':'GPU','views':views}
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(),'<review>','exec'))
