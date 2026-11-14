from pathlib import Path
p=Path('G:/DEV/mask-project-mayhem/art_source/Manta/export_reopen_v5.py').read_text().replace('Manta_V5','Manta_V24').replace('standalone_validation_v5','standalone_validation_v24')
p=p.replace('VanessaWarfield_V1.blend','VanessaWarfield_V2.blend').replace('Whip_V1.blend','Whip_V2.blend')
exec(compile(p,'<export_v24>','exec'))
