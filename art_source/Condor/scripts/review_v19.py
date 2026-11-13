from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
exec(compile((P/'art_source/Condor/scripts/review_v16.py').read_text().replace('v16_review','v19_review'),'<review_v19>','exec'))
