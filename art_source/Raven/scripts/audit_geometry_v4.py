from pathlib import Path
A=Path('G:/DEV/mask-project-mayhem/art_source/Raven')
exec(compile((A/'scripts/audit_geometry_v2.py').read_text(encoding='utf-8').replace('geometry_audit_v2.json','geometry_audit_v4.json'),'<geometry-audit-v4>','exec'))
