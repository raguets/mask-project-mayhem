from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
exec(compile((P/'art_source/Condor/scripts/review_v8.py').read_text().replace('v8_review','v13_review'),'<review_v13>','exec'))
