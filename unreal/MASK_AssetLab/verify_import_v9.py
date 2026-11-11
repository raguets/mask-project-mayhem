"""Verify actual imported mesh bounds against Blender's evaluated rest geometry."""
import unreal,json
from pathlib import Path
project=Path(unreal.Paths.project_dir()); art=project.parents[1]/'art_source'/'Thunderhawk'
data=json.loads((art/'exports'/'THK_V9_assembly.json').read_text(encoding='utf-8'))
checks=[]
for item in data['objects']:
    asset=unreal.EditorAssetLibrary.load_asset('/Game/Thunderhawk_V9/'+item['name'])
    if not asset: checks.append({'name':item['name'],'error':'missing'}); continue
    b=asset.get_bounding_box(); actual={'min':[b.min.x,b.min.y,b.min.z],'max':[b.max.x,b.max.y,b.max.z]}
    err=max(abs(actual[k][i]-item['rest_bounds_cm'][k][i]) for k in ('min','max') for i in range(3))
    checks.append({'name':item['name'],'max_bound_error_cm':err})
report={'checked_meshes':len(checks),'tolerance_cm':.1,'max_bound_error_cm':max(c.get('max_bound_error_cm',1e9) for c in checks),
        'status':'PASS' if all(c.get('max_bound_error_cm',1e9)<.1 for c in checks) else 'FAIL','checks':checks,
        'limitation':'Axis/scale/rest bounding boxes; does not prove UV quality, shading or visual equivalence.'}
(project/'import_v9_geometry_check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
unreal.log_warning('THK_V9_GEOMETRY '+str({k:v for k,v in report.items() if k!='checks'}))

