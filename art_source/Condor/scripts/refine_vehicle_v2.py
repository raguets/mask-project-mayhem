import bpy,math
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Condor'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
CURRENT=bpy.data.collections['Condor_Vehicle'];root=bpy.data.objects['Condor_Control'];PARENT=root
green=bpy.data.materials['Condor_LimePaint'];green.diffuse_color=(.13,.57,.004,1);next(n for n in green.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'].default_value=green.diffuse_color
black=bpy.data.materials['Condor_Charcoal'];chrome=bpy.data.materials['Condor_WheelAlloy']
for side in [-1,1]:
 blade=bpy.data.objects['Condor_BladeHinge_'+str(side)];blade.driver_remove('rotation_euler',0);blade.rotation_euler=(0,0,0);drive(blade,'rotation_euler',2,str(side)+'*1.570796*(1-t)',[('t',root,'transform')])
 # Fold both blades forward alongside the rear cowl in road state.
 arm=bpy.data.objects['Condor_MastArm'+('' if side==-1 else '.001')]
 # Fairing drops around the engine sides as on the original toy, leaving leg pockets.
 poly=[(.66,side*.30,.84),(.52,side*.30,.71),(.40,side*.27,.36),(.20,side*.25,.27),(.36,side*.27,.24),(.57,side*.30,.33),(.79,side*.32,.72)]
 o=mesh('Condor_LowerFairing_'+str(side),poly,[tuple(range(7))],green,bevel=.02);o.modifiers.new('PanelWall','SOLIDIFY').thickness=.022
 o=bpy.data.objects['Condor_BlackSideInset'+('' if side==-1 else '.001')]
 for v in o.data.vertices:v.co.y=side*(abs(v.co.y)+.021)
 # Triangular tail graphics and broad panel joins.
 path('Condor_TailGraphic_'+str(side),[(-1.30,side*.19,.63),(-1.00,side*.25,.61),(-.46,side*.249,.61)],.009,black)
gun=bpy.data.objects['Condor_HeadlampCannon'];tube('Condor_CannonTelescopicSleeve',(1.09,0,.79),(1.35,0,.79),.021,black,root=gun)
rear=bpy.data.objects['Condor_RearWheelPivot']
for o in list(CURRENT.all_objects):
 if o.name.startswith('Condor_RearSwingArm'):
  # Keep fork mechanically attached to pivot instead of loose dangling bars.
  pass
# Wider blade root bridge, structurally ties both mast arms to center spindle.
mast=bpy.data.objects['Condor_RotorSupport'];tube('Condor_MastCrossBridge',(-1.94,-.33,.32),(-1.94,.33,.32),.030,black,root=mast)
bpy.context.scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(A/'Condor_V2_Assembly.blend'),compress=True)
print('VEHICLE_V2_CORRECTED')
