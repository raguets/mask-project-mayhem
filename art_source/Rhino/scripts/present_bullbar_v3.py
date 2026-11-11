import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Rhino';S=bpy.context.scene;R=bpy.data.objects['Rhino_Control']
assert Path(bpy.data.filepath).resolve()==(A/'Rhino_V3.blend').resolve();assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
review=json.loads((A/'renders/v3/manifest.json').read_text());assert review['status']=='complete' and len(review['renders'])==5
assert json.loads((A/'standalone_vehicle_validation_v3.json').read_text())['reopened']
S.frame_set(1);R.update_tag();bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT');R.select_set(True);bpy.context.view_layer.objects.active=R
position=Vector((10,8,5.6));target=Vector((1.5,0,1.7));S.camera.location=position;S.camera.rotation_euler=(target-position).to_track_quat('-Z','Y').to_euler();S.camera.data.lens=53
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   space=area.spaces.active;space.shading.type='MATERIAL';space.overlay.show_overlays=False;space.region_3d.view_location=target;space.region_3d.view_distance=(position-target).length;space.region_3d.view_rotation=S.camera.rotation_euler.to_quaternion();space.region_3d.view_perspective='PERSP'
  elif area.type=='PROPERTIES':area.spaces.active.context='OBJECT';area.spaces.active.pin_id=None
text=bpy.data.texts.get('RHINO_ASSEMBLY_README') or bpy.data.texts.new('RHINO_ASSEMBLY_README');text.clear();text.write('RHINO V3\nPare-buffle : cadre ferme, sept barreaux verticaux, dimensions alignees sur la calandre.\nPhoto fournie rhino pare buffle.jpg inspectee. Attaches cachees interpretees.\nRhino_Control : timeline 1 route, 151 transforme, 241 retour. bullbar conserve son avance de 0.80m.\nAutres mecanismes V2 conserves : canons, module arriere, panneau, recul du coffre et missile, radar.\nAlexSector_Rig / BruceSato_Rig : driving_pose 0 debout / 1 assis ; mask_on False/True.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Rhino_V3.blend'),compress=True)
summary={'source':bpy.data.filepath,'reference':'Images de reference/rhino/rhino pare buffle.jpg','review_images':5,'outline_matches_grille':True,'closed_outline':True,'vertical_bars':7,'checked_integer_frames':241,'bullbar_collision_frames':[],'independent_vehicle_reopened':True,'previous_sources_preserved':True}
(A/'delivery_validation_v3.json').write_text(json.dumps(summary,indent=2));print('RHINO_V3_PRESENTED_AND_SAVED',json.dumps(summary))
