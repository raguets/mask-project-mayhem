from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
views=[]
for n,p,m,c in [('standing',0.,False,(2.9,-3.4,2.0)),('standing_mask',0.,True,(2.9,-3.4,2.0)),('standing_profile',0.,False,(.1,-4,1.8)),('driving',1.,False,(2.3,-3,2.0)),('driving_mask',1.,True,(2.3,-3,2.0))]:
 views.append({'name':n,'frame':1,'properties':{'driving_pose':p,'mask_on':m,'in_vehicle':p},'camera':c,'target':(-.3 if p else 0,-.37 if p else 0,.95),'lens':65,'hide_collections':['Manta_Vehicle','Manta_Interior'] if not p else []})
for n,f,c in [('road_front',1,(6,-6,3.8)),('phase_50',61,(6,-6,5)),('flight_front',121,(6,-7,5.7)),('flight_rear',121,(-6,-7,4.8)),('flight_top',121,(0,-.01,12))]:
 views.append({'name':n,'frame':f,'camera':c,'target':(0,0,.6),'lens':53,'properties':{'driving_pose':1.,'in_vehicle':1.,'mask_on':True}})
RENDER_JOB={'rig':'VanessaWarfield_Rig','rig_properties':['driving_pose','mask_on','in_vehicle'],'output_dir':str(P/'art_source/Manta/renders/v3'),'width':1200,'height':1000,'samples':24,'device':'GPU','views':views}
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(),'<review>','exec'))
