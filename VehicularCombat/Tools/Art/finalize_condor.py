"""Read saved Condor assets and verify category, crew, wheels, tracks and rotors."""
import unreal,json
from pathlib import Path
P=Path(unreal.Paths.project_dir()).resolve();L=unreal.EditorAssetLibrary;D='/Game/MASK/Condor';definition=L.load_asset(D+'/DA_Condor')
if not definition:raise RuntimeError('Missing Condor definition')
dyn=definition.get_editor_property('dynamics');wheels=definition.get_editor_property('wheels');parts=definition.get_editor_property('parts');sk=definition.get_editor_property('driver').get_editor_property('skeleton')
checks={
 'condor_and_brad':definition.get_editor_property('vehicle_name')=='Condor' and definition.get_editor_property('driver_name')=='Brad Turner' and definition.get_editor_property('mask_name')=='Hocus Pocus',
 'road_helicopter':definition.get_editor_property('supports_flight') and dyn.get_editor_property('flight_model')==unreal.MaskFlightModel.ROTORCRAFT,
 'zero_minimum_speed':dyn.get_editor_property('minimum_airspeed_mps')==0.,
 'two_centerline_wheels':{str(w.get_editor_property('name')) for w in wheels}=={'F','R'} and all(abs(w.get_editor_property('center').y)<.01 for w in wheels),
 'two_wheel_balance':dyn.get_editor_property('two_wheel_road_balance'),
 'sampled_source_articulations':len(parts)>=10 and all(len(p.get_editor_property('samples'))==97 for p in parts),
 'both_rotors':sum(p.get_editor_property('rotor_speed_degrees')>0 for p in parts)>=3,
 'one_crew_skeleton':all(definition.get_editor_property(k) and definition.get_editor_property(k).get_editor_property('skeleton')==sk for k in ['driver','hair','mask']),
 'driver_moves_with_seat':len(definition.get_editor_property('driver_transform_samples'))==97 and bool(definition.get_editor_property('driver_transformation_pose')),
 'onfoot_ready':bool(definition.get_editor_property('driver_locomotion') and definition.get_editor_property('driver_jump')),
 'condor_pawn':isinstance(unreal.get_default_object(L.load_blueprint_class(D+'/BP_Condor')),unreal.CondorPawn),
 'cook_label':L.does_asset_exist(D+'/PAL_Condor')
}
report={'passed':all(checks.values()),'checks':checks,'parts':len(parts),'wheels':len(wheels),'rotorcraft_max_speed_mps':dyn.get_editor_property('rotorcraft_maximum_airspeed_mps')}
(P/'Saved/Art/condor-finalize.json').write_text(json.dumps(report,indent=2))
if not report['passed']:raise RuntimeError('Condor saved-asset contract failed: '+str(checks))
unreal.log_warning('CONDOR_FINALIZED '+json.dumps(report))
