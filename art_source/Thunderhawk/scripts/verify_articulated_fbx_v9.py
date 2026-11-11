"""Round-trip the actual animated FBX into a clean Blender scene; no source save."""
import bpy,json
from pathlib import Path
ROOT=Path('G:/DEV/mask-project-mayhem/art_source/Thunderhawk')
names=['THK_DoorShell_L','THK_DoorShell_R','THK_RearPanel','THK_RearStabilizer','THK_DoorCannon_L','THK_DoorCannon_R']
frames=[1,65,97,151,193]
def bound(name):
    ob=bpy.data.objects[name];ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
    vv=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear()
    return [min(p[i] for p in vv) for i in range(3)]+[max(p[i] for p in vv) for i in range(3)]
expected={}
for fr in frames:
    bpy.context.scene.frame_set(fr)
    for name in names:expected[(fr,name)]=bound(name)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(ROOT/'exports'/'THK_V9_Articulated.fbx'),use_anim=True,anim_offset=0.0)
checks=[]
for fr in frames:
    bpy.context.scene.frame_set(fr)
    for name in names:
        if name not in bpy.data.objects:checks.append({'frame':fr,'name':name,'error':'MISSING'});continue
        actual=bound(name);error=max(abs(a-b) for a,b in zip(actual,expected[(fr,name)]))
        checks.append({'frame':fr,'name':name,'max_bound_error_m':error})
report={'fbx':'exports/THK_V9_Articulated.fbx','checks':checks,'tolerance_m':.0001,'blender_import_anim_offset':0.0,'export_simplification':0.0,
        'status':'PASS' if all(c.get('max_bound_error_m',1e6)<.0001 for c in checks) else 'FAIL',
        'limitation':'Evaluated world bounds of six major parts at five poses; not an Unreal skeletal import or a full continuous trajectory comparison.'}
(ROOT/'articulated_fbx_roundtrip_v9.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('THK9_FBX_ROUNDTRIP',report['status'],max(c.get('max_bound_error_m',1e6) for c in checks))
