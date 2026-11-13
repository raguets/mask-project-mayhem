import bpy
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Switchblade'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
root=bpy.data.objects['Switchblade_Control'];CURRENT=bpy.data.collections['Switchblade_Vehicle'];PARENT=root
def keel(x):return .91+(x-1.10)*(.25/2.02)
# Front keel and nose underside lie on the same straight longitudinal line.
o=bpy.data.objects['SB_CabinBelly']
for v in o.data.vertices:
 p=v.co
 if p.x>1.11 and p.z<1.20:
  if abs(p.y)<.50 or p.z<1.10:p.z=keel(p.x)+(.075 if abs(p.y)>.50 else 0)
# Explicitly set lower/chamfer loops, avoiding changes to the upper side joint.
for section,x in [(3,1.75),(4,2.22)]:
 for i in [1,2,3,4]:o.data.vertices[section*6+i].co.z=keel(x)+(.075 if i in [1,4] else 0)
bpy.data.objects.remove(bpy.data.objects['SB_NoseWedge'],do_unlink=True)
# The only exposed upper nose section continues the last windshield plane.
front_glass_top=1.53+(1.60-1.53)*.56-.035*.56
# Actual central roof mesh height at x2.5 is1.5496; bevel rounds the last millimetres.
gl=bpy.data.objects['SB_MagentaFacetedGlazing'];roof_tip=max(v.co.z for v in gl.data.vertices if abs(v.co.x-2.5)<.001)
roof_previous=max(v.co.z for v in gl.data.vertices if abs(v.co.x-2.12)<.001)
slope=(roof_tip-roof_previous)/(2.5-2.12)
upper=lambda x:roof_tip+slope*(x-2.5)
sections=[(2.22,.40,keel(2.22),1.515),(2.50,.33,keel(2.50),roof_tip),(3.12,.12,keel(3.12),upper(3.12))]
vv=[];ff=[]
for x,w,lo,hi in sections:vv += [(x,-w*.7,lo),(x,w*.7,lo),(x,w,(lo+hi)/2),(x,w*.7,hi),(x,-w*.7,hi),(x,-w,(lo+hi)/2)]
for j in range(2):
 for i in range(6):
  if j==0 and i==3:continue # covered by the front glazing; no reversed exposed upper slope
  ff.append((j*6+i,j*6+(i+1)%6,(j+1)*6+(i+1)%6,(j+1)*6+i))
ff += [tuple(reversed(range(6))),tuple(range(12,18))]
mesh('SB_NoseWedge',vv,ff,bpy.data.materials['SB_DeepNavyPaint'],bevel=.009)
root['nose_profile_note']='V18: wider24cm front, top follows actual last glazing plane, underside collinear with forward keel; hidden under-glass transition estimated.'
root.update_tag();bpy.context.scene.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Switchblade_V18_Assembly.blend'),compress=True)
print('NOSE_V18_STRAIGHTENED',roof_tip,roof_previous,upper(3.12),keel(3.12))
