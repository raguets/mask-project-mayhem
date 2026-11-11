from pathlib import Path
A=Path('G:/DEV/mask-project-mayhem/art_source/Raven')
source=(A/'scripts/export_v5.py').read_text(encoding='utf-8').replace('V5','V8').replace('_v5','_v8')
source=source.replace('Unshown cam lift provisional; capot/tire collision remains at a late intermediate phase.','Unshown linkage and overlapping progress rates interpreted; complete swept-volume validation remains partial. See evaluated geometry audit and rendered views.')
exec(compile(source,'<exports-v8>','exec'))
