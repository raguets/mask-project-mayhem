"""Blender MCP: on-foot actions on Brad's own editable game-exported skeleton."""
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');T=P/'VehicularCombat/Tools/Art'
code=(T/'author_calhoun_motion.py').read_text(encoding='utf-8-sig').replace('Calhoun','Brad').replace('Raven','Condor').replace('V16','V20')
exec(compile(code,'<brad-locomotion>','exec'))
