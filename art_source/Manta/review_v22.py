from pathlib import Path
p=Path('G:/DEV/mask-project-mayhem/art_source/Manta/review_v18.py').read_text().replace('renders/v18','renders/v22')
exec(compile(p,'<review_v22>','exec'))
