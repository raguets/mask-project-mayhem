from pathlib import Path
p=Path('G:/DEV/mask-project-mayhem/art_source/Manta/validate_v10.py').read_text().replace('validation_v10.json','validation_v14.json').replace("'version':10","'version':14")
exec(compile(p,'<validation_v14>','exec'))
