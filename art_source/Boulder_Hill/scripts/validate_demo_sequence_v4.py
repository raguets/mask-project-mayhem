import bpy,json,ast
from pathlib import Path
from mathutils import Vector,Matrix
P=Path('G:/DEV/mask-project-mayhem');S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
tree=ast.parse((P/'art_source/Boulder_Hill/scripts/validate_layout_final.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'rect','overlaps'}],type_ignores=[]),'<sat>','exec'))
fr=S.frame_current;d=json.loads((P/'art_source/Boulder_Hill/vehicle_measurements_v1.json').read_text())['assets'];hits=[]
try:
    for frame in range(1,542):
        S.frame_set(frame);bpy.context.view_layer.update();a=bpy.data.objects['BH_Thunderhawk_PathRoot'];b=bpy.data.objects['BH_Rhino_PathRoot']
        if overlaps(rect(a.matrix_world,d['Thunderhawk']['length'],d['Thunderhawk']['width']),rect(b.matrix_world,d['Rhino']['length'],d['Rhino']['width'])):hits.append(frame)
    result={'method':'2D separating-axis test on conservative full vehicle road envelopes at every integer animation frame. Does not simulate steering, wheels, terrain contact or dynamics.','sampled_frames':541,'vehicle_overlap_frames':hits,'end_positions':{name:list(bpy.data.objects['BH_'+name+'_PathRoot'].matrix_world.translation) for name in ['Thunderhawk','Rhino']}}
    (P/'docs/qa/boulder_demo_sequence_v4.json').write_text(json.dumps(result,indent=2));print('DEMO_SEQUENCE overlaps',hits)
finally:S.frame_set(fr);bpy.context.view_layer.update()
