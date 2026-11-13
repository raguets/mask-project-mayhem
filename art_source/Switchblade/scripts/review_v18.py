from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
exec(compile((P/'art_source/Switchblade/scripts/review_v16.py').read_text().replace('v16_review','v18_review'),'<review_v18>','exec'))
