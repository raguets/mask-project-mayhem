from pathlib import Path
p=Path('G:/DEV/mask-project-mayhem/art_source/Manta/export_reopen_v5.py').read_text().replace('Manta_V5','Manta_V23').replace('standalone_validation_v5','standalone_validation_v23')
exec(compile(p,'<export_v23>','exec'))
