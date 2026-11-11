from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Boulder_Hill'
EXPORT_JOB={'source_blend':str(A/'BoulderHill_V4_Assembly.blend'),'manifest':str(A/'independent_export_v4.json'),'rig':'BoulderHill_Control','components':[
{'kind':'environment','output':str(A/'BoulderHill_V4_Base.blend'),'scene_name':'BoulderHill_V4_Base','collections':['BH_Ground','BH_Shop','BH_QuarterGarage','BH_Pumps','BH_Sign','BH_Rock','BH_Turret','BH_Hangar','BH_Studio'],'extra_objects':['BoulderHill_Control'],'frame':1,'help_text':(A/'README.md').read_text(encoding='utf-8'),'presentation':{'camera':[63,-82,43],'target':[0,17,12],'lens':46,'focus':[0,-2,7],'distance':57}}
]}
exec(compile((P/'art_source/shared_tools/export_components.py').read_text(encoding='utf-8'),'<export>','exec'))
