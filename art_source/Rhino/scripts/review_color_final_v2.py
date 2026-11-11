import ast
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');path=P/'art_source/Rhino/scripts/review_final_v2.py';tree=ast.parse(path.read_text(encoding='utf-8'));exec(compile(ast.Module(body=tree.body[:-1],type_ignores=[]),'<v2_review_config>','exec'))
RENDER_JOB['output_dir']=str(P/'art_source/Rhino/renders/v2_final');RENDER_JOB['width']=1100;RENDER_JOB['height']=800;RENDER_JOB['samples']=20
RENDER_JOB['views']=[v for v in RENDER_JOB['views'] if v['name'] in ['road_front','road_profile','mid_transform','transformed','transformed_rear','launcher','cabin_mask','crew_fit']]
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(encoding='utf-8'),'<render_review_queue>','exec'))
