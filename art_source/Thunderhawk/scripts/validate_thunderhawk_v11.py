import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path('G:/DEV/mask-project-mayhem');S=bpy.context.scene;r=bpy.data.objects['MattTrakker_Rig'];report={}
assert sum(o.type=='ARMATURE' for o in bpy.data.collections['MT11_Character'].all_objects)==1
assert sum(o.name=='MT_Head_AnatomicalSurface' for o in S.objects)==1
report['one_character_one_head']=True;report['reference_fidelity']='Interpretation, visual review required; no claim of ultra-faithful photorealism'
# Full transform timing audit.
for fr in range(1,194):
 S.frame_set(fr);x=bpy.data.objects['THK_Reactor_Deploy_L'].location.x;z=bpy.data.objects['THK_RearPanel_Lift'].location.z
 if x<-.00001:assert abs(z-.215)<1e-5,(fr,x,z)
report['reactor_timing_frames_checked']=193
states=[];rigids={o.name:o.data.as_pointer() for o in bpy.data.collections['MT11_Character'].objects if o.type=='MESH'}
for pose in [0,1]:
 for masked in [False,True]:
  r['driving_pose']=pose;r['mask_on']=masked;r.update_tag();S.frame_set(97 if pose else 1);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
  visible=sum(not o.hide_render for o in bpy.data.collections['Spectrum11_Asset'].objects)
  assert (visible>0)==masked,(pose,masked,visible)
  assert all(o.data.as_pointer()==rigids[o.name] for o in bpy.data.collections['MT11_Character'].objects if o.type=='MESH')
  states.append({'driving_pose':pose,'mask_on':masked,'visible_mask_parts':visible,'same_character_meshes':True})
report['four_states']=states
r['driving_pose']=1;r['mask_on']=True;r.location=(0,.4,0);r.update_tag();S.frame_set(1);bpy.context.view_layer.update()
def tree(obs):
 dg=bpy.context.evaluated_depsgraph_get();vv=[];ff=[]
 for ob in obs:
  if ob.type!='MESH':continue
  ev=ob.evaluated_get(dg);me=ev.to_mesh();off=len(vv);vv.extend(ev.matrix_world@v.co for v in me.vertices);ff.extend(tuple(off+i for i in p.vertices) for p in me.polygons);ev.to_mesh_clear()
 return BVHTree.FromPolygons(vv,ff,all_triangles=False) if vv else None
helmet=[o for o in bpy.data.collections['Spectrum11_Asset'].objects if o.type=='MESH']
headtree=tree(helmet);bodytree=tree([bpy.data.objects['MT_ContinuousFlightSuit']])
# Geometric intersection samples between the actual seated meshes and moving doors.
collisions=[]
for fr in [1,25,45,65,85,97,121,133,151,173,193]:
 S.frame_set(fr);bpy.context.view_layer.update()
 doors=[o for o in bpy.data.collections['THK9_Exterior'].objects if o.type=='MESH' and o.name.startswith(('THK_DoorShell','THK_DoorGlass','THK_DoorRoofInset','THK_RoofSpine','THK_DoorAFrame'))]
 dt=tree(doors)
 hp=len(headtree.overlap(dt));bp=len(bodytree.overlap(dt));collisions.append({'frame':fr,'helmet_door_surface_pairs':hp,'suit_door_surface_pairs':bp})
report['sampled_door_surface_intersections']=collisions
# Evaluated shoe sole and roof-envelope measurements, not merely object origins.
dg=bpy.context.evaluated_depsgraph_get()
def bbox(n):
 ob=bpy.data.objects[n].evaluated_get(dg);vv=[ob.matrix_world@Vector(p) for p in ob.bound_box];return {'min':[min(v[i] for v in vv) for i in range(3)],'max':[max(v[i] for v in vv) for i in range(3)]}
report['driving_fit']={n:bbox(n) for n in ['MT_BootSole_L','MT_GlovePalm_L','MT_GlovePalm_R','Spectrum_SilverHelmetShell','THK_RecessedFootwell_L']}
report['single_suit_mesh_vertices']=len(bpy.data.objects['MT_ContinuousFlightSuit'].data.vertices)
report['limitations']=['Portrait is an illustration; photographic references are toys and helmet replicas.','Semi-realistic artistic interpretation, not validated photoreal likeness.','Voxel cloth sculpt retains source cages; shipping retopology/UV and animation-quality deform polish remain.','Collision samples cover moving door surfaces versus helmet and suit, not an exhaustive physical collision certification.']
(P/'art_source/Thunderhawk/validation_v11.json').write_text(json.dumps(report,indent=2))
S.frame_set(97);r['mask_on']=False;r.update_tag();bpy.context.view_layer.update()
print(json.dumps(report))
