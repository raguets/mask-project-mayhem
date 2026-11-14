import bpy,math
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Manta';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
S.frame_set(1)
# Restore clean body topology before repeated swept Boolean cuts from V8.
with bpy.data.libraries.load(str(A/'Manta_V7_Assembly.blend'),link=False) as (src,dst):dst.objects=['MA_MainBody']
source=dst.objects[0];body=bpy.data.objects['MA_MainBody'];body.data=source.data.copy();bpy.data.objects.remove(source,do_unlink=True)
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
CURRENT=bpy.data.collections['Manta_Vehicle'];root=bpy.data.objects['Manta_Control'];PARENT=root
# Hinge is aft of the road tire, close to its outer face. This carries the tire
# farther out without a fictitious slide or counter-rotation.
for s in [-1,1]:
 wing=bpy.data.objects['MA_UnderbodyWingPivot_'+str(s)];delta=Vector((0,s*.10,0));wing.location+=delta
 for ob in wing.children:ob.matrix_parent_inverse.translation-=delta
cut=tube('TempRearSweptWell',(-1.34,-1.2,.32),(-1.34,1.2,.32),.355,None,N=96)
for v in cut.data.vertices:v.co.x=-1.34+(v.co.x+1.34)*1.30
m=body.modifiers.new('RearWheelContinuousSweptWell','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cut;bpy.context.view_layer.objects.active=body;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cut,do_unlink=True)
# Update rear arch lips to the actual clearance outline, removing obsolete arcs.
for ob in list(bpy.data.objects):
 if ob.type=='CURVE' and ob.name.startswith('MA_ArchLip'):
  points=[p.co.x for sp in ob.data.splines for p in sp.points]
  if points and sum(points)/len(points)<0:bpy.data.objects.remove(ob,do_unlink=True)
purple=body.data.materials[0]
for s in [-1,1]:path('MA_RearSweptArchLip', [(-1.34+.466*cos(a),s*.89,.32+.36*sin(a)) for a in seq(48,0,pi)],.012,purple)
root['wing_note']='Hinges X=-1.57m, Y=+/-0.85m, immediately aft of rear road tires. Wheels rotate rigidly with blades and become aft-facing turbines; no independent lateral slide. Stored wing X[-1.40,.80], |Y|<=.77.'
bpy.context.view_layer.update();S.frame_set(61);S.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Manta_V9_Assembly.blend'),compress=True)
print('V9_SAVED')
