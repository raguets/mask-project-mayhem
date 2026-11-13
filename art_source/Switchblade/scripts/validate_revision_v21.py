import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Switchblade'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
r=bpy.data.objects['Switchblade_Control'];s=bpy.context.scene;saved=(s.frame_current,r['transform']);report={'source':bpy.data.filepath,'rotor_sequence':[],'forewing_joint':[]}
def evaluated(name):
 o=bpy.data.objects[name];e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();v=[e.matrix_world@p.co for p in m.vertices];f=[tuple(p.vertices) for p in m.polygons];t=BVHTree.FromPolygons(v,f);e.to_mesh_clear();return v,t
def phase(p):r['transform']=p;r.update_tag();bpy.context.view_layer.update()
for p in [0.,.5,.82,.9,1.]:
 phase(p);report['rotor_sequence'].append({'phase':p,'blade_hinge_rad':bpy.data.objects['SB_BladeFold_1'].rotation_euler.z,'mast_z_m':bpy.data.objects['SB_MainRotorMast'].location.z})
phase(1.)
for side in [-1,1]:
 main,tree=evaluated('SB_MainWing_'+str(side));small,smalltree=evaluated('SB_FixedCockpitChine_'+str(side));gap=min(tree.find_nearest(p)[3] for p in small)
 samples=[Vector((.3,side*(.55+.57*i/100),1.5)) for i in range(101)];edgegap=min(tree.find_nearest(p)[3] for p in samples)
 report['forewing_joint'].append({'side':side,'sampled_back_edge_to_main_surface_min_m':edgegap,'small_mesh_vertex_to_main_surface_min_m':gap,'intersecting_triangle_pairs':len(tree.overlap(smalltree))})
 report.setdefault('front_cannons',[]).append({'side':side,'barrel_world_x_max_m':max(v.x for v in evaluated('SB_FrontWingCannonBarrel_'+str(side))[0]),'pod_world_x_max_m':max(v.x for v in evaluated('SB_FrontWingCannonPod_'+str(side))[0])})
phase(0.);blade=evaluated('SB_MainRotorBlade_1')[0];intakes=[p for n in ['SB_MetalAirIntake_-1','SB_MetalAirIntake_1'] for p in evaluated(n)[0]]
report['helicopter_rotor_to_intake_vertical_gap_m']=min(p.z for p in blade)-max(p.z for p in intakes)
R=bpy.data.objects['MilesMayhem_Rig'];report['driving_ankles_world']={name:list(R.matrix_world@R.pose.bones['foot.'+name].head) for name in ['L','R']}
floor=evaluated('SB_CockpitFloor')[0];report['floor_top_z_m']=max(p.z for p in floor)
report['nose_front_width_m']=2*max(abs(v.co.y) for v in bpy.data.objects['SB_NoseWedge'].data.vertices if v.co.x>3.1)
report['packed_paints']={name:bool(bpy.data.images[name].packed_file) for name in ['SB_MainWingPaint_V16','SB_FrontWingPaint_V16']}
report['invalid_drivers']=[o.name+':'+f.data_path for o in bpy.data.objects if o.animation_data for f in o.animation_data.drivers if not f.driver.is_valid]
s.frame_set(saved[0]);r['transform']=saved[1];r.update_tag();bpy.context.view_layer.update();(A/'revision_validation_v21.json').write_text(json.dumps(report,indent=2));print('REVISION_CHECK',json.dumps(report))
