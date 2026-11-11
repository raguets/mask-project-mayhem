from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Raven'
source=(A/'scripts/review_v4.py').read_text(encoding='utf-8').split("exec(compile((P/'art_source/shared_tools")[0]
exec(compile(source,'<v10-review-config>','exec'))
RENDER_JOB['output_dir']=str(A/'renders/v10_review')
RENDER_JOB['views']=[v for v in RENDER_JOB['views'] if v['name']!='11_half_transform']
RENDER_JOB['views'] += [
{'name':'15_complete_front_roll','frame':61,'properties':{'hover_height':.6},'object_states':actor(m=True),'camera':[5.7,-6.5,3.8],'target':[0,0,1.0],'lens':51},
{'name':'16_secondary_wheel_fold','frame':106,'properties':{'hover_height':.6},'object_states':actor(m=True),'camera':[5.7,-6.5,3.8],'target':[0,0,1.0],'lens':51}]
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(encoding='utf-8'),'<review>','exec'))
