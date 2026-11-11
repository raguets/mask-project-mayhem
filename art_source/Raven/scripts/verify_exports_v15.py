from pathlib import Path
A=Path('G:/DEV/mask-project-mayhem/art_source/Raven')
code=(A/'scripts/verify_exports_v14.py').read_text(encoding='utf-8').replace('V14','V15').replace('_v14','_v15')
exec(compile(code,'<verify-exports-v15>','exec'))
