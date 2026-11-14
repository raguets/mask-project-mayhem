from pathlib import Path
p=Path('G:/DEV/mask-project-mayhem/art_source/Manta/review_v3.py').read_text()
p=p.replace('renders/v3','renders/v6').replace('(6,-7,5.7)','(9,-11,7)').replace('(-6,-7,4.8)','(-9,-11,6)').replace('(0,-.01,12)','(0,-.01,15)').replace('(6,-6,5)','(9,-10,6)')
exec(compile(p,'<review_v6>','exec'))
