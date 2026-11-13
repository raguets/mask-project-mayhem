import bpy,gc,types
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Condor'
lock=bpy.app.driver_namespace.get('_mask_asset_review_active')
if lock:
 assert Path(lock['output_dir']).resolve()==(A/'renders/v6_review').resolve()
 fs=[f for f in gc.get_objects() if isinstance(f,types.FunctionType) and f.__name__=='step' and f.__globals__.get('lock_token')==lock['token']];assert len(fs)==1
 fn=fs[0]
 if bpy.app.timers.is_registered(fn):bpy.app.timers.unregister(fn)
 fn.__globals__['restore']();(A/'renders/v6_review/CANCELLED').write_text('Stopped for user request: lateral glass continues down to green chassis.')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
CURRENT=bpy.data.collections['Condor_Vehicle'];PARENT=bpy.data.objects['Condor_Control'];glass=bpy.data.materials['Condor_SmokeWindshield'];black=bpy.data.materials['Condor_Charcoal']
for o in list(CURRENT.all_objects):
 if o.name.startswith(('Condor_FacetedWindshield','Condor_WindshieldPerimeter')):bpy.data.objects.remove(o,do_unlink=True)
v=[(1.20,-.18,.99),(1.20,.18,.99),(.64,.19,1.44),(.64,-.19,1.44),(1.10,-.32,.94),(.56,-.285,1.38),(1.10,.32,.94),(.56,.285,1.38),(.49,-.30,.92),(.49,.30,.92)]
o=mesh('Condor_FacetedWindshield',v,[(0,1,2,3),(4,0,3,5,8),(1,6,9,7,2)],glass,smooth=False);o.modifiers.new('GlassThickness','SOLIDIFY').thickness=.006;o.modifiers.new('GlassEdgeSoftening','BEVEL').width=.002
path('Condor_WindshieldPerimeter',[v[i] for i in [8,4,0,1,6,9,7,2,3,5,8]],.007,black)
o['user_note']='Side returns extend all the way to green chassis, user correction 2026-11-12.'
bpy.context.scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(A/'Condor_V7_Assembly.blend'),compress=True)
print('SIDE_GLASS_EXTENDED_V7')
