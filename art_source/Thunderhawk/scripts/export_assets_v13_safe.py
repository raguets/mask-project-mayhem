"""Export through ordinary Blender saves, avoiding scene-library-copy crash.

Each component is isolated only in memory after reloading the saved assembly.
The assembly on disk and all previous source files remain intact.
"""
import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');T=P/'art_source/Thunderhawk';A=P/'art_source/Matt_Trakker';assembly=T/'Thunderhawk_V13.blend'
def presentation(s,location,target,lens,focus,distance):
    c=s.camera;c.location=location;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                sp=area.spaces.active;sp.overlay.show_extras=False;sp.shading.type='SOLID';sp.shading.color_type='MATERIAL';sp.region_3d.view_location=focus;sp.region_3d.view_distance=distance;sp.region_3d.view_rotation=(Vector(location)-Vector(target)).to_track_quat('Z','Y')
def remove_except(keep):
    for ob in list(bpy.data.objects):
        if ob not in keep:bpy.data.objects.remove(ob,do_unlink=True)
    for co in list(bpy.data.collections):
        if not co.all_objects:bpy.data.collections.remove(co)
out=[]
bpy.ops.wm.open_mainfile(filepath=str(assembly));s=bpy.context.scene;r=bpy.data.objects['MattTrakker_Rig'];char=bpy.data.collections['MT11_Character'];mask=bpy.data.collections['Spectrum11_Asset']
keep=set(char.all_objects)|set(mask.all_objects)|{o for o in s.objects if o.type in ['CAMERA','LIGHT'] or o.name=='Review_Floor'};remove_except(keep)
r['driving_pose']=0;r['mask_on']=False;r.location=(0,0,0);r.update_tag();s.frame_set(1);bpy.context.view_layer.update()
r.id_properties_ui('driving_pose').update(min=0,max=1,description='0 = debout ; 1 = assis au volant. Un seul personnage.')
r.id_properties_ui('mask_on').update(description='Afficher ou cacher Spectrum sur la même tête.')
txt=bpy.data.texts.get('LIRE_MOI_Matt_Trakker') or bpy.data.texts.new('LIRE_MOI_Matt_Trakker');txt.clear();txt.write('Matt V4 / Spectrum V3\n\nUn seul personnage, une armature, une tête conservée sous le casque.\n\nSur MattTrakker_Rig, Propriétés personnalisées :\n driving_pose : 0 debout / 1 assis\n mask_on : décoché visage / coché casque\n\nLes deux commandes sont indépendantes ; aucune variante du corps n’est dupliquée.\nAnatomie interprétée du portrait fourni, autorisation 2026-11-02.\nSources CC0 et limites dans anatomy_provenance_v4.json et la documentation du projet.\n')
bpy.data.objects['Review_Floor'].location.z+=.016;s.name='MattTrakker_V4_Independent'
presentation(s,(3.5,3.4,1.9),(0,0,.96),62,(0,0,.94),3.1)
bpy.ops.object.select_all(action='DESELECT');r.select_set(True);bpy.context.view_layer.objects.active=r
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='PROPERTIES':area.spaces.active.context='OBJECT';area.spaces.active.pin_id=r
bpy.ops.wm.save_as_mainfile(filepath=str(A/'MattTrakker_V4.blend'),compress=True);out.append('art_source/Matt_Trakker/MattTrakker_V4.blend')

bpy.ops.wm.open_mainfile(filepath=str(assembly));s=bpy.context.scene
remove=set(bpy.data.collections['MT11_Character'].all_objects)|set(bpy.data.collections['Spectrum11_Asset'].all_objects)
for ob in list(remove):bpy.data.objects.remove(ob,do_unlink=True)
for co in list(bpy.data.collections):
    if not co.all_objects:bpy.data.collections.remove(co)
s.name='Thunderhawk_V13_Vehicle_Independent';s.frame_set(1);presentation(s,(5,5,2.8),(0,0,.7),44,(0,0,.7),6)
bpy.ops.wm.save_as_mainfile(filepath=str(T/'Thunderhawk_V13_Vehicle.blend'),compress=True);out.append('art_source/Thunderhawk/Thunderhawk_V13_Vehicle.blend')

bpy.ops.wm.open_mainfile(filepath=str(A/'MattTrakker_V4.blend'));s=bpy.context.scene;mask=bpy.data.collections['Spectrum11_Asset'];origin=Vector((-.008,0,1.55))
socket=bpy.data.objects.new('Spectrum_HeadSocket',None);mask.objects.link(socket);socket['attach_to']='MattTrakker_Rig/head';minz=0
for ob in list(mask.objects):
    if ob==socket:continue
    ob.animation_data_clear()
    for mod in list(ob.modifiers):
        if mod.type=='ARMATURE':ob.modifiers.remove(mod)
    ob.parent=None;ob.matrix_world.identity();ob.vertex_groups.clear()
    for v in ob.data.vertices:v.co-=origin;minz=min(minz,v.co.z)
    ob.parent=socket;ob.hide_render=False;ob.hide_viewport=False
keep=set(mask.all_objects)|{o for o in s.objects if o.type in ['CAMERA','LIGHT'] or o.name=='Review_Floor'};remove_except(keep)
s.name='Spectrum_V3_Independent';bpy.data.objects['Review_Floor'].location.z=minz+.010
presentation(s,(.85,.67,.4),(.02,0,.14),70,(0,0,.14),.9)
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Spectrum_V3.blend'),compress=True);out.append('art_source/Matt_Trakker/Spectrum_V3.blend')
bpy.ops.wm.open_mainfile(filepath=str(assembly));(T/'independent_assets_v13.json').write_text(json.dumps(out,indent=2));print('V13_SAFE_COMPONENT_EXPORT_COMPLETE',json.dumps(out))
