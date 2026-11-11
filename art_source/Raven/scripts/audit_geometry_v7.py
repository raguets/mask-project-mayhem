from pathlib import Path
A=Path('G:/DEV/mask-project-mayhem/art_source/Raven')
source=(A/'scripts/audit_geometry_v2.py').read_text(encoding='utf-8').replace('geometry_audit_v2.json','geometry_audit_v7.json').replace('[1,46,61,76,91,106,121,151]','[1]+list(range(31,122,3))+[151]')
exec(compile(source,'<geometry-audit-v7>','exec'))
