from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');views=[]
for drive in [False,True]:
 for mask in [False,True]:
  views.append({'name':('driving' if drive else 'standing')+('_whip' if mask else '_face'),'frame':1,
   'camera':(1.5,3,2) if drive else (3,4,1.8),'target':(-.25,.37,.85) if drive else (0,0,.90),'lens':65,
   'hide_collections':[] if drive else ['Manta_Vehicle','Manta_Interior'],
   'properties':{'driving_pose':float(drive),'in_vehicle':float(drive),'mask_on':mask}})
RENDER_JOB={'rig':'VanessaWarfield_Rig','rig_properties':['driving_pose','mask_on','in_vehicle'],'output_dir':str(P/'art_source/Manta/renders/v24_character'),'width':900,'height':1000,'samples':20,'views':views}
exec(compile((P/'art_source/Manta/robust_review_queue.py').read_text(),'<character-review>','exec'))
