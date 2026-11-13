import bpy
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Switchblade'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
root=bpy.data.objects['Switchblade_Control'];bpy.context.scene.frame_set(121);root.update_tag();bpy.context.view_layer.update()
# Broader, more swept leading planform, preserving the straight trailing edge.
def wing_shape(p):
 sign=1 if p.y>0 else -1;t=max(0,min(1,(abs(p.y)-.71)/3.13));oldfront=.17-.74*t;newfront=.30-.91*t;p.x=-.96+(p.x+.96)/(oldfront+.96)*(newfront+.96);p.y=sign*(.71+(abs(p.y)-.71)*1.06)
for side in [-1,1]:
 for ob in bpy.data.objects['SB_WingSweep_'+str(side)].children:
  if ob.type=='MESH':
   for v in ob.data.vertices:wing_shape(v.co)
   ob.data.update()
  elif ob.type=='CURVE':
   for sp in ob.data.splines:
    for p in sp.points:wing_shape(p.co)
 sk=bpy.data.objects['SB_SkidToCannon_'+str(side)];drive(sk,'location',0,'-0.38+0.10*t',[('t',root,'transform')])
 ob=bpy.data.objects['SB_BentSkidStrut_'+str(side)]
 for i,j in [(0,9),(1,8),(2,7),(3,6),(4,5)]:
  a=ob.data.vertices[i].co.copy();b=ob.data.vertices[j].co.copy();mid=(a+b)*.5
  ob.data.vertices[i].co=mid+(a-mid)*1.25;ob.data.vertices[j].co=mid+(b-mid)*1.25
 ob.modifiers['SweptStrutThickness'].thickness=.095
 for name in ['SB_Tailplane_'+str(side),'SB_TailStripe_'+str(side)]:
  ob=bpy.data.objects[name]
  for v in ob.data.vertices:
   p=v.co;p.x=-3.8+(p.x+3.8)*1.10;p.y=side*(.11+(abs(p.y)-.11)*1.14)
# Interior floor and control column no longer protrude below the rising keel.
floor=bpy.data.objects['SB_CockpitFloor']
for v in floor.data.vertices:
 if v.co.x>1.5:v.co.x=1.15
 if v.co.z<1.20:v.co.z=1.225
column=bpy.data.objects['SB_ControlColumn']
for sp in column.data.splines:
 for p in sp.points:
  if p.co.z<1.40:p.co.z=1.43
root['latest_corrections']='V17: patins18cm farther aft; curved supports25% wider and9.5cm thick; wings6% more span and broader root with stronger leading sweep; rear tailplanes14% wider and10% more chord; interior floor/column no longer protrude below keel.'
root.update_tag();bpy.context.scene.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Switchblade_V17_Assembly.blend'),compress=True)
print('PROPORTIONS_AND_KEEL_CLEANUP_V17_SAVED')
