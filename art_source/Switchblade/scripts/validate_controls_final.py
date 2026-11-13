import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Switchblade';s=bpy.context.scene;r=bpy.data.objects['Switchblade_Control'];saved=s.frame_current
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
def bounds(name):
 o=bpy.data.objects[name];e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();v=[e.matrix_world@p.co for p in m.vertices];e.to_mesh_clear();return {'min':[min(p[i] for p in v) for i in range(3)],'max':[max(p[i] for p in v) for i in range(3)]}
report={'source':bpy.data.filepath,'wing_sides':[]}
for side in [-1,1]:
 s.frame_set(1);r.update_tag();bpy.context.view_layer.update();h=bpy.data.objects['SB_WingSweep_'+str(side)];stored=h.matrix_world.to_3x3()@Vector((0,0,1))
 s.frame_set(121);r.update_tag();bpy.context.view_layer.update();deployed=h.matrix_world.to_3x3()@Vector((0,0,1));wing=bounds('SB_MainWing_'+str(side));skid=bounds('SB_LandingSkidCannon_'+str(side));cannon=bounds('SB_SkidCannonBarrel_'+str(side))
 report['wing_sides'].append({'side':side,'upper_surface_outward_in_storage_dot':stored.dot(Vector((0,side,0))),'upper_surface_up_deployed_dot':deployed.z,'skid_rail_under_wing_gap_m':wing['min'][2]-skid['max'][2],'barrel_under_wing_gap_m':wing['min'][2]-cannon['max'][2],'wing_bounds':wing,'rail_bounds':skid})
s.frame_set(1);r.update_tag();bpy.context.view_layer.update();glass=bounds('SB_MagentaFacetedGlazing');report['glazing_bounds']=glass
report['invalid_drivers']=[o.name+':'+f.data_path for o in bpy.data.objects if o.animation_data for f in o.animation_data.drivers if not f.driver.is_valid]
report['category']=r['vehicle_category'];report['no_gameplay_simulation']=True
s.frame_set(saved);r.update_tag();bpy.context.view_layer.update();(A/'control_validation_final.json').write_text(json.dumps(report,indent=2));print('CONTROL_VALIDATION',json.dumps(report))
