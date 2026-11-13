from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
code=(P/'art_source/Switchblade/scripts/validate_motion_v2.py').read_text().replace('motion_validation_v2.json','motion_validation_v10.json')
exec(compile(code,'<validate_v10>','exec'))
