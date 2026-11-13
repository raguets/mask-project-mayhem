from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
exec(compile((P/'art_source/Condor/scripts/validate_clearance_v16.py').read_text().replace('v16','v19'),'<clearance_v19>','exec'))
