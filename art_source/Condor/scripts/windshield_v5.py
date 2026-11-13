import bpy
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Condor'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
CURRENT=bpy.data.collections['Condor_Vehicle'];PARENT=bpy.data.objects['Condor_Control'];glass=bpy.data.materials['Condor_SmokeWindshield'];black=bpy.data.materials['Condor_Charcoal']
for o in list(CURRENT.all_objects):
 if o.name.startswith('Condor_Windshield'):bpy.data.objects.remove(o,do_unlink=True)
v=[(1.20,-.18,.99),(1.20,.18,.99),(.64,.19,1.44),(.64,-.19,1.44),(1.10,-.29,.97),(.56,-.285,1.38),(1.10,.29,.97),(.56,.285,1.38)]
o=mesh('Condor_FacetedWindshield',v,[(0,1,2,3),(4,0,3,5),(1,6,7,2)],glass,smooth=False);o.modifiers.new('GlassThickness','SOLIDIFY').thickness=.006;o.modifiers.new('GlassEdgeSoftening','BEVEL').width=.002
path('Condor_WindshieldPerimeter',[v[i] for i in [4,0,1,6,7,2,3,5,4]],.007,black)
PARENT['windshield_note']='User correction 2026-11-12: planar central screen plus two angled side returns, sharp visible transitions.'
bpy.context.scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(A/'Condor_V5_Assembly.blend'),compress=True)
print('FACETED_WINDSHIELD_SAVED')
