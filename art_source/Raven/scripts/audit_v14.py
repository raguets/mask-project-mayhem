from pathlib import Path
A=Path('G:/DEV/mask-project-mayhem/art_source/Raven')
source=(A/'scripts/audit_v12.py').read_text(encoding='utf-8').replace('validation_v12.json','validation_v14.json')
start=source.index('for join,left,right in ');end=source.index("checks['rounded_black",start)
source=source[:start]+source[end:]
source=source.replace("initial_nozzles['max'][2]<.66","initial_nozzles['max'][2]<.78").replace("deployed_nozzles['min'][2]-.66","deployed_nozzles['min'][2]-.78").replace(".20<cassette.location.z<.215",".19<cassette.location.z<.20")
extra='''
checks['roof_side_thirds_follow_doors']=all(bpy.data.objects['RV_DoorRoofWing_'+s].parent==bpy.data.objects['RV_DoorWing_Hinge_'+s] for s in ['L','R'])
checks['fixed_roof_is_middle_third']=abs(bpy.data.objects['RV_RoofTarga']['roof_width_fraction']-1/3)<1e-6
checks['rear_glass_extends_to_cassette']=min(v.co.x for v in bpy.data.objects['RV_RearHatchGlass'].data.vertices)<-1.81
checks['black_rear_door_pillars_present']=all(bpy.data.objects.get('RV_B_Pillar_'+s) and bpy.data.objects.get('RV_BlackRearDoorPillar_'+s) for s in ['L','R'])
bs=next(n for n in bpy.data.materials['RV_RearPrivacyGlass_V14'].node_tree.nodes if n.type=='BSDF_PRINCIPLED')
checks['rear_glass_very_dark_separate_material']=max(bs.inputs['Base Color'].default_value[:3])<.03 and bpy.data.objects['RV_RearHatchGlass'].data.materials[0]!=bpy.data.objects['RV_Windshield'].data.materials[0]
clearances=[v.x-(-2.225+.035*(v.y/.77)**2) for v in outer_surface('RV_ReactorCassette_FourNozzleBank')]
data['nozzle_rest_depth_clearance_min_m']=min(clearances)
checks['nozzles_behind_bowed_fascia_at_rest']=min(clearances)>0
rows={}
for v in bpy.data.objects['RV_ReactorCassette_RoundedTopAndSides'].data.vertices:
    x=round(v.co.x,6);rows[x]=max(rows.get(x,-100),v.co.z)
checks['cassette_top_horizontal']=max(rows.values())-min(rows.values())<1e-6
'''
source=source.replace('contacts=[];rigid_error=0',extra+'\ncontacts=[];rigid_error=0')
exec(compile(source,'<v14-audit>','exec'))
