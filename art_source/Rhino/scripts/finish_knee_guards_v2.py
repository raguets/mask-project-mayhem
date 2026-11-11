"""Formed orange guards on the same Bruce rig, replacing jagged surface-bound patches."""
import bpy,ast
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Rhino';S=bpy.context.scene;assert not S.get('knee_guards_v2')
assert (A/'renders/v2/COMPLETE').exists(),'Wait for the active review before editing.'
tree=ast.parse((A/'scripts/build_characters_v1.py').read_text(encoding='utf-8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'<skin_helpers>','exec'))
r=bpy.data.objects['BruceSato_Rig'];saved=(r['driving_pose'],r['mask_on'],r.location.copy());r['driving_pose']=0;r['mask_on']=False;r.location=(0,0,0);r.update_tag();bpy.context.view_layer.update()
for sg,sd in [(1,'L'),(-1,'R')]:
 ob=bpy.data.objects['BS_KneePatch_'+sd]
 for mod in list(ob.modifiers):ob.modifiers.remove(mod)
 ob.vertex_groups.clear();verts=[];faces=[];N=21
 for j in range(N):
  dz=-.050+.10*j/(N-1)
  for i in range(N):
   dy=-.058+.116*i/(N-1);x=.102-.018*(dy/.058)**2-.008*(dz/.05)**2;verts.append((x,sg*.11+dy,.535+dz))
 for j in range(N-1):faces.extend((j*N+i,j*N+i+1,(j+1)*N+i+1,(j+1)*N+i) for i in range(N-1))
 ob.data.clear_geometry();ob.data.from_pydata(verts,[],faces);ob.data.update()
 for f in ob.data.polygons:f.use_smooth=True
 bind(ob,r,'shin.'+sd);mod=ob.modifiers.new('FormedGuardThickness','SOLIDIFY');mod.thickness=.004;mod=ob.modifiers.new('SoftGuardEdges','BEVEL');mod.width=.003;mod.segments=3
 ob['construction']='Formed guard follows shin rigidly, replacing surface-deform patch. Supplied orange pad silhouette interpreted.'
r['driving_pose'],r['mask_on'],r.location=saved;r.update_tag();bpy.context.view_layer.update();S['knee_guards_v2']='Two smooth formed knee guards, same Bruce rig, no stale surface-deform binding.';bpy.ops.wm.save_as_mainfile(filepath=str(A/'Rhino_V2.blend'),compress=True);print('BRUCE_SMOOTH_KNEE_GUARDS_SAVED')
