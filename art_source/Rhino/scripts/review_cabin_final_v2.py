import ast,json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');path=P/'art_source/Rhino/scripts/review_final_v2.py'
tree=ast.parse(path.read_text(encoding='utf-8'));exec(compile(ast.Module(body=tree.body[:-1],type_ignores=[]),'<v2_review_config>','exec'))
RENDER_JOB['views']=[v for v in RENDER_JOB['views'] if v['name'] in ['cabin','cabin_mask','crew_fit']];RENDER_JOB['retain_unrequested_views']=True
RENDER_JOB['retention_reason']='Interior knee guards changed. The three cutaway/interior views are rerendered; general vehicle/mechanism views retain occluded knee geometry.'
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(encoding='utf-8'),'<render_review_queue>','exec'))
