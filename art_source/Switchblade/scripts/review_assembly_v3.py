from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
exec(compile((P/'art_source/Switchblade/scripts/review_assembly_v1.py').read_text().replace('v1_assembly','v3_assembly'),'<review_v3>','exec'))
