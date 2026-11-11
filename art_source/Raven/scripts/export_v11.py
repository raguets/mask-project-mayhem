from pathlib import Path
A=Path('G:/DEV/mask-project-mayhem/art_source/Raven')
exec(compile((A/'scripts/export_v10.py').read_text(encoding='utf-8').replace(".replace('V5','V10')",".replace('V5','V11')").replace(".replace('_v5','_v10')",".replace('_v5','_v11')"),'<exports-v11>','exec'))
