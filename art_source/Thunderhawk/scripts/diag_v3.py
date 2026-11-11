import bpy
exec(open(bpy.path.abspath('//scripts/check_intersections_v3.py'),encoding='utf-8-sig').read().split('with open')[0])
for fr in [1,35,45,55,85]:
 s.frame_set(fr)
 for b in ('THK_Body','THK_Roof'):
  a=bpy.data.objects['THK_Wing_L']; bb=bpy.data.objects[b]; hits=tree(a).overlap(tree(bb)); print('DIAG',fr,b,len(hits),[(tuple(round(v,2) for v in (bb.matrix_world @ bb.data.polygons[j].center))) for i,j in hits[:5]])


