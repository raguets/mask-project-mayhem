from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
code=(P/'art_source/Switchblade/scripts/review_assembly_v1.py').read_text().replace('v1_assembly','v7_assembly').replace("'lens':62","'lens':56").replace("'target':(0,0,1.0)","'target':(0,0,.94)")
code=code.replace("RENDER_JOB={", "views.append({'name':'helicopter_top','frame':1,'properties':{},'camera':(0,-.01,14),'target':(-.4,0,1.5),'lens':55})\nviews.append({'name':'early_opening','frame':13,'properties':{},'camera':(-8,-9,6),'target':(-.7,0,1.5),'lens':58})\nRENDER_JOB={")
exec(compile(code,'<review_v7>','exec'))
