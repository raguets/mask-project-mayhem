"""Import Condor V20 and Brad, with two true wheels and rotorcraft tuning."""
from pathlib import Path
import unreal
P=Path(unreal.Paths.project_dir()).resolve()
code=(P/'Tools/Art/import_hurricane.py').read_text(encoding='utf-8-sig')
code=code.replace('Hurricane','Condor').replace('hurricane','condor').replace('Hondo','Brad').replace('HU_','CD_')
code=code.replace("DEFAULT_ATLAS='SM_Condor_Control_BaseColor'", "DEFAULT_ATLAS=next(p.stem for p in SOURCE.glob('*_BaseColor.png') if not p.stem.startswith('Brad'))")
code=code.replace("for kind in ('Body','Mask'):", "for kind in ('Body','Hair','Mask'):")
code=code.replace("driver_name='Brad MacLean',mask_name='Blaster'", "driver_name='Brad Turner',mask_name='Hocus Pocus'")
code=code.replace('supports_flight=False','supports_flight=True')
code=code.replace('mass_kg=1800.,engine_torque=550.','mass_kg=280.,engine_torque=120.')
code=code.replace('center_of_mass=unreal.Vector(0,0,45)','center_of_mass=unreal.Vector(0,0,42)')
code=code.replace('chase_location=unreal.Vector(0,0,155),chase_distance=800.,cockpit_location=unreal.Vector(-15,-37,148)','chase_location=unreal.Vector(0,0,115),chase_distance=470.,cockpit_location=unreal.Vector(10,0,146)')
code=code.replace('clearance_center=unreal.Vector(0,0,200),clearance_extent=unreal.Vector(300,135,130)','clearance_center=unreal.Vector(-30,0,150),clearance_extent=unreal.Vector(200,155,100)')
code=code.replace("p.set_editor_property('samples',transforms(item['samples']));parts.append(p)", "p.set_editor_property('samples',transforms(item['samples']))\n            if item.get('rotor_speed'):\n                p.set_editor_property('rotor_axis',unreal.Vector(*item['rotor_axis']));p.set_editor_property('rotor_pivot',unreal.Vector(*item['rotor_pivot_cm']));p.set_editor_property('rotor_speed_degrees',item['rotor_speed'])\n            parts.append(p)")
code=code.replace("    lib.save_loaded_asset(definition)\n    path=DEST+'/BP_Condor'", """    dynamics=definition.get_editor_property('dynamics')
    for key,value in dict(flight_model=unreal.MaskFlightModel.ROTORCRAFT,minimum_airspeed_mps=0.,rotorcraft_maximum_airspeed_mps=20.,speed_command_rate_mps2=10.,maximum_pitch_degrees=22.,low_speed_turn_rate_degrees=60.,rotorcraft_climb_mps=5.,automatic_takeoff_height_m=2.,landing_descent_mps=6.,road_power_kw=55.,road_drag_area_m2=.35,air_drag_area_m2=.22,two_wheel_road_balance=True).items():dynamics.set_editor_property(key,value)
    definition.set_editor_property('dynamics',dynamics)
    lib.save_loaded_asset(definition)
    path=DEST+'/BP_Condor'""")
code=code.replace('unreal.SystemLibrary.quit_editor()','None')
code=code.replace("options.set_editor_property('reduction_settings',lods);editor.set_lods(mesh,options)", "options.set_editor_property('reduction_settings',lods)\n        if editor:editor.set_lods(mesh,options)\n        else:report['static_lod_note']='Commandlet: reduced source LOD0 retained; skeletal LODs generated separately.'")
exec(compile(code,'<condor-import>','exec'))


