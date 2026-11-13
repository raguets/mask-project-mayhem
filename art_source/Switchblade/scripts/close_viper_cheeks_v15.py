import bpy
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Switchblade'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
R=bpy.data.objects['MilesMayhem_Rig'];CURRENT=bpy.data.collections['Miles_ViperMask'];PARENT=None
for side in [-1,1]:
 v=[(.171,side*.111,1.682),(.125,side*.140,1.675),(.095,side*.115,1.59),(.172,side*.067,1.565),(.190,side*.072,1.625)]
 o=mesh('MM_Viper_ClosedCheek_'+str(side),v,[(0,1,2,3,4)],bpy.data.materials['MM_ViperNavyShell'],bevel=.004);o.parent=R;o.vertex_groups.new(name='head').add(list(range(5)),1,'REPLACE');m=o.modifiers.new('MilesEditableSkin','ARMATURE');m.object=R;o.modifiers.new('CheekShellWall','SOLIDIFY').thickness=.006
 for k in ['hide_render','hide_viewport']:drive(o,k,None,'1-m',[('m',R,'mask_on')])
R.update_tag();bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Switchblade_V15_Assembly.blend'),compress=True)
print('VIPER_CHEEK_JOINTS_CLOSED_V15')
