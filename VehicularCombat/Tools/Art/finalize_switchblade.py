import unreal,json
from pathlib import Path
P=Path(unreal.Paths.project_dir()).resolve();L=unreal.EditorAssetLibrary;D='/Game/MASK/Switchblade';d=L.load_asset(D+'/DA_Switchblade')
if not d:raise RuntimeError('Missing definition')
parts=d.get_editor_property('parts');sk=d.get_editor_property('driver').get_editor_property('skeleton');dyn=d.get_editor_property('dynamics')
checks=dict(native=d.get_editor_property('vehicle_category')==unreal.MaskVehicleCategory.HELICOPTER_AIRPLANE,venom=d.get_editor_property('faction')==unreal.MaskFaction.VENOM,no_wheels=len(d.get_editor_property('wheels'))==0,parts=len(parts)==17 and all(len(p.get_editor_property('samples'))==97 for p in parts),airplane=dyn.get_editor_property('flight_model')==unreal.MaskFlightModel.FIXED_WING and dyn.get_editor_property('minimum_airspeed_mps')>0,miles=d.get_editor_property('driver_name')=='Miles Mayhem',viper=d.get_editor_property('mask_name')=='Viper',one_skeleton=all(d.get_editor_property(k).get_editor_property('skeleton')==sk for k in ['driver','hair','mask']),rotor=any(p.get_editor_property('rotor_in_base_mode') and p.get_editor_property('rotor_speed_degrees')>0 for p in parts),onfoot=bool(d.get_editor_property('driver_locomotion') and d.get_editor_property('driver_jump')),pawn=isinstance(unreal.get_default_object(L.load_blueprint_class(D+'/BP_Switchblade')),unreal.SwitchbladePawn))
r=dict(passed=all(checks.values()),checks=checks);(P/'Saved/Art/switchblade-finalize.json').write_text(json.dumps(r,indent=2))
if not r['passed']:raise RuntimeError(str(r))
