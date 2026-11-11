"""Ordinary-save component export in live Blender MCP; supply EXPORT_JOB dict.

The saved source is reloaded before each in-memory reduction and restored last.
Never pass the source path as an output. No new scenes/libraries.write(scene).
"""
import bpy,json
from datetime import datetime
from pathlib import Path
from mathutils import Vector,Matrix
job=EXPORT_JOB;source=Path(job['source_blend']).resolve();outputs=[]
assert not bpy.app.driver_namespace.get('_mask_asset_review_active'),'Finish the active review before component export.'
assert source.exists() and source.suffix.lower()=='.blend'
Path(job['manifest']).parent.mkdir(parents=True,exist_ok=True)
for spec in job['components']:
    target=Path(spec['output']).resolve();assert target!=source and target.suffix.lower()=='.blend','Output must be a separate .blend file'
if job.get('preserve_session',True):
    backup=Path(job.get('session_backup',source.parent/('Session_before_export_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'.blend')))
    backup.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(backup),copy=True,compress=True)
def dependency_closure(objects):
    keep=set(objects);changed=True
    while changed:
        changed=False
        for ob in list(keep):
            deps=[ob.parent]
            for mod in ob.modifiers:
                for name in ['object','target','mirror_object']:
                    value=getattr(mod,name,None)
                    if isinstance(value,bpy.types.Object):deps.append(value)
            for con in ob.constraints:
                value=getattr(con,'target',None)
                if isinstance(value,bpy.types.Object):deps.append(value)
            for dep in deps:
                if dep is not None and dep not in keep:keep.add(dep);changed=True
    return keep
def prune(keep):
    for ob in list(bpy.data.objects):
        if ob not in keep:bpy.data.objects.remove(ob,do_unlink=True)
    for co in list(bpy.data.collections):
        if not co.all_objects:bpy.data.collections.remove(co)
def present(scene,spec,rig):
    cfg=spec.get('presentation',{})
    if scene.camera and cfg.get('camera'):
        c=scene.camera;c.location=cfg['camera'];c.rotation_euler=(Vector(cfg['target'])-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=cfg.get('lens',60)
    floor=bpy.data.objects.get(job.get('floor','Review_Floor'))
    if floor and 'ground_z' in spec:
        ground=spec['ground_z']
        if ground=='asset_min':
            dg=bpy.context.evaluated_depsgraph_get();points=[]
            for ob in scene.objects:
                if ob.type=='MESH' and ob!=floor:
                    ev=ob.evaluated_get(dg);me=ev.to_mesh();points.extend((ev.matrix_world@v.co).z for v in me.vertices);ev.to_mesh_clear()
            ground=min(points)
        old=max((floor.matrix_world@Vector(v)).z for v in floor.bound_box);floor.location.z+=ground-old
    bpy.ops.object.select_all(action='DESELECT')
    if rig:
        rig.hide_set(False);rig.select_set(True);bpy.context.view_layer.objects.active=rig
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                sp=area.spaces.active;sp.shading.type='MATERIAL';sp.overlay.show_extras=False
                sp.region_3d.view_location=cfg.get('focus',[0,0,.8]);sp.region_3d.view_distance=cfg.get('distance',3)
                if cfg.get('camera'):sp.region_3d.view_rotation=(Vector(cfg['camera'])-Vector(cfg['target'])).to_track_quat('Z','Y')
            elif area.type=='PROPERTIES' and rig:
                area.spaces.active.pin_id=rig
                # Context choices depend on the saved editor pin/selection.
                # A presentation panel must not abort an otherwise valid export.
                try:area.spaces.active.context='OBJECT'
                except TypeError:pass
try:
    for spec in job['components']:
        bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene
        rig=bpy.data.objects.get(job.get('rig',''))
        # Remove only explicit assembly bridge drivers. Keep pose-bone drivers on
        # an articulated character, unlike animation_data_clear used for a rigid bake.
        for item in spec.get('remove_drivers',[]):
            ob=bpy.data.objects[item['object']]
            if 'index' in item:ob.driver_remove(item['data_path'],item['index'])
            else:ob.driver_remove(item['data_path'])
        if rig:
            for name,value in spec.get('properties',{}).items():rig[name]=value
            rig.location=spec.get('rig_location',[0,0,0]);rig.update_tag()
        scene.frame_set(spec.get('frame',1));bpy.context.view_layer.update()
        # Bake only explicitly named component controls before detaching their source drivers.
        # Preserve evaluated transforms so an independent module can open deployed.
        for name in spec.get('bake_driver_objects',[]):
            ob=bpy.data.objects[name];matrix=ob.matrix_world.copy();ob.animation_data_clear();ob.matrix_world=matrix
        keep=set()
        for name in spec['collections']:keep.update(bpy.data.collections[name].all_objects)
        keep.update(bpy.data.objects[name] for name in spec.get('extra_objects',[]))
        studio={ob for ob in scene.objects if ob.type in spec.get('keep_types',['CAMERA','LIGHT']) or ob.name==job.get('floor','Review_Floor')}
        if spec.get('detach_mask'):
            origin=rig.data.bones[spec.get('origin_bone','head')].head_local.copy();socket=bpy.data.objects.new(spec.get('socket','Mask_HeadSocket'),None)
            owner=bpy.data.collections[spec['collections'][0]];owner.objects.link(socket);socket['rest_bind_origin']=list(origin);socket['attachment_note']='Rigid parts: head. Flexible skirt: retain named weights and rebind to matching body rig; restore rest_bind_origin when rebuilding armature modifier.'
            for ob in list(keep):
                matrix=ob.matrix_world.copy();ob.animation_data_clear()
                for mod in list(ob.modifiers):
                    if mod.type=='ARMATURE':ob.modifiers.remove(mod)
                if ob.type=='MESH':
                    ob.data=ob.data.copy();ob.data.transform(Matrix.Translation(-origin)@matrix,shape_keys=True)
                    if ob.data.shape_keys:ob.data.shape_keys.animation_data_clear()
                ob.parent=socket;ob.matrix_parent_inverse.identity();ob.matrix_basis.identity();ob.hide_render=False;ob.hide_viewport=False
            keep.add(socket);rig=None
        else:keep=dependency_closure(keep)
        keep.update(dependency_closure(studio));kept_rig=rig if rig in keep else None;prune(keep);rig=kept_rig;scene.name=spec['scene_name']
        if spec.get('component_offset'):
            offset=Vector(spec['component_offset'])
            for ob in keep-studio:
                if ob.parent is None:ob.location+=offset
        if spec.get('help_text'):
            text=bpy.data.texts.get('ASSET_README') or bpy.data.texts.new('ASSET_README');text.clear();text.write(spec['help_text'])
        present(scene,spec,rig)
        target=Path(spec['output']);target.parent.mkdir(parents=True,exist_ok=True);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
        outputs.append({'kind':spec['kind'],'file':str(target),'scene':scene.name,'scene_objects':len(scene.objects)})
finally:
    bpy.ops.wm.open_mainfile(filepath=str(source))
    Path(job['manifest']).write_text(json.dumps({'source':str(source),'outputs':outputs,'expected':len(job['components'])},indent=2))
assert len(outputs)==len(job['components'])
print('COMPONENT_EXPORTS_SAVED',json.dumps(outputs))
