from pathlib import Path
A=Path('G:/DEV/mask-project-mayhem/art_source/Raven')
source=(A/'scripts/audit_v12.py').read_text(encoding='utf-8').replace('validation_v12.json','validation_v13.json')
source=source.replace("initial_nozzles['max'][2]<.66","initial_nozzles['max'][2]<.78").replace("deployed_nozzles['min'][2]-.66","deployed_nozzles['min'][2]-.78").replace(".20<cassette.location.z<.215",".19<cassette.location.z<.20")
extra="""roofrows={}
for v in bpy.data.objects['RV_ReactorCassette_RoundedTopAndSides'].data.vertices:
    x=round(v.co.x,6);roofrows[x]=max(roofrows.get(x,-100),v.co.z)
data['cassette_roof_longitudinal_height_range_m']=max(roofrows.values())-min(roofrows.values())
checks['cassette_roof_horizontal']=data['cassette_roof_longitudinal_height_range_m']<1e-6
checks['cassette_never_tilts']"""
source=source.replace("checks['cassette_never_tilts']",extra)
exec(compile(source,'<v13-audit>','exec'))
