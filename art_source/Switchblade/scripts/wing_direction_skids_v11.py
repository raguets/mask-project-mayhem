import bpy,math,bmesh
from pathlib import Path
from mathutils import Quaternion
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Switchblade'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
root=bpy.data.objects['Switchblade_Control'];bpy.context.scene.frame_set(121);root.update_tag();bpy.context.view_layer.update()
for side in [-1,1]:
 hinge=bpy.data.objects['SB_WingSweep_'+str(side)]
 # Reverse the fold sense, preserving the STORED contour by mirroring chord coordinates.
 for o in list(hinge.children):
  if o.type=='MESH':
   for v in o.data.vertices:v.co.x=-.60-v.co.x
   bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.reverse_faces(bm,faces=bm.faces);bm.to_mesh(o.data);bm.free();o.data.update()
  elif o.type=='CURVE':
   for sp in o.data.splines:
    for p in sp.points:p.co.x=-.60-p.co.x
 q=Quaternion((0,0,1),side*(pi/2+.12))@Quaternion((0,1,0),pi/2);axis,angle=q.to_axis_angle()
 drive(hinge,'rotation_quaternion',0,'cos('+str(angle/2)+'*(1-t))',[('t',root,'transform')])
 for i in range(3):drive(hinge,'rotation_quaternion',i+1,str(axis[i])+'*sin('+str(angle/2)+'*(1-t))',[('t',root,'transform')])
 # The final top normal now points outward in storage: exterior becomes upper wing.
 sk=bpy.data.objects['SB_SkidToCannon_'+str(side)]
 drive(sk,'location',2,'1.13-0.28*t',[('t',root,'transform')])
 drive(sk,'location',0,'-0.20+0.10*t',[('t',root,'transform')])
 for o in sk.children:
  if o.type=='MESH':
   for v in o.data.vertices:
    if v.co.x<-.47:v.co.x-=.22
root['kinematic_estimates']='Outer stored wing faces rotate UP to become upper wing; diagonal hinges and0.30m transient outward clearance estimated. Skids rotate to cannons below wings, slight0.10m forward carriage; rear rail length increased0.22m.'
root['latest_corrections']='V11: user-reversed wing fold direction, exterior-to-upper surface mapping; persistent patin/cannons below wings with longer aft rails. V10 cockpit and shoulder fit retained.'
root.update_tag();bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Switchblade_V11_Assembly.blend'),compress=True)
print('WING_DIRECTION_AND_UNDERWING_CANNONS_V11_SAVED')
