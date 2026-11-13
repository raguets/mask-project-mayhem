from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
exec(compile((P/'art_source/Switchblade/scripts/review_assembly_v12.py').read_text().replace('v12_assembly','v13_assembly'),'<review_v13>','exec'))
