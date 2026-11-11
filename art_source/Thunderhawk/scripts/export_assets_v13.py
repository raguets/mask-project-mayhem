"""Export single-character Matt V4, Spectrum V3 and independent vehicle V13."""
raise RuntimeError('Historical exporter disabled: Blender 5.2.3 crashed in BKE_view_layer_copy_data during libraries.write(scene). Use export_assets_v13_safe.py, which was verified with regular saves.')
import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');T=P/'art_source/Thunderhawk';A=P/'art_source/Matt_Trakker'
s=bpy.context.scene;r=bpy.data.objects['MattTrakker_Rig'];char=bpy.data.collections['MT11_Character'];mask=bpy.data.collections['Spectrum11_Asset'];out=[]
r.id_properties_ui('driving_pose').update(min=0,max=1,description='0 = debout ; 1 = assis au volant. Même personnage et mêmes maillages.')
r.id_properties_ui('mask_on').update(description='Afficher ou cacher Spectrum sur la même tête : coché = casque visible.')
helptext=(A/'COMMANDES_MATT.txt').read_text(encoding='utf-8').replace('Ce fichier reprend les maillages du Matt de Thunderhawk V12, sans reconstruction.','Matt V4 reprend le personnage et l’armature du véhicule ; anatomie et casque affinés dans Thunderhawk V13.')+'\nV4 : anatomie générique adaptée, interprétation du portrait autorisée le 2 novembre 2026.\nSpectrum V3 amovible. Sources de topologie CC0 et limites dans anatomy_provenance_v4.json.\n'
txt=bpy.data.texts.get('LIRE_MOI_Matt_Trakker') or bpy.data.texts.new('LIRE_MOI_Matt_Trakker');txt.clear();txt.write(helptext)
def studio(scene,name,location,target,lens,floor_z=None):
    co=bpy.data.collections.new(name+'_Studio');scene.collection.children.link(co);objects=[]
    for ob in s.objects:
        if ob.type=='LIGHT' or ob.name=='Review_Floor':
            dupe=ob.copy();co.objects.link(dupe);objects.append(dupe)
            if ob.name=='Review_Floor' and floor_z is not None:dupe.location.z+=floor_z+.010
    cam=s.camera.copy();cam.data=s.camera.data.copy();co.objects.link(cam);objects.append(cam);scene.camera=cam;cam.location=location;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
    return co,objects
def scene_write(name,path,collections,location,target,lens,floor_z=None):
    scene=bpy.data.scenes.new(name);scene.world=s.world;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.render.resolution_x=1000;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.frame_end=193
    for co in collections:scene.collection.children.link(co)
    co,objects=studio(scene,name,location,target,lens,floor_z);scene['usage']=helptext if name.startswith('Matt') else 'Independent editable asset. Source interpretation and limits recorded in project documentation.'
    bpy.data.libraries.write(str(path),{scene},path_remap='RELATIVE_ALL',fake_user=False,compress=True)
    out.append(str(path.relative_to(P)));bpy.data.scenes.remove(scene)
    for ob in objects:bpy.data.objects.remove(ob,do_unlink=True)
    bpy.data.collections.remove(co)
r['driving_pose']=0;r['mask_on']=False;r.location=(0,0,0);r.update_tag();s.frame_set(1);bpy.context.view_layer.update()
scene_write('MattTrakker_V4_Independent',A/'MattTrakker_V4.blend',[char,mask],(3.5,3.4,1.9),(0,0,.96),62,.006)
scene_write('Thunderhawk_V13_Vehicle_Independent',T/'Thunderhawk_V13_Vehicle.blend',[bpy.data.collections['THK9_Exterior'],bpy.data.collections['THK11_Interior']],(5,5,2.8),(0,0,.7),44)
standalone=bpy.data.collections.new('Spectrum_V3_IndependentParts');socket=bpy.data.objects.new('Spectrum_HeadSocket',None);standalone.objects.link(socket);socket['attach_to']='MattTrakker_Rig/head';origin=Vector((-.008,0,1.55));minz=0
for ob in mask.objects:
    copy=ob.copy();copy.data=ob.data.copy();copy.animation_data_clear();copy.parent=None;copy.matrix_world.identity();copy['canonical_part_name']=ob.name
    for mod in list(copy.modifiers):
        if mod.type=='ARMATURE':copy.modifiers.remove(mod)
    for v in copy.data.vertices:v.co-=origin;minz=min(minz,v.co.z)
    copy.vertex_groups.clear();copy.parent=socket;copy.hide_render=False;copy.hide_viewport=False;standalone.objects.link(copy)
scene_write('Spectrum_V3_Independent',A/'Spectrum_V3.blend',[standalone],(.85,.67,.4),(.02,0,.14),70,minz)
for ob in list(standalone.objects):bpy.data.objects.remove(ob,do_unlink=True)
bpy.data.collections.remove(standalone)
r['driving_pose']=1;r['mask_on']=False;r.location=(0,.4,0);r.update_tag();s.frame_set(97);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(T/'Thunderhawk_V13.blend'),compress=True)
(T/'independent_assets_v13.json').write_text(json.dumps(out,indent=2));print('V13_COMPONENT_SOURCES_EXPORTED',json.dumps(out))
