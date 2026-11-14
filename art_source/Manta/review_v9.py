from pathlib import Path
p=Path('G:/DEV/mask-project-mayhem/art_source/Manta/review_v3.py').read_text().replace('renders/v3','renders/v9').replace('(6,-7,5.7)','(8,-9,6)').replace('(-6,-7,4.8)','(-8,-9,5.5)').replace('(0,-.01,12)','(0,-.01,13)').replace('(6,-6,5)','(8,-9,6)')
exec(compile(p,'<review_v9>','exec'))
