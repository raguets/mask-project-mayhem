"""Raven V16 import, reusing the shared legacy FBX/PBR path without changing other assets."""
from pathlib import Path
import unreal
P=Path(unreal.Paths.project_dir()).resolve()
code=(P/'Tools/Art/import_hurricane.py').read_text(encoding='utf-8-sig')
code=code.replace('Hurricane','Raven').replace('hurricane','raven').replace('Hondo','Calhoun').replace('HU_','RV_')
code=code.replace("DEFAULT_ATLAS='SM_Raven_Control_BaseColor'", "DEFAULT_ATLAS=next(p.stem for p in SOURCE.glob('*_BaseColor.png') if not p.stem.startswith('Calhoun'))")
code=code.replace("supports_flight=False", "supports_flight=True")
code=code.replace("for kind in ('Body','Mask'):", "for kind in ('Body','Hair','Mask'):")
code=code.replace("driver_name='Calhoun MacLean',mask_name='Blaster'", "driver_name='Calhoun Burns',mask_name='Gulliver'")
code=code.replace("mass_kg=1800.,engine_torque=550.", "mass_kg=1450.,engine_torque=550.")
code=code.replace("center_of_mass=unreal.Vector(0,0,45)", "center_of_mass=unreal.Vector(0,0,38)")
code=code.replace("chase_location=unreal.Vector(0,0,155),chase_distance=800.,cockpit_location=unreal.Vector(-15,-37,148)", "chase_location=unreal.Vector(0,0,115),chase_distance=650.,cockpit_location=unreal.Vector(-30,-37,111)")
code=code.replace("clearance_center=unreal.Vector(0,0,200),clearance_extent=unreal.Vector(300,135,130)", "clearance_center=unreal.Vector(0,0,130),clearance_extent=unreal.Vector(245,185,125)")
code=code.replace("if item['control']==manifest['spare_control']:", "if False: # Raven has no Hurricane spare-wheel assembly")
code=code.replace("definition.set_editor_property(prop,value)\n    lib.save_loaded_asset(definition)", "definition.set_editor_property(prop,value)\n    thunderhawk=lib.load_asset('/Game/MASK/Thunderhawk/DA_Thunderhawk')\n    dynamics=thunderhawk.get_editor_property('dynamics')\n    dynamics.set_editor_property('flight_model',unreal.MaskFlightModel.FIXED_WING)\n    definition.set_editor_property('dynamics',dynamics)\n    lib.save_loaded_asset(definition)")
# The shared glass helper has one pale tint. Preserve Raven's distinct dark rear glass.
marker="\ndef transforms(samples):"
custom='''
shared_material=material
def material(part,slot,contract):
    if not ('Glass' in part or contract.get('glass')):return shared_material(part,slot,contract)
    dark='RearGlass' in part or 'RearPrivacyGlass' in contract.get('name','')
    name='M_Raven_RearPrivacyGlass' if dark else 'M_Raven_Glass'
    path=DEST+'/Materials/'+name
    if lib.does_asset_exist(path):return lib.load_asset(path)
    mat=assets.create_asset(name,DEST+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
    mat.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT);mat.set_editor_property('two_sided',True)
    mat.set_editor_property('translucency_lighting_mode',unreal.TranslucencyLightingMode.TLM_SURFACE_PER_PIXEL_LIGHTING)
    edit=unreal.MaterialEditingLibrary
    color=edit.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,0,0)
    color.set_editor_property('constant',unreal.LinearColor(*((.012,.018,.022,1) if dark else (.08,.13,.15,1))))
    edit.connect_material_property(color,'',unreal.MaterialProperty.MP_BASE_COLOR)
    for value,prop in [(.90 if dark else .24,unreal.MaterialProperty.MP_OPACITY),(.105 if dark else .08,unreal.MaterialProperty.MP_ROUGHNESS),(.5,unreal.MaterialProperty.MP_SPECULAR)]:edit.connect_material_property(scalar(mat,value),'',prop)
    edit.recompile_material(mat);lib.save_loaded_asset(mat);return mat
'''
code=code.replace(marker,'\n'+custom+marker)
if globals().get('RAVEN_KEEP_EDITOR'):code=code.replace('unreal.SystemLibrary.quit_editor()','None')
exec(compile(code,'<raven-import>','exec'))
