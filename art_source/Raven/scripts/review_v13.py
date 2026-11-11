from pathlib import Path
A=Path('G:/DEV/mask-project-mayhem/art_source/Raven')
exec(compile((A/'scripts/review_v12.py').read_text(encoding='utf-8').replace('renders/v12_review','renders/v13_review'),'<v13-review>','exec'))
