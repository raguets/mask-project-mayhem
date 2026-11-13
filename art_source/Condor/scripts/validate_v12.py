from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
exec(compile((P/'art_source/Condor/scripts/validate_v7.py').read_text().replace('v7','v12').replace('V7','V12'),'<validate_v12>','exec'))
