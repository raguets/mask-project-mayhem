from pathlib import Path
P=Path(__file__).resolve().parents[2];A=P/'art_source/Rhino/scripts'
s=(A/'export_v1.py').read_text(encoding='utf-8')
for old,new in [('Rhino_V1.blend','Rhino_V2.blend'),('Rhino_V1_Vehicle.blend','Rhino_V2_Vehicle.blend'),('Rhino_V1_IndependentVehicle','Rhino_V2_IndependentVehicle'),('final_reviews_COMPLETE','final_reviews_v2_COMPLETE'),('validation_v1.json','validation_v2.json'),('vehicle_exports_v1.json','vehicle_exports_v2.json'),('export_jobs_v1.json','export_jobs_v2.json'),('RHINO V1','RHINO V2')]:s=s.replace(old,new)
s=s.replace('Commandes partielles : bullbar, cannons, rear_detach, rear_open, launcher_up.', 'Commandes partielles : bullbar, cannons, rear_detach, rear_open, cabinet_slide, launcher_up ; radar_spin pilote le radar.')
s=s.replace('Le lanceur reste bloque tant que la porte arriere nest pas ouverte.', 'Le lanceur reste bloque tant que la porte arriere nest pas ouverte et le grand coffre recule.')
(A/'export_v2.py').write_text(s,encoding='utf-8')
s=(A/'verify_exports_v1.py').read_text(encoding='utf-8')
for old,new in [('Rhino_V1.blend','Rhino_V2.blend'),('Rhino_V1_Vehicle.blend','Rhino_V2_Vehicle.blend'),('standalone_validation_v1.json','standalone_validation_v2.json')]:s=s.replace(old,new)
s=s.replace("'rear_hatch_angle':bpy.data.objects['RH_RearCockpitHatchPivot'].rotation_euler.y", "'rear_hatch_angle':bpy.data.objects['RH_RearCockpitHatchPivot'].rotation_euler.y,'cabinet_x':bpy.data.objects['RH_RearCabinetSlide'].location.x,'launcher_z':bpy.data.objects['RH_MissileLauncherLift'].location.z,'radar_angle':bpy.data.objects['RH_RadarRotation'].rotation_euler.z")
s=s.replace("entry['transform_states']=states;assert states[2]['pod_location'][0]<-4.8", "entry['transform_states']=states;assert states[2]['pod_location'][0]<-4.8;assert states[2]['cabinet_x']<-.79 and states[2]['launcher_z']>3.63;assert states[1]['radar_angle']!=states[0]['radar_angle']")
(A/'verify_exports_v2.py').write_text(s,encoding='utf-8')
print('V2 export and real reopen verification scripts prepared')
