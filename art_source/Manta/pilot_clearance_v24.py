import bpy,json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');S=bpy.context.scene;R=bpy.data.objects['VanessaWarfield_Rig'];rows=[]
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
prefix=(P/'art_source/Manta/validate_full_v20.py').read_text().split('parts=lambda')[0]
exec(compile(prefix,'<surface-helper>','exec'))
for mask in [False,True]:
 R['in_vehicle']=1.;R['driving_pose']=1.;R['mask_on']=mask
 for o in S.objects:o.update_tag(refresh={'OBJECT','DATA','TIME'})
 S.frame_set(2);S.frame_set(1);bpy.context.view_layer.update()
 assert R['mask_on']==mask
 cs=[surface(bpy.data.objects['VW_ContinuousBodyAndFace'])[0]]
 if mask:cs += [surface(o)[0] for o in bpy.data.collections['Whip_Mask'].all_objects if o.type=='MESH']
 overlaps={n:sum(len(surface(bpy.data.objects[n])[0].overlap(t)) for t in cs) for n in ['MA_Windshield','MA_TbarRoof','MA_CabinFloor']}
 rows.append({'mask':mask,'overlaps':overlaps})
R['mask_on']=False;R.update_tag();S.frame_set(2);S.frame_set(1)
r={'source':bpy.data.filepath,'passed':all(not any(x['overlaps'].values()) for x in rows),'states':rows}
(P/'art_source/Manta/pilot_clearance_v24.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
