from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Hurricane'
text=(A/'scripts/export_v6.py').read_text().replace('V6','V7').replace('_v6','_v7')
exec(compile(text,'<export-v7>','exec'))
