import bpy,gc,types,json
from pathlib import Path
lock=bpy.app.driver_namespace.get('_mask_asset_review_active')
if lock:
    expected='G:\\DEV\\mask-project-mayhem\\art_source\\Hurricane\\renders\\v2_review'
    assert Path(lock['output_dir']).resolve()==Path(expected).resolve()
    matches=[f for f in gc.get_objects() if isinstance(f,types.FunctionType) and f.__name__=='step' and f.__globals__.get('lock_token')==lock['token']]
    assert len(matches)==1,len(matches)
    fn=matches[0];namespace=fn.__globals__
    if bpy.app.timers.is_registered(fn):bpy.app.timers.unregister(fn)
    namespace['restore']();out=Path(lock['output_dir']);(out/'CANCELLED').write_text('Review stopped because flame paint creation failed before rendering; state restored.')
    print('INCOMPLETE_PAINT_REVIEW_CANCELLED')
else:print('NO_ACTIVE_REVIEW')
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
tri=tessellate_polygon([[Vector((0,0,0)),Vector((1,0,0)),Vector((1,1,0)),Vector((0,1,0))]])
print('TESSELLATE_RESULT',repr(tri),[type(x).__name__ for x in tri[0]])
