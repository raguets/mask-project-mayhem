from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
exec(compile((P/'art_source/Switchblade/scripts/validate_motion_v2.py').read_text().replace('motion_validation_v2.json','motion_validation_v7.json'),'<validate_v7>','exec'))
