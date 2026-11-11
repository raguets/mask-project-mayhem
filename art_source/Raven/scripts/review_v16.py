from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Raven'
code=(A/'scripts/review_v15.py').read_text(encoding='utf-8');exec(code[:code.rindex('exec(compile(')])
RENDER_JOB['output_dir']=str(A/'renders/v16_review')
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(encoding='utf-8'),'<review>','exec'))
