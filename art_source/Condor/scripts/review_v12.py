from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
exec(compile((P/'art_source/Condor/scripts/review_v8.py').read_text().replace('v8_review','v12_review'),'<review_v12>','exec'))
