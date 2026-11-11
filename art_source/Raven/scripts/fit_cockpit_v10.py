from pathlib import Path
A=Path('G:/DEV/mask-project-mayhem/art_source/Raven')
exec(compile((A/'scripts/fit_cockpit_v8.py').read_text(encoding='utf-8').replace('V8','V10'),'<cockpit-fit-v10>','exec'))
