from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
code=(P/'art_source/Condor/scripts/review_v16.py').read_text().replace('v16_review','v20_review')
code=code.replace("RENDER_JOB={", "views[3]['floor_offset']=[0,0,-0.22]\nRENDER_JOB={")
exec(compile(code,'<review_v20>','exec'))
