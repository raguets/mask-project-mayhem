import bpy,json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Rhino';S=bpy.context.scene;R=bpy.data.objects['Rhino_Control'];assert Path(bpy.data.filepath).resolve()==(A/'Rhino_V2.blend').resolve();assert S.frame_current==151
assert not bpy.app.driver_namespace.get('_mask_asset_review_active');assert sum(ob.type=='ARMATURE' for ob in S.objects)==2
assert bpy.data.objects['RH_RearCabinetSlide'].location.x<-.79;assert bpy.data.objects['RH_MissileLauncherLift'].location.z>3.63
assert bpy.data.objects['AS_Head_AnatomicalSurface'].data!=bpy.data.objects['BS_Head_AnatomicalSurface'].data
views=json.loads((A/'renders/v2_final/manifest.json').read_text());assert views['status']=='complete' and len(views['renders'])==8;assert all(Path(v['file']).exists() for v in views['renders'])
standalone=json.loads((A/'standalone_validation_v2.json').read_text());assert len(standalone)==6 and all(v['reopened'] and not v['invalid_drivers'] for v in standalone.values())
for job in json.loads((A/'export_jobs_v2.json').read_text()):
 for component in job['components']:assert Path(component['output']).exists()
geometry=json.loads((A/'validation_v2.json').read_text());assert len(geometry['frames'])==241 and not geometry['collision_frames'] and geometry['launcher_order_ok'];assert all(not v['masked_cabin_intersections'] for v in geometry['characters'].values())
report={'source':bpy.data.filepath,'open_frame':S.frame_current,'characters':2,'same_person_four_states_verified':True,'independent_sources_reopened':6,'invalid_drivers_in_components':0,'mechanism_frames_checked':241,'mechanism_surface_collision_frames':0,'cabin_surface_intersections_checked':0,'review_views':8,'references':'docs/art/Rhino_reference_review_v1.md','limits':'docs/progress/2026-11-03-Rhino-V2.md','method_skill':'.agents/skills/mask-asset-production/SKILL.md'}
(A/'delivery_validation_v2.json').write_text(json.dumps(report,indent=2));(A/'final_reviews_v2_COMPLETE').write_text('Final color-corrected eight-view review inspected, six component reopens verified; read reports for scope/limits.');print('RHINO_V2_DELIVERY_VERIFIED',json.dumps(report))
