from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');T=P/'VehicularCombat/Tools/Art'
code=(T/'author_calhoun_motion.py').read_text(encoding='utf-8-sig').replace('Calhoun','Miles').replace('Raven','Switchblade').replace('V16','V22')
exec(compile(code,'<miles-locomotion>','exec'))
