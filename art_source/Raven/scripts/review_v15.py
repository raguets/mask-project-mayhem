from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Raven'
code=(A/'scripts/review_v14.py').read_text(encoding='utf-8')
exec(code[:code.rindex('exec(compile(')])
RENDER_JOB['output_dir']=str(A/'renders/v15_review')
RENDER_JOB['views']=[v for v in RENDER_JOB['views'] if v['name'] in ['01_road_front','02_road_rear','03_deployed_front','04_deployed_rear','06_canopy_flow','14_roof_thirds_top','15_dark_hatch_and_pillars','16_roof_winglets']]
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(encoding='utf-8'),'<review>','exec'))
