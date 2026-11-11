"""Persist existing atlas material assignments; write struct values back to arrays."""
import unreal,json,re,traceback
from pathlib import Path
report={'passed':False,'meshes':[]};lib=unreal.EditorAssetLibrary
try:
    families={'Thunderhawk':{'SK_Matt':'MattBody','SK_MattHair':'MattHair','SK_Spectrum':'Spectrum'},
              'Rhino':{'SK_Alex':'AlexBody','SK_AlexMask':'AlexMask','SK_Bruce':'BruceBody','SK_BruceHair':'BruceHair','SK_BruceMask':'BruceMask'},
              'Hurricane':{'SK_Hondo':'HondoBody','SK_HondoMask':'HondoMask'}}
    for family,meshes in families.items():
        for name,part in meshes.items():
            mesh=lib.load_asset('/Game/MASK/'+family+'/'+name)
            if not mesh:raise RuntimeError('Missing '+family+'/'+name)
            slots=mesh.get_editor_property('materials')
            for index,slot in enumerate(slots):
                key=re.sub(r'[^A-Za-z0-9_]','_',part+'_'+str(slot.get_editor_property('material_slot_name')))
                path='/Game/MASK/'+family+'/Materials/MI2_'+key;mat=lib.load_asset(path)
                if not mat:raise RuntimeError('Missing existing material '+path)
                slot.set_editor_property('material_interface',mat);slots[index]=slot
            mesh.set_editor_property('materials',slots)
            if not lib.save_loaded_asset(mesh,False):raise RuntimeError('Could not save '+name+'; close all game/editor processes holding it')
            assigned=[bool(s.get_editor_property('material_interface')) for s in mesh.get_editor_property('materials')]
            if not assigned or not all(assigned):raise RuntimeError('Assignment failed '+name)
            report['meshes'].append({'mesh':mesh.get_path_name(),'assigned_slots':len(assigned)})
    report['passed']=True
except Exception:report['error']=traceback.format_exc();unreal.log_error(report['error'])
finally:(Path(unreal.Paths.project_dir())/'Saved/Art/fleet-crew-material-finalize.json').write_text(json.dumps(report,indent=2))
