import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Manta';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
CURRENT=bpy.data.collections['Manta_Vehicle'];PARENT=bpy.data.objects['Manta_Control'];S.frame_set(1)
body=bpy.data.objects['MA_MainBody']
def subtract(cut,name):
 m=body.modifiers.new(name,'BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cut;bpy.context.view_layer.objects.active=body;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cut,do_unlink=True)
subtract(box('TempSlidingWell',(1.48,0,.92),(1.59,1.39,.90),None,0),'FunctionalHoodClearance')
subtract(box('TempReactorWell',(-1.95,0,.56),(1.05,1.04,.34),None,0),'FunctionalReactorWell')
# Open the complete front wheel swept recess by an additional 8 mm.
for x in [1.24]:subtract(tube('TempWheelSweep',(x,-1.15,.34),(x,1.15,.34),.355,None,N=80),'FrontWheelSweptRecess')
bpy.data.objects['MA_RearLightSpoilerHinge'].location.x-=.08
for n,dz in [('MA_CabinFloor',-.075),('MA_Underbody',-.045)]:
 for v in bpy.data.objects[n].data.vertices:v.co.z+=dz
for s in [-1,1]:
 wing=bpy.data.objects['MA_UnderbodyWingPivot_'+str(s)]
 for ob in wing.children:
  if ob.name.startswith('MA_RearWheelCarrier'):continue
  if ob.type=='MESH':
   for v in ob.data.vertices:v.co.z-=.08
  elif ob.type=='CURVE':ob.location.z-=.08
CURRENT=bpy.data.collections['Manta_Interior']
black=bpy.data.objects['MA_CabinFloor'].data.materials[0]
for s in [-1,1]:box('MA_SeatPedestal',(-.49,s*.37,.27),(.44,.40,.07),black,.013)
# Save once all driven states have been evaluated; no invalid driver accepted.
R=bpy.data.objects['VanessaWarfield_Rig'];R['driving_pose']=1.;R['in_vehicle']=1.;R['mask_on']=False;R.update_tag();S.frame_set(61);S.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Manta_V5_Assembly.blend'),compress=True)
print('V5_SAVED')
