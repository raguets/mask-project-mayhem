import bpy,gc,types
from pathlib import Path
lock=bpy.app.driver_namespace.get('_mask_asset_review_active')
if lock:
    assert Path(lock['output_dir']).resolve()==Path('G:/DEV/mask-project-mayhem/art_source/Hurricane/renders/v2_review').resolve()
    matches=[f for f in gc.get_objects() if isinstance(f,types.FunctionType) and f.__name__=='step' and f.__globals__.get('lock_token')==lock['token']]
    assert len(matches)==1
    fn=matches[0]
    if bpy.app.timers.is_registered(fn):bpy.app.timers.unregister(fn)
    fn.__globals__['restore']();(Path(lock['output_dir'])/'CANCELLED').write_text('Stopped for user corrections: lower body lift, taller black understructure, right windshield cannon. Scene restored.')
    print('USER_CORRECTION_REVIEW_STOPPED')
else:print('NO_ACTIVE_REVIEW')
