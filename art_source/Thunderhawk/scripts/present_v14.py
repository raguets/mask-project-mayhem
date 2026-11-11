"""Leave the final assembly open with its reversible character controls visible."""
import bpy
from pathlib import Path
from mathutils import Vector

path=Path('G:/DEV/mask-project-mayhem/art_source/Thunderhawk/Thunderhawk_V14.blend')
assert Path(bpy.data.filepath).resolve()==path.resolve()
s=bpy.context.scene
r=bpy.data.objects['MattTrakker_Rig']
print('BEFORE_PRESENTATION',s.frame_current,list(r.location),dict(r.items()))
r['driving_pose']=1
r['mask_on']=True
r.id_properties_ui('driving_pose').update(description='Même Matt : 0 debout, 1 conduite',min=0,max=1)
r.id_properties_ui('mask_on').update(description='Afficher ou cacher Spectrum sur le même visage')
r.update_tag()
s.frame_set(97)
bpy.context.view_layer.update()
bpy.ops.object.select_all(action='DESELECT')
r.hide_set(False)
r.select_set(True)
bpy.context.view_layer.objects.active=r
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active
            space.shading.type='MATERIAL'
            space.overlay.show_overlays=False
            region=space.region_3d
            position=Vector((5.6,-6.1,3.3))
            target=Vector((0,0,.85))
            region.view_rotation=(target-position).to_track_quat('-Z','Y')
            region.view_location=target
            region.view_distance=(position-target).length
            region.view_perspective='PERSP'
bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
print('V14_ASSEMBLY_PRESENTED_AND_SAVED',s.frame_current,list(r.location))
