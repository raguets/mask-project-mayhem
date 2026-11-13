"""2026-11-13 user silhouette and hinge corrections, executed through MCP."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Switchblade'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
# Discard only known unsaved trajectory experiments after preserving them.
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Session_trajectory_trials.blend'),copy=True)
bpy.ops.wm.open_mainfile(filepath=str(A/'Switchblade_V4_Assembly.blend'))
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
CURRENT=bpy.data.collections['Switchblade_Vehicle'];root=bpy.data.objects['Switchblade_Control'];R=bpy.data.objects['MilesMayhem_Rig'];PARENT=root
navy=bpy.data.materials['SB_DeepNavyPaint'];edge=bpy.data.materials['SB_EdgeBlue'];orange=bpy.data.materials['SB_OrangeMarkings'];red=bpy.data.materials['SB_RedMarkings']
bpy.context.scene.frame_set(121);root.update_tag();bpy.context.view_layer.update()
# Canopy roof height matches the fixed tail deck, not a tall independent bubble.
for name in ['SB_MagentaFacetedGlazing','SB_CanopyRearFrame','SB_CanopyCenterSeam']:
 o=bpy.data.objects[name]
 def lower(p):p.z=1.53+(p.z-1.53)*.56
 if o.type=='MESH':
  for v in o.data.vertices:lower(v.co)
 elif o.type=='CURVE':
  for sp in o.data.splines:
   for p in sp.points:lower(p.co)
# Move hinge to lowered rear upper edge, preserving all current child world transforms.
can=bpy.data.objects['SB_CanopyHinge'];children=[(o,o.matrix_world.copy()) for o in can.children];can.location.z=2.13;bpy.context.view_layer.update()
for o,mat in children:o.matrix_world=mat
# Continuous convex underside and rising nose extending the front glazing slope.
for name in ['SB_CabinBelly','SB_NoseWedge']:
 if bpy.data.objects.get(name):bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
def loft(name,sections):
 vv=[];ff=[];N=20
 for x,w,lo,hi in sections:
  for i in range(N):
   a=2*pi*i/N;y=w*sin(a);z=(hi+lo)/2+(hi-lo)/2*cos(a);vv.append((x,y,z))
 for j in range(len(sections)-1):
  for i in range(N):ff.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
 ff += [tuple(reversed(range(N))),tuple((len(sections)-1)*N+i for i in range(N))]
 return mesh(name,vv,ff,navy,smooth=True,bevel=.01)
loft('SB_CabinBelly',[(0,.63,.78,1.17),(.35,.67,.68,1.20),(1.10,.64,.70,1.23),(1.75,.54,.86,1.30),(2.22,.40,1.13,1.48)])
# Four flatter upper nose facets continue the glazing, while the keel is convex.
loft('SB_NoseWedge',[(2.22,.40,1.13,1.54),(2.52,.34,1.25,1.40),(2.78,.23,1.30,1.34),(2.98,.06,1.315,1.325)])
for side in [-1,1]:
 old=bpy.data.objects['SB_CabinSideWall_'+str(side)]
 for v in old.data.vertices:
  if v.co.z<1.4:v.co.z-=.20*(1-abs(v.co.x-1)/2)
 # Remove former wings/markings/hinges, preserving no stale driver experiment.
 names=['SB_WingSweep_'+str(side),'SB_WingFold_'+str(side)]
 for o in list(bpy.data.objects):
  if any(k in o.name for k in ['SB_MainWing_'+str(side),'SB_WingOrangeFlash_'+str(side),'SB_WingRedFlash_'+str(side),'SB_WingPanelLine_'+str(side)]):bpy.data.objects.remove(o,do_unlink=True)
 for name in reversed(names):bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
 hinge=empty('SB_WingSweep_'+str(side),(-.30,side*.69,1.50),root);hinge.rotation_mode='QUATERNION'
 # Single diagonal rotation maps the final XY wing exactly onto the XZ tail contour.
 drive(hinge,'rotation_quaternion',0,'cos(1.0471975512*(1-t))',[('t',root,'transform')])
 for i,factor in [(1,side*.5773502692),(2,-.5773502692),(3,side*.5773502692)]:drive(hinge,'rotation_quaternion',i,str(factor)+'*sin(1.0471975512*(1-t))',[('t',root,'transform')])
 drive(hinge,'location',1,str(side)+'*(0.69+0.30*sin(3.14159265359*t))',[('t',root,'transform')])
 # At rest the four edges follow the fixed rear side silhouette; straight trailing edge.
 pts=[(.36,side*.71),(.24,side*3.84),(-.27,side*3.84),(-.77,side*.71)]
 def prism(name,poly,z,thick,mat):
  vv=[(x,y,z+d) for d in [-thick/2,thick/2] for x,y in poly];N=len(poly);ff=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)];return mesh(name,vv,ff,mat,hinge,bevel=.015)
 prism('SB_MainWing_'+str(side),pts,1.50,.07,navy)
 # Narrow graphic shapes on both sides, no detached stacked decal blocks.
 for z in [1.539,1.461]:
  prism('SB_WingOrangeFlash_'+str(side),[(.24,side*1.01),(.20,side*1.77),(-.04,side*2.57),(.02,side*1.37)],z,.002,orange)
  prism('SB_WingRedFlash_'+str(side),[(.05,side*1.12),(-.12,side*1.80),(-.16,side*2.53),(-.08,side*1.51)],z+(.003 if z>1.5 else -.003),.002,red)
 path('SB_WingPanelLine_'+str(side),[(.29,side*.90,1.54),(.18,side*3.66,1.54),(-.20,side*3.66,1.54)],.006,edge,hinge)
 # Shorter aft skid rail and forward travel reserve the rotating wing's swept region.
 sk=bpy.data.objects['SB_SkidToCannon_'+str(side)]
 drive(sk,'rotation_euler',0,str(side)+'*1.57079632679*t',[('t',root,'transform')])
 drive(sk,'location',2,'1.13+0.24*t',[('t',root,'transform')])
 drive(sk,'location',0,'-0.20+1.15*t',[('t',root,'transform')])
 for o in list(sk.children):
  if o.type=='MESH':
   for v in o.data.vertices:
    if v.co.x<-.5:v.co.x=-.5+(v.co.x+.5)*.08
 # Fixed small chine ends meet the main wing at the same height.
 for o in bpy.data.objects:
  if o.name=='SB_FixedCockpitChine_'+str(side):
   for v in o.data.vertices:v.co.z+=.01
# Tail fin pivots aft in the vertical longitudinal plane, never sideways.
fin=bpy.data.objects['SB_TailRotorToFin'];fin.driver_remove('rotation_euler',0);fin.rotation_euler.x=0
drive(fin,'rotation_euler',1,'3.14159265359*t',[('t',root,'transform')])
# Cabin contents and same articulated pilot descend under the corrected canopy.
for o in bpy.data.collections['Switchblade_Interior'].all_objects:o.location.z-=.35
drive(R,'location',2,'0.30*v',[('v',R,'in_vehicle')])
# Keep decorative shirt layers distinct and belt visible over the broadened jacket.
for o in bpy.data.collections['Miles_Character'].all_objects:
 if o.type=='MESH' and 'Belt' in o.name:
  for v in o.data.vertices:v.co.x*=1.20;v.co.y*=1.14
 if o.name=='MM_FabricCollar':
  for i in range(len(o.data.materials)):o.data.materials[i]=bpy.data.materials['MM_LightBlueLeather']
mat=bpy.data.materials['MM_SilverGreyHair'];mat.diffuse_color=(.15,.17,.19,1);next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'].default_value=(.15,.17,.19,1)
root['kinematic_estimates']='Diagonal wing hinges with0.30m transient outward clearance; patin/cannon forward carriage1.15m and rise0.24m; hidden linkage interpreted, dimensions estimated. All major mechanisms start together.'
root['user_corrections']='2026-11-13: wings match rear side outline, low canopy matching tail deck, continuous convex forward underside/nose, tail fin pivots aft vertically.'
bpy.context.scene.frame_set(1);root.update_tag();R.update_tag();bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Switchblade_V6_Assembly.blend'),compress=True)
print('USER_CORRECTIONS_V6_SAVED')
