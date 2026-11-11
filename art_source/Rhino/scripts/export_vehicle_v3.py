import json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Rhino'
assert (A/'renders/v3/COMPLETE').exists()
assert not json.loads((A/'bullbar_validation_v3.json').read_text())['collision_frames']
EXPORT_JOB={'source_blend':str(A/'Rhino_V3.blend'),'rig':'Rhino_Control','floor':'Review_Floor','manifest':str(A/'vehicle_export_v3.json'),'components':[
 {'kind':'vehicle','output':str(A/'Rhino_V3_Vehicle.blend'),'scene_name':'Rhino_V3_IndependentVehicle','collections':['Rhino_Truck','Rhino_RearVehicle','Rhino_Interior'],'frame':1,'presentation':{'camera':[12,11,7],'target':[.3,0,2],'lens':52,'focus':[.3,0,1.8],'distance':13},'help_text':'RHINO V3\nPare-buffle : cadre ferme et sept barreaux verticaux, largeur et hauteur alignees sur la calandre. Reference fournie rhino pare buffle.jpg inspectee.\nRhino_Control : battle_mode 0 route / 1 transforme, timeline 1-241. Pare-buffle avance par bullbar ; meme mecanisme conserve.\nAutres mecanismes V2 conserves : canons, separation du module, panneau arriere, recul du coffre puis missile, radar independant.\nDimensions et attaches cachees interpretees. Source independante sans personnages.\n'}]}
exec(compile((P/'art_source/shared_tools/export_components.py').read_text(encoding='utf-8'),'<component_export>','exec'))
