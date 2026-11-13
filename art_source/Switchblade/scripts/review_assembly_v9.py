from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
exec(compile((P/'art_source/Switchblade/scripts/review_assembly_v7.py').read_text().replace('v7_assembly','v9_assembly'),'<review_v9>','exec'))
