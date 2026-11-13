from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');views=[]
for name,f,cam,target,lens in [('helicopter_front',1,(9,-11,6),(-.4,0,1.5),55),('helicopter_side',1,(0,-13,3.2),(-.4,0,1.5),55),('mid_transform',61,(9,-11,7),(-.4,0,1.5),55),('airplane_front',121,(9,-11,8),(-.4,0,1.6),55),('airplane_rear',121,(-10,-9,6),(-.4,0,1.6),55),('helicopter_top',1,(0,-.01,18),(-.4,0,1.5),55),('airplane_top',121,(0,-.01,18),(-.4,0,1.4),55),('early_opening',13,(-8,-9,6),(-.7,0,1.5),58)]:views.append({'name':name,'frame':f,'properties':{},'camera':cam,'target':target,'lens':lens})
RENDER_JOB={'rig':'Switchblade_Control','rig_properties':['transform','rotor_angle','canopy_open','hover_height'],'actors':{'MilesMayhem_Rig':['driving_pose','mask_on','in_vehicle']},'output_dir':str(P/'art_source/Switchblade/renders/v14_final'),'width':1200,'height':900,'samples':24,'device':'GPU','views':views}
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(),'<review>','exec'))
