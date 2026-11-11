from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Raven'
source=(A/'scripts/review_v2.py').read_text(encoding='utf-8').split('exec(compile')[0]
exec(compile(source.replace('renders/v2_review','renders/v3_review'),'<v3-review-config>','exec'))
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(encoding='utf-8'),'<review>','exec'))
