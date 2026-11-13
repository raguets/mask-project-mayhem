from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
exec(compile((P/'art_source/Switchblade/scripts/validate_motion_v19.py').read_text().replace('motion_validation_v19.json','motion_validation_v21.json'),'<validate_v21>','exec'))
