from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');views=[]
for name,frame,cam,target,lens in [('road_side',1,[-.2,-6,1.6],[-.2,0,.85],48),('road_rear',1,[-3.5,-3,2.2],[-.3,0,.8],52),('support_first',43,[-3,-4,2.4],[-.3,0,.9],48),('wheel_mid',79,[-3,-4,2.4],[-.3,0,.9],48),('flight',121,[3.6,-4,2.6],[-.2,0,.9],48),('skid_underseat',121,[2,-3,.75],[-.17,0,.35],70)]:views.append({'name':name,'frame':frame,'properties':{},'camera':cam,'target':target,'lens':lens})
for pose in [0.,1.]:
 for mask in [False,True]:views.append({'name':'brad_'+str(int(pose))+'_'+str(mask),'frame':1,'properties':{},'camera':[3,-3,1.8],'target':[0,0,.95],'lens':58,'hide_collections':['Condor_Vehicle'],'object_states':{'BradTurner_Rig':{'properties':{'driving_pose':pose,'mask_on':mask,'in_vehicle':0.}}}})
views.append({'name':'mask_side','frame':1,'properties':{},'camera':[-.4,-2,1.75],'target':[0,0,1.65],'lens':88,'hide_collections':['Condor_Vehicle'],'object_states':{'BradTurner_Rig':{'properties':{'driving_pose':0.,'mask_on':True,'in_vehicle':0.}}}})
RENDER_JOB={'rig':'Condor_Control','rig_properties':['transform','rotor_angle','forward_flight','hover_height'],'actors':{'BradTurner_Rig':['driving_pose','mask_on','in_vehicle']},'output_dir':str(P/'art_source/Condor/renders/v16_review'),'width':1100,'height':900,'samples':24,'device':'GPU','views':views}
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(),'<review>','exec'))
