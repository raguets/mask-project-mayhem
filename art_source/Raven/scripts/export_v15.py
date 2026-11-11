from pathlib import Path
A=Path('G:/DEV/mask-project-mayhem/art_source/Raven')
code=(A/'scripts/export_v14.py').read_text(encoding='utf-8').replace('V14','V15').replace('_v14','_v15')
code=code.replace('Curved trapezoidal windshield','Rounded tapered door roof wings; curved trapezoidal windshield')
exec(compile(code,'<export-v15>','exec'))
