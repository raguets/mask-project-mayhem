from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
code=(P/'art_source/Condor/scripts/export_reopen_v7.py').read_text().replace('v7','v20').replace('V7','V20').replace('BradTurner_V1.blend','BradTurner_V2.blend').replace('HocusPocus_V1.blend','HocusPocus_V2.blend')
exec(compile(code,'<export_v20>','exec'))
