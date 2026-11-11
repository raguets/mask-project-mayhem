from pathlib import Path
A=Path('G:/DEV/mask-project-mayhem/art_source/Raven')
exec(compile((A/'scripts/review_v10.py').read_text(encoding='utf-8').replace('renders/v10_review','renders/v11_review'),'<review-v11>','exec'))
