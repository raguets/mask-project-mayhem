import bpy,json,math,time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
A=Path('G:/DEV/mask-project-mayhem/art_source/Manta');S=bpy.context.scene;root=bpy.data.objects['Manta_Control'];R=bpy.data.objects['VanessaWarfield_Rig']
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
def surf(o):
 dg=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(dg);me=ev.to_mesh();v=[ev.matrix_world@p.co for p in me.vertices];f=[list(p.vertices) for p in me.polygons];ev.to_mesh_clear();return BVHTree.FromPolygons(v,f),v
names=['MA_MainBody','MA_Underbody','MA_MainWing_1','MA_MainWing_-1','MA_FrontWheel_1_Tire','MA_FrontWheel_-1_Tire','MA_RearWheel_1_Tire','MA_RearWheel_-1_Tire','MA_SlidingHoodSkin','MA_RearLightPanel','MA_ReactorCassette']
pairs=[('MA_MainBody',n) for n in names[2:]]+[('MA_Underbody','MA_MainWing_'+str(s)) for s in [-1,1]]
hits={a+' / '+b:[] for a,b in pairs};phases=[];mins={n:999 for n in names}
for f in range(1,122):
 S.frame_set(f);bpy.context.view_layer.update();ss={n:surf(bpy.data.objects[n]) for n in names}
 phases.append(float(root['transform']))
 for n,(bv,v) in ss.items():mins[n]=min(mins[n],min(p.z for p in v))
 for a,b in pairs:
  ov=ss[a][0].overlap(ss[b][0])
  if ov:hits[a+' / '+b].append({'frame':f,'t':float(root['transform']),'triangle_pairs':len(ov)})
invalid=[]
for o in bpy.data.objects:
 if o.animation_data:
  invalid.extend([(o.name,f.data_path,f.array_index) for f in o.animation_data.drivers if not f.driver.is_valid])
pilot=[]
for mask in [False,True]:
 R['driving_pose']=1.;R['in_vehicle']=1.;R['mask_on']=mask;R.update_tag();S.frame_set(1);bpy.context.view_layer.update()
 ids=['VW_ContinuousBodyAndFace']+([o.name for o in bpy.data.collections['Whip_Mask'].all_objects if o.type=='MESH'] if mask else [o.name for o in bpy.data.collections['Vanessa_Character'].all_objects if o.type=='MESH' and ('Hair' in o.name or 'Fringe' in o.name)])
 trees={n:surf(bpy.data.objects[n]) for n in ids};test={}
 for n in ['MA_Windshield','MA_TbarRoof','MA_RoofFrontCross','MA_RoofRearCross','MA_CabinFloor']:
  b=surf(bpy.data.objects[n])[0];test[n]=sum(len(b.overlap(v[0])) for v in trees.values())
 pilot.append({'mask_on':mask,'surface_intersections':test,'highest_head_or_mask':max(v.z for name,(tr,vs) in trees.items() for v in vs if v.z>.8)})
R['mask_on']=False;R.update_tag();S.frame_set(1);bpy.context.view_layer.update()
report={'version':4,'phases':121,'transform_samples':phases,'invalid_drivers':invalid,'selected_surface_overlaps':hits,'minimum_world_z':mins,'pilot':pilot,'limits':'Evaluated triangle surfaces for selected pairs; intended mounts/seams may overlap. Does not prove absence of containment or all-part collisions. No gameplay/physics validation.'}
(A/'validation_v4.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'invalid_drivers':invalid,'colliding_phase_counts':{k:len(v) for k,v in hits.items()},'minimum_z':mins,'pilot':pilot}))
