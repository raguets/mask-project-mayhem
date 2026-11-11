from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Raven'
source=(A/'scripts/review_v4.py').read_text(encoding='utf-8').split("exec(compile((P/'art_source/shared_tools")[0]
exec(compile(source,'<v6-review-config>','exec'))
RENDER_JOB['output_dir']=str(A/'renders/v6_review')
RENDER_JOB['views']=[v for v in RENDER_JOB['views'] if v['name'] not in ['05_calhoun_standing','06_calhoun_mask','07_calhoun_driving','08_calhoun_driving_mask']]
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(encoding='utf-8'),'<review>','exec'))
