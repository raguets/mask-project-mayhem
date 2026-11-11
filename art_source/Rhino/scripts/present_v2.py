"""Leave the saved final assembly open, with reusable controls selected."""
import bpy
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Rhino';S=bpy.context.scene
assert Path(bpy.data.filepath).resolve()==(A/'Rhino_V2.blend').resolve()
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
R=bpy.data.objects['Rhino_Control'];R['crew_controls']='AlexSector_Rig / BruceSato_Rig : driving_pose=0 debout, 1 assis ; mask_on=False/True'
for n in ['AlexSector_Rig','BruceSato_Rig']:
 ob=bpy.data.objects[n];ob['driving_pose']=1;ob['mask_on']=False;ob.update_tag()
S.frame_set(151);R.update_tag();bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT');R.hide_set(False);R.select_set(True);bpy.context.view_layer.objects.active=R
position=Vector((13,16,10));target=Vector((-1.9,-.9,1.9));S.camera.location=position;S.camera.rotation_euler=(target-position).to_track_quat('-Z','Y').to_euler();S.camera.data.lens=47
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   space=area.spaces.active;space.shading.type='MATERIAL';space.overlay.show_overlays=False;space.region_3d.view_location=target;space.region_3d.view_distance=(position-target).length;space.region_3d.view_rotation=S.camera.rotation_euler.to_quaternion();space.region_3d.view_perspective='PERSP'
  elif area.type=='PROPERTIES':area.spaces.active.context='OBJECT';area.spaces.active.pin_id=None
text=bpy.data.texts.get('RHINO_ASSEMBLY_README') or bpy.data.texts.new('RHINO_ASSEMBLY_README');text.clear();text.write('RHINO V2 / ALEX SECTOR V1 / BRUCE SATO V1\nTimeline 1 route, 151 transforme, 241 retour.\nRhino_Control : battle_mode ; bullbar, cannons, rear_detach, rear_open, cabinet_slide, launcher_up, radar_spin.\nCoffre recule et panneau ouvert avant sortie du missile.\nAlexSector_Rig et BruceSato_Rig : driving_pose 0 debout / 1 assis ; mask_on False/True.\nMemes personnages et visages, masques separes. Sources independantes et rapports dans art_source/Rhino et dossiers personnages.\nReferences fournies inspectees ; dimensions, anatomie et mecanismes caches interpretes.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Rhino_V2.blend'),compress=True);print('RHINO_V2_FINAL_ASSEMBLY_OPEN_AND_SAVED')
