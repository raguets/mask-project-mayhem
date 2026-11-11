from pathlib import Path
A=Path('G:/DEV/mask-project-mayhem/art_source/Raven')
source=(A/'scripts/export_v5.py').read_text(encoding='utf-8').replace('V5','V10').replace('_v5','_v10')
source=source.replace('Unshown cam lift provisional; capot/tire collision remains at a late intermediate phase.','Complete front unit carries bodywork/bumper/lamps/wheels through longitudinal roll; front wheels then tilt onto the inverted unit. Recessed diametric guns rise45degrees toward front. No separate hood cam lift. Full swept-volume/game physics validation remains partial; see latest geometry audit.')
exec(compile(source,'<exports-v10>','exec'))
