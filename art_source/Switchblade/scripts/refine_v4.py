import bpy,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Switchblade'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
root=bpy.data.objects['Switchblade_Control'];R=bpy.data.objects['MilesMayhem_Rig'];R['driving_pose']=0.;R['in_vehicle']=0.;R['mask_on']=False;R.update_tag();bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
# Distinct garment layer offsets prevent overlapping shirt/tie/lapel surfaces.
for name,offset in [('MM_NarrowTie',.005),('MM_JacketLapel_-1',.010),('MM_JacketLapel_1',.010)]:
 for v in bpy.data.objects[name].data.vertices:v.co.x+=offset
CURRENT=bpy.data.collections['Miles_Character'];PARENT=None
def bind(o,bone='head'):
 o.vertex_groups.new(name=bone).add(list(range(len(o.data.vertices))),1,'REPLACE');o.parent=R;m=o.modifiers.new('MilesEditableSkin','ARMATURE');m.object=R;m.use_deform_preserve_volume=True;return o
for o in list(CURRENT.all_objects):
 if 'ShoulderAiguillette' in o.name:bpy.data.objects.remove(o,do_unlink=True)
cloth=bpy.data.objects['MM_ContinuousFlightSuit'];dg=bpy.context.evaluated_depsgraph_get();ev=cloth.evaluated_get(dg);me=ev.to_mesh();tree=BVHTree.FromPolygons([v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons]);ev.to_mesh_clear()
for layer in range(3):
 pts=[]
 for u in seq(60):
  y=.14+.065*math.sin(2*pi*u)+layer*.004;z=1.355+.10*math.cos(2*pi*u);hit=tree.ray_cast(Vector((.5,y,z)),Vector((-1,0,0)),1.)
  if hit[0]:pts.append(tuple(hit[0]+hit[1]*(.009+layer*.002)))
 cu=path('MM_FittedGoldAiguillette',pts,.003,bpy.data.materials['MM_GoldBraid']);me=bpy.data.meshes.new_from_object(cu.evaluated_get(dg),depsgraph=dg);o=bpy.data.objects.new(cu.name+'_Mesh',me);CURRENT.objects.link(o);bpy.data.objects.remove(cu,do_unlink=True);bind(o,'spine')
# Solid sculpted chin/cheek piece covers the retained mouth.
CURRENT=bpy.data.collections['Miles_ViperMask'];SHELL=bpy.data.materials['MM_ViperNavyShell'];DARK=bpy.data.materials['MM_BootLeather']
v=[(.171,-.111,1.682),(.171,.111,1.682),(.190,.072,1.625),(.172,.067,1.565),(.172,-.067,1.565),(.190,-.072,1.625)]
o=bind(mesh('MM_Viper_ChinShell',v,[(0,1,2,3,4,5)],SHELL,bevel=.008));o.modifiers.new('ChinShellWall','SOLIDIFY').thickness=.008
for k in ['hide_render','hide_viewport']:drive(o,k,None,'1-m',[('m',R,'mask_on')])
vv=[];ff=[];N=48
for z,rx,ry in [(1.46,.092,.105),(1.59,.106,.112)]:
 for i in range(N):a=2*pi*i/N;vv.append((-.02+rx*cos(a),ry*sin(a),z))
for i in range(N):ff.append((i,(i+1)%N,(i+1)%N+N,i+N))
o=bind(mesh('MM_Viper_InterpretedFlexibleNeck',vv,ff,DARK,smooth=True),'neck')
for k in ['hide_render','hide_viewport']:drive(o,k,None,'1-m',[('m',R,'mask_on')])
# Trial faster skid deployment; starts with the other mechanisms, nonlinear rate estimated.
for side in [-1,1]:
 skid=bpy.data.objects['SB_SkidToCannon_'+str(side)]
 drive(skid,'rotation_euler',0,str(side)+'*1.57079632679*sqrt(t)',[('t',root,'transform')])
 drive(skid,'location',2,'1.13+0.24*sqrt(t)',[('t',root,'transform')])
R['in_vehicle']=1.;R['driving_pose']=1.;R['mask_on']=True;root.update_tag();R.update_tag();bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Switchblade_V4_Assembly.blend'),compress=True)
print('REFINED_V4_SAVED')
