from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Raven'
source=(A/'scripts/review_v2.py').read_text(encoding='utf-8').split('exec(compile')[0]
exec(compile(source.replace('renders/v2_review','renders/v4_review'),'<v4-review-config>','exec'))
RENDER_JOB['views'] += [
{'name':'13_wheel_cannon','frame':151,'properties':{'hover_height':.6},'object_states':actor(m=True),'camera':[2.8,-3.6,3.2],'target':[1.1,-.4,1.45],'lens':75},
{'name':'14_rear_slide','frame':151,'properties':{'hover_height':.6},'object_states':actor(m=True),'camera':[-4.5,3.1,2.2],'target':[-1.75,0,1.35],'lens':72}]
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(encoding='utf-8'),'<review>','exec'))
