from pathlib import Path
p=Path('G:/DEV/mask-project-mayhem/art_source/Manta/validate_v10.py').read_text().replace('validation_v10.json','validation_v12.json').replace("'version':10","'version':12")
exec(compile(p,'<validation_v12>','exec'))
