from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
code=(P/'art_source/Switchblade/scripts/review_assembly_v1.py').read_text().replace('v1_assembly','v6_assembly').replace("'lens':62","'lens':56").replace("'target':(0,0,1.0)","'target':(0,0,.94)")
exec(compile(code,'<review_v6>','exec'))
