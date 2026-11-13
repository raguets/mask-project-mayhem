from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');views=[]
for pose in [0.,1.]:
 views.append({'name':'viper_pose_'+str(int(pose)),'frame':1,'properties':{},'camera':(2.1,-2.6,1.8),'target':(.02,0,1.48),'lens':77,'hide_collections':['Switchblade_Vehicle','Switchblade_Interior'],'object_states':{'MilesMayhem_Rig':{'properties':{'driving_pose':pose,'mask_on':True,'in_vehicle':0.}}}})
RENDER_JOB={'rig':'Switchblade_Control','rig_properties':['transform','rotor_angle','canopy_open','hover_height'],'actors':{'MilesMayhem_Rig':['driving_pose','mask_on','in_vehicle']},'output_dir':str(P/'art_source/Switchblade/renders/v15_mask'),'width':1000,'height':1000,'samples':24,'device':'GPU','views':views}
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(),'<review>','exec'))
