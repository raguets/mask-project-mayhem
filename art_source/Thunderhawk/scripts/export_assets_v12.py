"""Export independent reusable scene datablocks through the live Blender MCP.

Uses libraries.write to preserve the assembled scene and all previous files.
The exported .blend files must subsequently be reopened and verified in Blender.
"""
import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Matt_Trakker';T=P/'art_source/Thunderhawk'
assembly=bpy.context.scene;r=bpy.data.objects['MattTrakker_Rig']
saved=(r.location.copy(),r['driving_pose'],r['mask_on'],assembly.frame_current)
out=[]
def write_asset(name,path,collections,focus,lens,metadata):
    scene=bpy.data.scenes.new(name);scene.world=assembly.world
    scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
    scene.render.resolution_x=900;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
    studio=bpy.data.collections.new(name+'_Studio');scene.collection.children.link(studio);copied=[]
    for collection in collections:scene.collection.children.link(collection)
    for ob in assembly.objects:
        if ob.type=='LIGHT' or ob.name=='Review_Floor':
            duplicate=ob.copy();studio.objects.link(duplicate);copied.append(duplicate)
            if ob.name=='Review_Floor' and name.startswith('Matt'):duplicate.location.z+=.016
    camera=assembly.camera.copy();camera.data=assembly.camera.data.copy();studio.objects.link(camera);copied.append(camera)
    camera.location=focus[0];camera.rotation_euler=(Vector(focus[1])-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=lens;scene.camera=camera
    for key,value in metadata.items():scene[key]=value
    scene.frame_set(assembly.frame_current)
    bpy.data.libraries.write(str(path),{scene},path_remap='RELATIVE_ALL',fake_user=False,compress=True)
    out.append({'file':str(path.relative_to(P)),'scene':name,'collections':[c.name for c in collections]})
    bpy.data.scenes.remove(scene)
    for ob in copied:bpy.data.objects.remove(ob,do_unlink=True)
    bpy.data.collections.remove(studio)

try:
    r.location=(0,0,0);r['driving_pose']=0;r['mask_on']=False;r.update_tag();assembly.frame_set(1);bpy.context.view_layer.update()
    write_asset('MattTrakker_V3_Independent',A/'MattTrakker_V3.blend',
        [bpy.data.collections['MT11_Character'],bpy.data.collections['Spectrum11_Asset']],
        ((3.5,3.4,1.9),(0,0,.96)),62,{
        'usage':'Select MattTrakker_Rig: driving_pose=0 standing / 1 driving; mask_on=false / true. Same articulated meshes and underlying head.',
        'reference_limit':'Interpreted anatomy from illustration and toy photographs; black/red footwear from supplied images (3).jpg. Estimated dimensions.',
        'asset_version':'Matt Trakker V3 with separately modeled Spectrum V2'})
    assembly.frame_set(1);bpy.context.view_layer.update()
    write_asset('Thunderhawk_V12_Vehicle_Independent',T/'Thunderhawk_V12_Vehicle.blend',
        [bpy.data.collections['THK9_Exterior'],bpy.data.collections['THK11_Interior']],
        ((5,5,2.8),(0,0,.7)),44,{
        'usage':'Independent editable vehicle with interpreted cockpit, transformation frames 1..193. No character dependency.',
        'reference_limit':'Exterior guided by supplied references; cockpit explicitly authorized as interpretation 2026-11-02.',
        'asset_version':'Thunderhawk V12; spoiler independent, vertical rear cover, reactors sequenced after cover rise; two named door cannons.'})
finally:
    loc,drive,mask,fr=saved;r.location=loc;r['driving_pose']=drive;r['mask_on']=mask;r.update_tag();assembly.frame_set(fr);bpy.context.view_layer.update()
(T/'independent_assets_v12.json').write_text(json.dumps(out,indent=2))
print('V12_INDEPENDENT_ASSETS_WRITTEN',json.dumps(out))
