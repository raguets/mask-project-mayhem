from pathlib import Path
p=Path('G:/DEV/mask-project-mayhem/art_source/Manta/validate_full_v20.py').read_text().replace('validation_full_v20.json','validation_full_v24.json').replace("'version':20","'version':23")
exec(compile(p,'<full_validation_v24>','exec'))
