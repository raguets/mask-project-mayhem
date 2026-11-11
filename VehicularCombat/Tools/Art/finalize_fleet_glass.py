"""Enable the refraction method explicitly on the three new vehicle glass masters."""
import unreal,json,traceback
from pathlib import Path
report={'passed':False,'materials':[]}
try:
    for name in ('Thunderhawk','Rhino','Hurricane'):
        path='/Game/MASK/'+name+'/Materials/M_MASK_Glass'
        mat=unreal.EditorAssetLibrary.load_asset(path)
        if not mat:raise RuntimeError('Missing '+path)
        mat.set_editor_property('refraction_method',unreal.RefractionMode.RM_PIXEL_NORMAL_OFFSET)
        unreal.MaterialEditingLibrary.recompile_material(mat)
        if not unreal.EditorAssetLibrary.save_loaded_asset(mat,False):raise RuntimeError('Could not save '+path)
        report['materials'].append({'path':mat.get_path_name(),'refraction':str(mat.get_editor_property('refraction_method'))})
    report['passed']=True
except Exception:report['error']=traceback.format_exc();unreal.log_error(report['error'])
finally:
    (Path(unreal.Paths.project_dir())/'Saved/Art/fleet-glass-finalize.json').write_text(json.dumps(report,indent=2))
