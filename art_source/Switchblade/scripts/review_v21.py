from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
exec(compile((P/'art_source/Switchblade/scripts/review_v20.py').read_text().replace('v20_review','v21_review'),'<review_v21>','exec'))
