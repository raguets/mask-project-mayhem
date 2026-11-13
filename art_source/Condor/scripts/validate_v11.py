from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
exec(compile((P/'art_source/Condor/scripts/validate_v7.py').read_text().replace('v7','v11').replace('V7','V11'),'<validate_v11>','exec'))
