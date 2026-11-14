from pathlib import Path
p=Path('G:/DEV/mask-project-mayhem/art_source/Manta/validate_v4.py').read_text()
p=p.replace('validation_v4.json','validation_v6.json').replace("'version':4","'version':6")
p=p.replace("pairs=[", "pairs=[('MA_ReactorCassette','MA_RearLightPanel')]+[")
p=p.replace("'MA_CabinFloor']", "'MA_CabinFloor','MA_TtopGlass_1','MA_TtopGlass_-1']")
exec(compile(p,'<validation_v6>','exec'))
