from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
views=[]
for n,f,c in [('road_front',1,(6,-6,3.8)),('road_rear',1,(-6,-6,3.5)),('road_side',1,(0,-8,2.0)),('phase_50',61,(6,-6,5)),('flight_front',121,(6,-7,5.7)),('flight_rear',121,(-6,-7,4.8)),('flight_top',121,(0,-.01,11))]:
 views.append({'name':n,'frame':f,'camera':c,'target':(0,0,.6),'lens':53,'properties':{}})
RENDER_JOB={'rig':'Manta_Control','rig_properties':['transform','door_open'],'output_dir':str(P/'art_source/Manta/renders/v1_vehicle'),'width':1200,'height':900,'samples':24,'device':'GPU','views':views}
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(),'<review>','exec'))
