import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Hurricane';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
S.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Session_before_finish_v7.blend'),copy=True,compress=True)
exec(compile((A/'scripts/geometry.py').read_text(),'<geometry>','exec'))
# Conform dense editable paint by rays in its original projection plane. Nearest
# surface wrap can jump onto wheel-arch returns and produces the observed streaks.
stats=[]
for o in list(S.objects):
 if not str(o.get('HU_group','')).startswith('paint_'):continue
 sw=next((m for m in o.modifiers if m.type=='SHRINKWRAP'),None)
 if not sw:continue
 target=sw.target;side=1 if target.name.endswith('_L') else -1 if target.name.endswith('_R') else 0
 o.modifiers.remove(sw)
 for m in o.modifiers:
  if m.type=='SUBSURF':m.levels=2;m.render_levels=2
 dg=bpy.context.evaluated_depsgraph_get();e=target.evaluated_get(dg);tm=e.to_mesh();vv=[e.matrix_world@v.co for v in tm.vertices];ff=[list(f.vertices) for f in tm.polygons];tree=BVHTree.FromPolygons(vv,ff);e.to_mesh_clear()
 eo=o.evaluated_get(dg);me=bpy.data.meshes.new_from_object(eo,preserve_all_data_layers=True,depsgraph=dg);bad=set();inv=o.matrix_world.inverted()
 for v in me.vertices:
  p=o.matrix_world@v.co
  start=Vector((p.x,side*1.5,p.z)) if side else Vector((p.x,p.y,3.0));direction=Vector((0,-side,0)) if side else Vector((0,0,-1));hit=tree.ray_cast(start,direction,3.0)
  if hit[0] is None:bad.add(v.index)
  else:v.co=inv@(hit[0]+(Vector((0,side*.003,0)) if side else Vector((0,0,.003))))
 bm=bmesh.new();bm.from_mesh(me);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[f for f in bm.faces if any(v.index in bad for v in f.verts)],context='FACES');bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
 outward=Vector((0,side,0)) if side else Vector((0,0,1))
 if sum(f.normal.dot(outward)*f.calc_area() for f in bm.faces)<0:bmesh.ops.reverse_faces(bm,faces=bm.faces)
 bm.to_mesh(me);bm.free()
 for m in list(o.modifiers):o.modifiers.remove(m)
 o.data=me
 for f in me.polygons:f.use_smooth=True
 o['paint_note']='Dense editable ray-projected paint, clipped at real panel boundaries; 3mm outside offset, no nearest-surface wrapping across wheel arches.'
 stats.append({'object':o.name,'vertices':len(me.vertices),'faces':len(me.polygons),'missed_rays':len(bad)})
# A curved inset port cover and an axis following its actual slanted glass edge.
ROOT=bpy.data.objects['Hurricane_Control'];LIFT=bpy.data.objects['HU_UpperChassisLift'];hinge=bpy.data.objects['HU_WindshieldHatchHinge'];old=bpy.data.objects['HU_WindshieldCannonCover'];bpy.data.objects.remove(old,do_unlink=True)
def wind(y,t):return Vector((1.015-.35*t-.055*(y/.80)**2,-y*(1-.17*t),1.15+.49*t))
hinge.driver_remove('rotation_euler',2);hinge.location=wind(.34,.16);hinge.rotation_mode='AXIS_ANGLE';axis=(wind(.34,.78)-wind(.34,.16)).normalized();hinge.rotation_axis_angle=(0,*axis)
drive(hinge,'rotation_axis_angle',0,'1.65*min(1,w/.45)',[('w',ROOT,'_wind')]);hinge.update_tag();bpy.context.view_layer.update()
CURRENT=bpy.data.collections['HU_Body'];GROUP='windshield_hatch';PARENT=LIFT
patch('HU_WindshieldCannonCover',seq(16,.348,.712),seq(16,.172,.768),lambda y,t:wind(y,t)+Vector((.002,0,.0015)),bpy.data.materials['HU_ChassisGraphite'],root=hinge,sub=0,thick=.004,orient=(1,0,.7))
for o in S.objects:
 o.update_tag()
S.frame_set(151);S.frame_set(1);bpy.context.view_layer.update();S.name='Hurricane_V7_Assembly';S['asset']='Hurricane V7 - reduced lift, reinforced black chassis, right windshield cannon'
(A/'paint_projection_v7.json').write_text(json.dumps(stats,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(A/'Hurricane_V7_Assembly.blend'),compress=True);print('FINISH_V7_SAVED',stats)
