from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Raven'
source=(A/'scripts/review_v4.py').read_text(encoding='utf-8').split("exec(compile((P/'art_source/shared_tools")[0]
exec(compile(source.replace('renders/v4_review','renders/v5_review'),'<v5-review-config>','exec'))
RENDER_JOB['output_dir']=str(A/'renders/v5_review')
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(encoding='utf-8'),'<review>','exec'))
