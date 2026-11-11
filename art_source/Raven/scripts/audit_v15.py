from pathlib import Path
A=Path('G:/DEV/mask-project-mayhem/art_source/Raven')
code=(A/'scripts/audit_v14.py').read_text(encoding='utf-8').replace("'validation_v14.json'","'validation_v15.json'")
exec(compile(code,'<audit-v15>','exec'))
import json,bpy
p=A/'validation_v15.json';report=json.loads(p.read_text())
report['checks']['rounded_door_glass_roof_bends']=all(bpy.data.objects.get('RV_DoorGlassRoof_RoundedBend_'+s) and bpy.data.objects['RV_DoorGlassRoof_RoundedBend_'+s].parent==bpy.data.objects['RV_DoorWing_Hinge_'+s] for s in ['L','R'])
report['checks']['roof_wings_narrower_at_front']=all(bpy.data.objects['RV_DoorRoofWing_'+s].get('front_narrowing_fraction',0)>.09 for s in ['L','R'])
report['passed']=all(report['checks'].values());p.write_text(json.dumps(report,indent=2));print('V15_AUDIT',report['passed'])
