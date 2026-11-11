import unreal,json
from pathlib import Path
report={}
for family,names in [('Thunderhawk',['SK_Matt','SK_Spectrum']),('Rhino',['SK_Alex','SK_AlexMask','SK_Bruce','SK_BruceMask']),('Hurricane',['SK_Hondo','SK_HondoMask'])]:
    for name in names:
        mesh=unreal.EditorAssetLibrary.load_asset('/Game/MASK/'+family+'/'+name)
        if not mesh:continue
        report[family+'/'+name]=[]
        for slot in mesh.get_editor_property('materials'):
            mat=slot.get_editor_property('material_interface')
            atlas=unreal.MaterialEditingLibrary.get_material_instance_texture_parameter_value(mat,'Atlas') if isinstance(mat,unreal.MaterialInstanceConstant) else None
            report[family+'/'+name].append({'slot':str(slot.get_editor_property('material_slot_name')),'material':mat.get_path_name() if mat else None,'atlas':atlas.get_path_name() if atlas else None})
(Path(unreal.Paths.project_dir())/'Saved/Art/fleet-material-inspection.json').write_text(json.dumps(report,indent=2))
