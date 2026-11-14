from pathlib import Path
p=Path('G:/DEV/mask-project-mayhem/art_source/Manta/review_v14.py').read_text().replace('renders/v14','renders/v15')
exec(compile(p,'<review_v15>','exec'))
