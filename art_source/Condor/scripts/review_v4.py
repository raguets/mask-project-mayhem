from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
code=(P/'art_source/Condor/scripts/review_assembly_v2.py').read_text().replace("v2_assembly","v4_review")
code=code.replace("exec(compile((P/", "RENDER_JOB['views'].extend([{'name':'road_rear','frame':1,'properties':{},'camera':[-4,-3,2.6],'target':[-.3,0,.8],'lens':50},{'name':'mask_close','frame':1,'properties':{},'camera':[1.6,-1.4,1.8],'target':[0,0,1.65],'lens':80,'hide_collections':['Condor_Vehicle'],'object_states':{'BradTurner_Rig':{'properties':{'driving_pose':0.,'mask_on':True,'in_vehicle':0.}}}}])\nexec(compile((P/")
exec(compile(code,'<v4review>','exec'))
