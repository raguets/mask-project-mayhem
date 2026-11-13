from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
code=(P/'art_source/Switchblade/scripts/review_assembly_v7.py').read_text().replace('v7_assembly','v10_assembly').replace("(0,-.01,14)","(0,-.01,18)")
exec(compile(code,'<review_v10>','exec'))
