import bpy
from mathutils import Vector
s=bpy.context.scene;r=bpy.data.objects['MattTrakker_Rig']
r['driving_pose']=1;r['mask_on']=False;r.update_tag();s.frame_set(97);bpy.context.view_layer.update()
r.id_properties_ui('driving_pose').update(min=0,max=1,description='0 = debout ; 1 = assis au volant. Le même personnage articulé.')
r.id_properties_ui('mask_on').update(description='Cocher pour afficher Spectrum ; décocher pour voir le visage conservé dessous.')
bpy.ops.object.select_all(action='DESELECT');r.select_set(True);bpy.context.view_layer.objects.active=r
s.cycles.preview_samples=16;s.cycles.use_preview_denoising=True
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active;space.overlay.show_extras=False;space.overlay.show_relationship_lines=False
            if hasattr(space.overlay,'show_bones'):space.overlay.show_bones=False
            space.shading.type='MATERIAL';space.shading.use_scene_world=False;v=space.region_3d;v.view_location=(-.65,0,.72);v.view_distance=5.7;v.view_rotation=(Vector((-5,4,2.6))-v.view_location).to_track_quat('Z','Y');v.view_perspective='PERSP'
        elif area.type=='PROPERTIES':area.spaces.active.context='OBJECT';area.spaces.active.pin_id=r
s['Art_Status']='V13 review pass: character realism improved, further likeness/groom/cloth polish pending. Surface collision sampling is not continuous-time or volumetric certification.'
bpy.ops.wm.save_as_mainfile(filepath='G:/DEV/mask-project-mayhem/art_source/Thunderhawk/Thunderhawk_V13.blend',compress=True)
print('V13_PRESENTATION_SAVED_MATERIAL_PREVIEW')
