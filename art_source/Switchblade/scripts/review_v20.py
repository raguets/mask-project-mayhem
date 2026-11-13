from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
code=(P/'art_source/Switchblade/scripts/review_v16.py').read_text().replace('v16_review','v20_review')
code=code.replace("RENDER_JOB={", "views.append({'name':'forewing_weapons','frame':121,'properties':{},'camera':(4,-4,2.8),'target':(1.25,0,1.5),'lens':75})\nviews.append({'name':'forewing_weapons_stored','frame':1,'properties':{},'camera':(4,-4,2.8),'target':(1.25,0,1.5),'lens':75})\nRENDER_JOB={")
exec(compile(code,'<review_v20>','exec'))
