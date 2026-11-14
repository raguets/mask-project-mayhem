from pathlib import Path
p=Path('G:/DEV/mask-project-mayhem/art_source/Manta/validate_v4.py').read_text()
exec(compile(p.replace('validation_v4.json','validation_v5.json').replace("'version':4","'version':5"),'<validation_v5>','exec'))
