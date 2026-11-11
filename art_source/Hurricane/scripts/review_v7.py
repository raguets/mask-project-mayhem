from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Hurricane'
exec(compile((A/'scripts/review_v6.py').read_text().split('exec(compile')[0],'<review-config>','exec'))
RENDER_JOB['output_dir']=str(A/'renders/v7_final');RENDER_JOB['views']=[v for v in RENDER_JOB['views'] if v['name'] in ['01_road','02_battle','03_profile','04_rear_eject','09_gunner','11_chassis','12_right_cannon']]
RENDER_JOB['floor']='HU_ReviewFloor'
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(encoding='utf-8'),'<review>','exec'))
