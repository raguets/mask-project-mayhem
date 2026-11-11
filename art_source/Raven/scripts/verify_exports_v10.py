from pathlib import Path
A=Path('G:/DEV/mask-project-mayhem/art_source/Raven')
exec(compile((A/'scripts/verify_exports_v5.py').read_text(encoding='utf-8').replace('V5','V10').replace('_v5','_v10'),'<verify-exports-v10>','exec'))
