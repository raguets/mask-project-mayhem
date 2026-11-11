import bpy,json
from pathlib import Path
from mathutils.bvhtree import BVHTree
S=bpy.context.scene
def mesh(name):
 o=bpy.data.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get());m=o.to_mesh();v=[o.matrix_world@p.co for p in m.vertices];f=[tuple(p.vertices) for p in m.polygons];o.to_mesh_clear();return v,f,BVHTree.FromPolygons(v,f)
out=[]
for frame,a,b in [(1,'HU_CurvedRoofFrontHeader','HU_OpeningRoofPanel'),(1,'HU_RaisedRoofHingeBracket_1','HU_OpeningRoofPanel'),(65,'HU_OpeningRoofPanel','HU_RoofCannon_1'),(151,'HU_SculptedSide_R','HU_CentreWheel_R_Tire'),(80,'HU_FrontFenderCrown_R','HU_HeadlightLens_R'),(97,'HU_WraparoundWindshield','HU_WindshieldCannonCover'),(97,'HU_FrontFenderCrown_R',"HU_HeadlightCannonCollar_('R', 2.4)")]:
 S.frame_set(frame);bpy.context.view_layer.update();va,fa,ta=mesh(a);vb,fb,tb=mesh(b);pairs=ta.overlap(tb);ca=[sum((va[k] for k in fa[i]),va[0]*0)/len(fa[i]) for i,j in pairs];cb=[sum((vb[k] for k in fb[j]),vb[0]*0)/len(fb[j]) for i,j in pairs]
 out.append({'frame':frame,'pair':[a,b],'contacts':len(pairs),'a_centroids':[[round(x,4) for x in p] for p in ca[:15]],'b_centroids':[[round(x,4) for x in p] for p in cb[:15]],'a_bounds':[[min(p[k] for p in va),max(p[k] for p in va)] for k in range(3)],'b_bounds':[[min(p[k] for p in vb),max(p[k] for p in vb)] for k in range(3)]})
S.frame_set(1);Path('G:/DEV/mask-project-mayhem/art_source/Hurricane/contacts_probe_v5.json').write_text(json.dumps(out,indent=2));print('CONTACT_PROBE_SAVED')
