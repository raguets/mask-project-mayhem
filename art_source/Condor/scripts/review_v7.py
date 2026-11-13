from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
exec(compile((P/'art_source/Condor/scripts/review_v4.py').read_text().replace('v4_review','v7_review'),'<v7review>','exec'))
