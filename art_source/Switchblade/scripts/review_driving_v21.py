from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');views=[]
for m in [False,True]:views.append({'name':'driving_'+str(m),'frame':1,'properties':{},'camera':(2.8,-3,1.8),'target':(.3,0,.95),'lens':62,'hide_collections':['Switchblade_Vehicle','Switchblade_Interior'],'object_states':{'MilesMayhem_Rig':{'properties':{'driving_pose':1.,'mask_on':m,'in_vehicle':0.}}}})
views.append({'name':'foot_controls_cutaway','frame':1,'properties':{'canopy_open':1.},'camera':(2.6,-2.8,2.5),'target':(.90,0,1.0),'lens':85,'hide_objects':['SB_InstrumentConsole','SB_NoseWedge','SB_CabinSideWall_-1','SB_FixedCockpitChine_-1','SB_FrontWingCannonPod_-1']})
RENDER_JOB={'rig':'Switchblade_Control','rig_properties':['transform','rotor_angle','canopy_open','hover_height'],'actors':{'MilesMayhem_Rig':['driving_pose','mask_on','in_vehicle']},'output_dir':str(P/'art_source/Switchblade/renders/v21_fit'),'width':1100,'height':900,'samples':24,'device':'GPU','views':views}
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(),'<review>','exec'))
