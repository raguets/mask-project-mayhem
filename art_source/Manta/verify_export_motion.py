import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Manta';C=Matrix.Diagonal((100.,-100.,100.,1.))
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
manifest=json.loads((P/'VehicularCombat/SourceArt/MASK/Manta/manifest.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(P/'art_source/GameReady/Manta/Manta_GameReady.blend'))
vertices={p['name']:[bpy.data.objects[p['name']].matrix_world@v.co for v in bpy.data.objects[p['name']].data.vertices] for p in manifest['parts']}
bpy.ops.wm.open_mainfile(filepath=str(A/'Manta_V24_Assembly.blend'));S=bpy.context.scene;R=bpy.data.objects['VanessaWarfield_Rig'];rows=[]
code=(A/'verify_export_geometry.py').read_text();start=code.index('for o in S.objects:');end=code.index('expected={k:bounds(v)',start);collect=code[start:end]
for frame,index in [(1,0),(61,48),(121,96)]:
 S.frame_set(frame);bpy.context.view_layer.update();groups={};exec(compile(collect,'<source-group-bounds>','exec'))
 for part in manifest['parts']:
  sm=part['samples'][index];q=sm['q'];M=C.inverted()@Matrix.LocRotScale(Vector(sm['t']),Quaternion((q[3],q[0],q[1],q[2])),Vector(sm['s']))@C
  expected=bounds(groups[part['name']]);actual=bounds([M@v for v in vertices[part['name']]])
  rows.append({'frame':frame,'part':part['name'],'delta_m':max(abs(a-b) for a,b in zip(expected,actual))})
r={'passed':all(x['delta_m']<.025 for x in rows),'checks':rows}
(A/'export_motion_validation.json').write_text(json.dumps(r,indent=2));print(json.dumps({'passed':r['passed'],'largest':sorted(rows,key=lambda x:-x['delta_m'])[:6]}));S.frame_set(1)
