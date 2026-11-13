import bpy
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Switchblade'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
root=bpy.data.objects['Switchblade_Control'];CURRENT=bpy.data.collections['Switchblade_Vehicle'];PARENT=root
o=bpy.data.objects['SB_CockpitRearBulkhead']
for v in o.data.vertices:v.co.z=2.12 if v.co.z>1.8 else .80
# Close lateral slots between the rounded keel and upper cockpit side walls.
widths=[(0,.63),(.35,.67),(1.10,.64),(1.75,.54),(2.22,.40)]
heights=[(0,.975),(.35,.94),(1.10,.965),(1.75,1.08),(2.22,1.305)]
for side in [-1,1]:
 o=bpy.data.objects['SB_CabinSideWall_'+str(side)]
 for i in [0,1,2]:
  p=o.data.vertices[i].co;p.z=profile(p.x,heights)-.025;p.y=side*(profile(p.x,widths)-.012)
# Proper inclined upper nose meeting the descending front of the glazing.
bpy.data.objects.remove(bpy.data.objects['SB_NoseWedge'],do_unlink=True)
sections=[(2.22,.40,1.13,1.60),(2.50,.33,1.14,1.53),(2.95,.15,1.16,1.27),(3.12,.04,1.19,1.22)]
vv=[];ff=[]
for x,w,lo,hi in sections:vv += [(x,-w*.70,lo),(x,w*.70,lo),(x,w,(lo+hi)/2),(x,w*.7,hi),(x,-w*.7,hi),(x,-w,(lo+hi)/2)]
for j in range(3):
 for i in range(6):ff.append((j*6+i,j*6+(i+1)%6,(j+1)*6+(i+1)%6,(j+1)*6+i))
ff += [tuple(reversed(range(6))),tuple(range(18,24))]
mesh('SB_NoseWedge',vv,ff,bpy.data.materials['SB_DeepNavyPaint'],bevel=.018)
root.update_tag();bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Switchblade_V9_Assembly.blend'),compress=True)
print('SHELL_CLOSED_AND_REAR_WALL_LOWERED')
