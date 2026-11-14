from pathlib import Path
p=Path('G:/DEV/mask-project-mayhem/art_source/Manta/validate_v10.py').read_text()
p=p.replace('validation_v10.json','validation_v11.json').replace("'version':10","'version':11")
# The wrapper constructs the underlying source substitutions at execution time.
p=p.replace("'validation_v10.json'","'validation_v11.json'")
exec(compile(p,'<validation_v11>','exec'))
