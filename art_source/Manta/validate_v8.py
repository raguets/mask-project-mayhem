from pathlib import Path
p=Path('G:/DEV/mask-project-mayhem/art_source/Manta/validate_v4.py').read_text()
p=p.replace('validation_v4.json','validation_v8.json').replace("'version':4","'version':8")
p=p.replace("pairs=[", "pairs=[('MA_ReactorCassette','MA_RearLightPanel')]+[")
exec(compile(p,'<validation_v8>','exec'))
