from pathlib import Path
A=Path('G:/DEV/mask-project-mayhem/art_source/Raven')
source=(A/'scripts/audit_geometry_v10.py').read_text(encoding='utf-8').replace('geometry_audit_v10.json','geometry_audit_v11.json')
exec(compile(source,'<geometry-audit-v11>','exec'))
