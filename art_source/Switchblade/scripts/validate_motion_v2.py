"""Evaluated mesh checks, selected moving pairs; not a universal collision certificate."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Switchblade';s=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
root=bpy.data.objects['Switchblade_Control'];R=bpy.data.objects['MilesMayhem_Rig'];saved=(s.frame_current,root['rotor_angle'],root['canopy_open'],R['mask_on'])
def evaluated(name):
 o=bpy.data.objects[name];dg=bpy.context.evaluated_depsgraph_get();e=o.evaluated_get(dg);m=e.to_mesh();v=[e.matrix_world@p.co for p in m.vertices];f=[tuple(p.vertices) for p in m.polygons];tree=BVHTree.FromPolygons(v,f);e.to_mesh_clear();return v,tree
fixed=['SB_FixedTailFuselage','SB_CabinBelly','SB_NoseWedge','SB_MagentaFacetedGlazing']
moving=['SB_MainWing_-1','SB_MainWing_1','SB_MainRotorBlade_-1','SB_MainRotorBlade_1','SB_LandingSkidCannon_-1','SB_LandingSkidCannon_1']
pairs=[(a,b) for a in moving for b in fixed]
pairs += [('SB_MainWing_'+str(t),'SB_LandingSkidCannon_'+str(t)) for t in [-1,1]]
pairs += [('SB_MainRotorBlade_'+str(t),'SB_VentralTailRotorFin') for t in [-1,1]]
collisions={};ground=1e9;rotor_min=1e9
for frame in range(1,122):
 s.frame_set(frame);root.update_tag();bpy.context.view_layer.update();names=set(n for p in pairs for n in p);meshes={n:evaluated(n) for n in names}
 for a,b in pairs:
  overlaps=meshes[a][1].overlap(meshes[b][1])
  if overlaps:collisions.setdefault(a+' / '+b,[]).append({'frame':frame,'triangle_pairs':len(overlaps)})
 ground=min(ground,min(v.z for n in ['SB_LandingSkidCannon_-1','SB_LandingSkidCannon_1'] for v in meshes[n][0]))
# Full angular sampling of helicopter rotor against canopy and tail.
s.frame_set(1)
rotor_hits=[]
for deg in range(0,360,3):
 root['rotor_angle']=math.radians(deg);root.update_tag();bpy.context.view_layer.update()
 for a in ['SB_MainRotorBlade_-1','SB_MainRotorBlade_1']:
  v,t=evaluated(a)
  for b in fixed:
   if t.overlap(evaluated(b)[1]):rotor_hits.append({'angle':deg,'blade':a,'obstacle':b})
  rotor_min=min(rotor_min,min(p.z for p in v))
# Pilot / glazing intersections on evaluated meshes, both mask states.
root['rotor_angle']=0.;root.update_tag();bpy.context.view_layer.update();pilot=[]
for mask in [False,True]:
 R['mask_on']=mask;R.update_tag();bpy.context.view_layer.update();glass=evaluated('SB_MagentaFacetedGlazing')[1]
 hits=[]
 for o in list(bpy.data.collections['Miles_Character'].all_objects)+list(bpy.data.collections['Miles_ViperMask'].all_objects):
  if o.type=='MESH' and not o.hide_render and glass.overlap(evaluated(o.name)[1]):hits.append(o.name)
 pilot.append({'mask_on':mask,'glazing_intersections':hits})
report={'scope':'121 integer phases; triangle intersections for listed evaluated moving/fixed surfaces. No complete volume containment proof. Rotor angular step 3 degrees, not exact swept volume. Contact/hinge pairs excluded. Gameplay/aerodynamics not tested.', 'phase_count':121,'selected_pairs':pairs,'collisions':collisions,'minimum_skid_rail_z_m':ground,'rotor_samples':120,'rotor_hits':rotor_hits,'minimum_helicopter_blade_z_m':rotor_min,'pilot_glazing':pilot}
s.frame_set(saved[0]);root['rotor_angle']=saved[1];root['canopy_open']=saved[2];R['mask_on']=saved[3];root.update_tag();R.update_tag();bpy.context.view_layer.update()
(A/'motion_validation_v2.json').write_text(json.dumps(report,indent=2));print('MOTION_CHECK',json.dumps({'collision_pairs':{k:len(v) for k,v in collisions.items()},'rotor_hits':len(rotor_hits),'ground_min':ground,'pilot':pilot}))
