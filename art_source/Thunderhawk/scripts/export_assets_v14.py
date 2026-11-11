import json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
EXPORT_JOB=json.loads((P/'art_source/Thunderhawk/scripts/export_v14_job.json').read_text())
exec(compile((P/'art_source/shared_tools/export_components.py').read_text(),'export_components.py','exec'))
