import bpy
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Switchblade'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
CURRENT=bpy.data.collections['Switchblade_Vehicle'];root=bpy.data.objects['Switchblade_Control'];PARENT=root
navy=bpy.data.materials['SB_DeepNavyPaint'];edge=bpy.data.materials['SB_EdgeBlue'];black=bpy.data.materials['SB_BlackMechanism']
bpy.data.objects.remove(bpy.data.objects['SB_FuselageLower'],do_unlink=True)
def loft(name,sections):
 vv=[];ff=[]
 for x,w,lo,hi in sections:vv += [(x,-w*.72,lo),(x,w*.72,lo),(x,w,lo+.07),(x,w,hi-.05),(x,w*.72,hi),(x,-w*.72,hi),(x,-w,hi-.05),(x,-w,lo+.07)]
 for j in range(len(sections)-1):
  for i in range(8):ff.append((j*8+i,j*8+(i+1)%8,(j+1)*8+(i+1)%8,(j+1)*8+i))
 ff += [tuple(reversed(range(8))),tuple((len(sections)-1)*8+i for i in range(8))]
 return mesh(name,vv,ff,navy,bevel=.025)
loft('SB_FixedTailFuselage',[(-4.05,.10,1.72,1.99),(-3.65,.22,1.60,2.03),(-1.25,.57,1.03,2.12),(-.35,.65,1.03,2.16),(-.04,.64,1.05,2.20)])
loft('SB_CabinBelly',[(0,.65,1.05,1.29),(1.65,.61,1.13,1.31),(2.22,.43,1.30,1.48)])
loft('SB_NoseWedge',[(2.20,.44,1.30,1.49),(2.65,.33,1.36,1.51),(3.10,.10,1.42,1.49)])
for s in [-1,1]:
 v=[(0,s*.64,1.15),(1.64,s*.60,1.23),(2.22,s*.42,1.38),(2.22,s*.42,1.50),(1.64,s*.60,1.51),(0,s*.64,1.59)]
 o=mesh('SB_CabinSideWall_'+str(s),v,[(0,1,2,3,4,5)],navy,bevel=.018);o.modifiers.new('SideWallThickness','SOLIDIFY').thickness=.05
 for i in range(4):box('SB_EngineSideVent',(-.50-i*.12,s*.64,1.30),(.065,.018,.14),black,.008)
# Lower the cabin floor to make room for actual seated feet; retain continuous belly.
bpy.data.objects['SB_CockpitFloor'].location.z=-.01
root.update_tag();bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Switchblade_V2_Vehicle.blend'),compress=True)
print('BODY_V2_FIXED')
