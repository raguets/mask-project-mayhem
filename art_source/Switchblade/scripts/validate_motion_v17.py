from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
code=(P/'art_source/Switchblade/scripts/validate_motion_v2.py').read_text().replace('motion_validation_v2.json','motion_validation_v17.json')
code=code.replace("fixed=['SB_FixedTailFuselage'", "fixed=['SB_MetalAirIntake_-1','SB_MetalAirIntake_1','SB_FixedTailFuselage'")
exec(compile(code,'<validate_v17>','exec'))
