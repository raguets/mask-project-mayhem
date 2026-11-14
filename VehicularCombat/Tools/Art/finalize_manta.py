"""Read back saved imported assets; fail the batch on contract violations."""
import unreal,json
from pathlib import Path
P=Path(unreal.Paths.project_dir()).resolve();L=unreal.EditorAssetLibrary;D='/Game/MASK/Manta'
d=L.load_asset(D+'/DA_Manta');t=L.load_asset('/Game/MASK/Thunderhawk/DA_Thunderhawk')
manifest=json.loads((P/'SourceArt/MASK/Manta/manifest.json').read_text())
dyn=d.get_editor_property('dynamics');tdyn=t.get_editor_property('dynamics')
parts=d.get_editor_property('parts');wheels=d.get_editor_property('wheels');sk=d.get_editor_property('driver').get_editor_property('skeleton')
checks={
    'venom_road_fixed_wing':d.get_editor_property('faction')==unreal.MaskFaction.VENOM and d.get_editor_property('supports_flight') and dyn.get_editor_property('flight_model')==unreal.MaskFlightModel.FIXED_WING,
    'same_dynamics_as_thunderhawk':dyn.export_text()==tdyn.export_text(),
    'vanessa_whip':d.get_editor_property('driver_name')=='Vanessa Warfield' and d.get_editor_property('mask_name')=='Whip',
    'four_wheels':{str(w.get_editor_property('name')) for w in wheels}=={'FL','FR','RL','RR'},
    'all_rigid_tracks':len(parts)==len(manifest['parts']) and all(len(p.get_editor_property('samples'))==97 and p.get_editor_property('mesh') for p in parts),
    'one_character_skeleton':all(d.get_editor_property(k).get_editor_property('skeleton')==sk for k in ['driver','hair','mask']),
    'driver_animations':all(d.get_editor_property(k) for k in ['driving_pose','standing_pose','driver_transformation_pose','driver_locomotion','driver_jump']),
    'native_manta_blueprint':isinstance(unreal.get_default_object(L.load_blueprint_class(D+'/BP_Manta')),unreal.MantaPawn),
    'cook_label':L.does_asset_exist(D+'/PAL_Manta')
}
r={'passed':all(checks.values()),'checks':checks,'parts':len(parts),'minimum_airspeed_mps':dyn.get_editor_property('minimum_airspeed_mps')}
r['mesh_bounds']={}
for part in parts:
    mesh=part.get_editor_property('mesh');b=mesh.get_bounds();o=b.origin;e=b.box_extent
    r['mesh_bounds'][str(part.get_editor_property('name'))]={'min':[o.x-e.x,o.y-e.y,o.z-e.z],'max':[o.x+e.x,o.y+e.y,o.z+e.z]}
    sample=part.get_editor_property('samples')[-1]
    transformed=unreal.MathLibrary.transform_location(sample,o)
    r['mesh_bounds'][str(part.get_editor_property('name'))].update(flight_center=[transformed.x,transformed.y,transformed.z],flight_transform=str(sample))
(P/'Saved/Art/manta-finalize.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
if not r['passed']:raise RuntimeError('Manta saved-asset contract failed: '+str(checks))
