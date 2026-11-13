import bpy,math
from pathlib import Path
from mathutils import Quaternion,Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Switchblade'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
root=bpy.data.objects['Switchblade_Control'];R=bpy.data.objects['MilesMayhem_Rig']
for side in [-1,1]:
 hinge=bpy.data.objects['SB_WingSweep_'+str(side)]
 q=Quaternion((0,0,1),side*(pi/2+.12))@Quaternion((0,1,0),-pi/2);axis,angle=q.to_axis_angle()
 drive(hinge,'rotation_quaternion',0,'cos('+str(angle/2)+'*(1-t))',[('t',root,'transform')])
 for i in range(3):drive(hinge,'rotation_quaternion',i+1,str(axis[i])+'*sin('+str(angle/2)+'*(1-t))',[('t',root,'transform')])
 drive(hinge,'location',1,str(side)+'*(0.69+0.10*(1-t)+0.30*sin(3.14159265359*t))',[('t',root,'transform')])
root['wing_taper_note']='User correction: stored wings wider beside cockpit, side edges converge aft by estimated6.9degrees; rear outline follows body.'
# Preserve convex underside but open its upper half: the cockpit is an actual well.
o=bpy.data.objects['SB_CabinBelly'];me=o.data;vv=[tuple(v.co) for v in me.vertices];faces=[]
for face in me.polygons:
 # Lower half of the circular cross sections, excluding upper closure end caps.
 center=face.center
 if len(face.vertices)==4 and (face.index%20) in range(5,15):faces.append(tuple(face.vertices))
new=bpy.data.meshes.new('SB_ConvexOpenCabinHull_Editable');new.from_pydata(vv,[],faces);new.update();new.materials.append(bpy.data.materials['SB_DeepNavyPaint']);o.data=new
for f in new.polygons:f.use_smooth=True
for m in list(o.modifiers):o.modifiers.remove(m)
o.modifiers.new('HullThickness','SOLIDIFY').thickness=.025
for ob in bpy.data.collections['Switchblade_Interior'].all_objects:ob.location.z-=.10
drive(R,'location',2,'0.20*v',[('v',R,'in_vehicle')])
# Remove inherited alternative hair source that was still visible over new scalp.
for ob in list(bpy.data.collections['Miles_Character'].all_objects):
 if 'ContinuousSweptHairCap' in ob.name:bpy.data.objects.remove(ob,do_unlink=True)
root.update_tag();R.update_tag();bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Switchblade_V7_Assembly.blend'),compress=True)
print('TAPER_COCKPIT_V7_SAVED')
