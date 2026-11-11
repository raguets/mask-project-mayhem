import json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
RENDER_JOB=json.loads((P/'art_source/Thunderhawk/scripts/review_v14_job.json').read_text())
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(),'render_review_queue.py','exec'))
