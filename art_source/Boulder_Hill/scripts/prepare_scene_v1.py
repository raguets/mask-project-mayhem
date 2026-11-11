"""Preserve live Blender state, create a new environment scene, measure real vehicle assets."""
import bpy,json,datetime,math
from pathlib import Path
from mathutils import Vector,Matrix
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Boulder_Hill';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
assert not (A/'BoulderHill_V1_Assembly.blend').exists()
bpy.ops.wm.save_as_mainfile(filepath=str(A/('Session_before_BoulderHill_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.blend')),copy=True,compress=True)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.shading.type='SOLID'
for ob in list(bpy.data.objects):bpy.data.objects.remove(ob,do_unlink=True)
for c in list(bpy.data.collections):bpy.data.collections.remove(c)
S.name='BoulderHill_V1_Environment';S.unit_settings.system='METRIC';S.unit_settings.scale_length=1;S.frame_set(1);S['BoulderVersion']='V1 preparing'
report={'previous_session_preserved':True,'assets':{}}
for label,path,collections in [('Thunderhawk',P/'art_source/Thunderhawk/Thunderhawk_V14_Vehicle.blend',['THK9_Exterior','THK11_Interior']),('Rhino',P/'art_source/Rhino/Rhino_V3_Vehicle.blend',['Rhino_Truck','Rhino_RearVehicle','Rhino_Interior'])]:
 with bpy.data.libraries.load(str(path),link=False) as (src,dst):dst.collections=collections
 container=bpy.data.collections.new('BH_Demo_'+label);S.collection.children.link(container)
 for c in dst.collections:container.children.link(c)
 objs=list(container.all_objects);S.frame_set(1);bpy.context.view_layer.update()
 for name in ['Rhino_Control','THK_Root']:
  r=bpy.data.objects.get(name)
  if r and r in objs:
   if 'battle_mode' in r:r['battle_mode']=0.;r.update_tag()
 bpy.context.view_layer.update();matrices={o:o.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.copy() for o in objs}
 for o in objs:o.animation_data_clear()
 for o,matrix in matrices.items():o.matrix_world=matrix
 bpy.context.view_layer.update();pts=[]
 for o in objs:
  if o.type not in ['MESH','CURVE','FONT'] or o.hide_render:continue
  ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();pts.extend(ev.matrix_world@v.co for v in me.vertices);ev.to_mesh_clear()
 bounds=([min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]);center=Vector(((bounds[0][0]+bounds[1][0])/2,(bounds[0][1]+bounds[1][1])/2,bounds[0][2]))
 actor=bpy.data.objects.new('BH_'+label+'_PathRoot',None);container.objects.link(actor);offset=bpy.data.objects.new('BH_'+label+'_GeometryOffset',None);container.objects.link(offset);offset.parent=actor;offset.location=-center
 for ob in objs:
  if ob.parent not in objs:ob.parent=offset;ob.matrix_parent_inverse.identity()
 actor.location=(-5.6,15 if label=='Thunderhawk' else 33,0)
 report['assets'][label]={'source':str(path),'bounds_before_centering':bounds,'length':bounds[1][0]-bounds[0][0],'width':bounds[1][1]-bounds[0][1],'height':bounds[1][2]-bounds[0][2],'frozen_road_geometry':True,'objects':len(objs),'original_vehicle_file_unchanged':True}
(A/'vehicle_measurements_v1.json').write_text(json.dumps(report,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(A/'BoulderHill_prepared_v1.blend'),compress=True);print('BOULDER_VEHICLES_MEASURED',json.dumps(report))
