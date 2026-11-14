from pathlib import Path
p=Path('G:/DEV/mask-project-mayhem/art_source/Manta/validate_v8.py').read_text().replace('validation_v8.json','validation_v9.json')
p=Path('G:/DEV/mask-project-mayhem/art_source/Manta/validate_v4.py').read_text().replace('validation_v4.json','validation_v9.json').replace("'version':4","'version':9").replace("pairs=[", "pairs=[('MA_ReactorCassette','MA_RearLightPanel')]+[")
exec(compile(p,'<validation_v9>','exec'))
