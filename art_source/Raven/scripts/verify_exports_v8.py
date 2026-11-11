from pathlib import Path
A=Path('G:/DEV/mask-project-mayhem/art_source/Raven')
exec(compile((A/'scripts/verify_exports_v5.py').read_text(encoding='utf-8').replace('V5','V8').replace('_v5','_v8'),'<verify-exports-v8>','exec'))
