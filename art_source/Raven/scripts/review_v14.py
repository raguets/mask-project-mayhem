from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Raven'
exec((A/'scripts/review_v12.py').read_text(encoding='utf-8').split("exec(compile((P/'art_source/shared_tools")[0])
RENDER_JOB['output_dir']=str(A/'renders/v14_review')
RENDER_JOB['views']=[RENDER_JOB['views'][i] for i in [0,1,2,3,5,6,10,11,12]]+[
{'name':'14_roof_thirds_top','frame':1,'properties':{},'object_states':actor(),'camera':[.8,-.15,6.8],'target':[-.45,0,.72],'lens':60},
{'name':'15_dark_hatch_and_pillars','frame':1,'properties':{},'object_states':actor(),'camera':[-3.7,-3.5,2.7],'target':[-.8,0,.9],'lens':65},
{'name':'16_roof_winglets','frame':151,'properties':{'hover_height':.6},'object_states':actor(m=True),'camera':[1.6,-4.8,3.6],'target':[-.35,0,1.0],'lens':58}]
RENDER_JOB['views'][6]['hide_objects']+=['RV_DoorRoofWing_L','RV_DoorRoofWing_R','RV_BlackRearDoorPillar_L','RV_B_Pillar_L']
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(encoding='utf-8'),'<review>','exec'))
