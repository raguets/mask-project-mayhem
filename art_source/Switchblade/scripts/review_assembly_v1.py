from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Switchblade';views=[]
for name,f,cam,target,lens in [('helicopter_front',1,(9,-11,6),(-.4,0,1.5),55),('helicopter_side',1,(0,-13,3.2),(-.4,0,1.5),55),('mid_transform',61,(9,-11,7),(-.4,0,1.5),55),('airplane_front',121,(9,-11,8),(-.4,0,1.6),55),('airplane_rear',121,(-10,-9,6),(-.4,0,1.6),55)]:
 views.append({'name':name,'frame':f,'properties':{},'camera':cam,'target':target,'lens':lens})
for pose in [0.,1.]:
 for mask in [False,True]:views.append({'name':'miles_'+str(int(pose))+'_'+str(mask),'frame':1,'properties':{},'camera':(3,-3,1.9),'target':(0,0,1.0),'lens':62,'hide_collections':['Switchblade_Vehicle','Switchblade_Interior'],'object_states':{'MilesMayhem_Rig':{'properties':{'driving_pose':pose,'mask_on':mask,'in_vehicle':0.}}}})
views.append({'name':'cockpit_fit','frame':1,'properties':{'canopy_open':1.},'camera':(4,-4,4),'target':(.85,0,1.8),'lens':78})
views.append({'name':'miles_face','frame':1,'properties':{},'camera':(1.4,-1.7,1.85),'target':(.03,0,1.69),'lens':90,'hide_collections':['Switchblade_Vehicle','Switchblade_Interior'],'object_states':{'MilesMayhem_Rig':{'properties':{'driving_pose':0.,'mask_on':False,'in_vehicle':0.}}}})
RENDER_JOB={'rig':'Switchblade_Control','rig_properties':['transform','rotor_angle','canopy_open','hover_height'],'actors':{'MilesMayhem_Rig':['driving_pose','mask_on','in_vehicle']},'output_dir':str(A/'renders/v1_assembly'),'width':1200,'height':900,'samples':24,'device':'GPU','views':views}
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(),'<review>','exec'))
