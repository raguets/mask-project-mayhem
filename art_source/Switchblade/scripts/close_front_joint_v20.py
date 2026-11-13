import bpy
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Switchblade'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
root=bpy.data.objects['Switchblade_Control'];CURRENT=bpy.data.collections['Switchblade_Vehicle'];PARENT=root;navy=bpy.data.materials['SB_DeepNavyPaint']
# Rear cabin wall tapers into the shallower keel instead of hanging below its sides.
bpy.data.objects.remove(bpy.data.objects['SB_CockpitRearBulkhead'],do_unlink=True)
yz=[(-.63,1.17),(-.63,2.12),(.63,2.12),(.63,1.17),(.42,.90),(-.42,.90)]
vv=[(x,y,z) for x in [-.075,.005] for y,z in yz];ff=[tuple(reversed(range(6))),tuple(range(6,12))]+[(i,(i+1)%6,(i+1)%6+6,i+6) for i in range(6)]
mesh('SB_CockpitRearBulkhead',vv,ff,navy,bevel=.012)
# The nose rear loop matches the real hull loop exactly, closing the former profile step.
bpy.data.objects.remove(bpy.data.objects['SB_NoseWedge'],do_unlink=True)
def lo(x):return .91+(x-1.10)*(.25/2.02)
gl=bpy.data.objects['SB_MagentaFacetedGlazing'];top=max(v.co.z for v in gl.data.vertices if abs(v.co.x-2.5)<.001);prior=max(v.co.z for v in gl.data.vertices if abs(v.co.x-2.12)<.001);slope=(top-prior)/.38
sections=[(2.22,.40,.40,.264,lo(2.22),lo(2.22)+.075,1.52),(2.5,.33,.211,.231,lo(2.5),(lo(2.5)+top)/2,top),(3.12,.12,.084,.084,lo(3.12),(lo(3.12)+top+slope*.62)/2,top+slope*.62)]
vv=[];ff=[]
for x,w,wt,wb,zl,zm,zh in sections:vv += [(x,-wt,zh),(x,-w,zm),(x,-wb,zl),(x,wb,zl),(x,w,zm),(x,wt,zh)]
for j in range(2):
 for i in range(6):
  if j==0 and i==5:continue # under the front glazing
  ff.append((j*6+i,j*6+(i+1)%6,(j+1)*6+(i+1)%6,(j+1)*6+i))
ff += [tuple(range(12,18))]
mesh('SB_NoseWedge',vv,ff,navy,bevel=.006)
root['latest_corrections']='V20: latest forward-curved broad supports, swept broader forewings with square gap and two front cannons, more prominent intakes; front keel/nose loops matched, rear cabin wall contained inside keel. V16–V19 shape corrections preserved.'
root.update_tag();bpy.context.scene.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Switchblade_V20_Assembly.blend'),compress=True)
print('CLOSED_KEEL_AND_NOSE_JOIN_V20')
