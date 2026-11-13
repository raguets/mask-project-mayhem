from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
exec(compile((P/'art_source/Condor/scripts/export_reopen_v7.py').read_text().replace('v7','v8').replace('V7','V8'),'<export_v8>','exec'))
