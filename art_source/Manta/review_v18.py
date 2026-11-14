from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');views=[]
for n,f,c,target,lens in [
 ('road_front_left',1,(6,6,3.5),(0,0,.64),53),('road_rear_left',1,(-6,6,3.3),(0,0,.64),53),('road_side_left',1,(0,8,1.7),(0,0,.64),53),('windshield_front',1,(6,0,2.0),(.2,0,1.0),75),('road_hood_detail',1,(4.8,3,2.6),(1.25,0,.62),68),('phase_50',61,(8,9,6),(0,0,.64),53),('phase_90_missiles',109,(4.7,3,3),(1.3,0,.7),65),('flight_front_left',121,(8,9,6),(0,0,.64),53),('flight_rear_left',121,(-8,9,5.5),(0,0,.64),53),('flight_top',121,(0,-.01,16),(0,0,.64),53),('driving_left',1,(1.5,3,2),(-.25,.37,.85),70)]:
 views.append({'name':n,'frame':f,'camera':c,'target':target,'lens':lens,'properties':{'driving_pose':1.,'in_vehicle':1.,'mask_on':False}})
RENDER_JOB={'rig':'VanessaWarfield_Rig','rig_properties':['driving_pose','mask_on','in_vehicle'],'output_dir':str(P/'art_source/Manta/renders/v18'),'width':1200,'height':900,'samples':20,'views':views}
exec(compile((P/'art_source/Manta/robust_review_queue.py').read_text(),'<verified_camera_review>','exec'))
