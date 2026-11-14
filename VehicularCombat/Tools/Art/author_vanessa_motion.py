from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');T=P/'VehicularCombat/Tools/Art'
code=(T/'author_calhoun_motion.py').read_text(encoding='utf-8-sig').replace('Calhoun','Vanessa').replace('Raven','Manta').replace('V16','V24')
exec(compile(code,'<vanessa-locomotion>','exec'))
