"""Blender MCP review renderer. Supply a JSON-serializable RENDER_JOB global.

No modeling or file loading. Runs one render per timer callback, restores scene
state, and writes a manifest only after the requested images have completed.
"""
import bpy,json,traceback,time
from pathlib import Path
from mathutils import Vector
job=RENDER_JOB;s=bpy.context.scene;r=bpy.data.objects[job['rig']];camera=s.camera
lock_key='_mask_asset_review_active'
assert not bpy.app.driver_namespace.get(lock_key),'Another review is active: '+str(bpy.app.driver_namespace.get(lock_key))
lock_token=str(time.time_ns())
out=Path(job['output_dir']);out.mkdir(parents=True,exist_ok=True)
for name in ['COMPLETE','ERROR.json']:(out/name).unlink(missing_ok=True)
floor=bpy.data.objects.get(job.get('floor','Review_Floor'))
actors={name:{'object':bpy.data.objects[name],'properties':{key:bpy.data.objects[name][key] for key in keys},'location':bpy.data.objects[name].location.copy()} for name,keys in job.get('actors',{}).items()}
saved={'rig_props':{name:r[name] for name in job['rig_properties']},'rig_location':r.location.copy(),'frame':s.frame_current,
       'camera_matrix':camera.matrix_world.copy(),'camera_lens':camera.data.lens,'camera_type':camera.data.type,
       'hidden':{o.name:o.hide_render for o in s.objects},'filepath':s.render.filepath,
       'resolution':(s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage),
       'floor':floor.location.copy() if floor else None,'shading':[(ar.spaces.active,ar.spaces.active.shading.type) for screen in bpy.data.screens for ar in screen.areas if ar.type=='VIEW_3D'],
       'engine':s.render.engine,'samples':s.cycles.samples,'device':s.cycles.device}
for space,mode in saved['shading']:space.shading.type='SOLID'
s.render.engine='CYCLES';s.cycles.samples=job.get('samples',24);s.cycles.use_denoising=True;s.cycles.device=job.get('device','GPU')
views=list(job['views']);results=[];retained=[];started=time.time()
if job.get('retain_unrequested_views') and (out/'manifest.json').exists():
    previous=json.loads((out/'manifest.json').read_text(encoding='utf-8'))
    assert previous['status']=='complete','Cannot retain views from an incomplete review'
    assert previous['scene_file']==bpy.data.filepath,'Cannot implicitly retain views from a different source file'
    requested={v['name'] for v in views}
    retained=[item for item in previous['renders'] if item['view']['name'] not in requested]
    assert all(Path(item['file']).exists() for item in retained),'A retained render is missing'
def reset_visibility():
    for name,val in saved['hidden'].items():
        ob=bpy.data.objects.get(name)
        if ob:ob.hide_render=val
def reset_actors(states=None):
    for name,state in actors.items():
        ob=state['object'];override=(states or {}).get(name,{})
        ob.location=override.get('location',state['location'])
        for key,value in state['properties'].items():ob[key]=override.get('properties',{}).get(key,value)
        ob.update_tag()
def restore():
    reset_actors()
    for name,val in saved['rig_props'].items():r[name]=val
    r.location=saved['rig_location'];r.update_tag();s.frame_set(saved['frame']);reset_visibility()
    camera.matrix_world=saved['camera_matrix'];camera.data.lens=saved['camera_lens'];camera.data.type=saved['camera_type']
    s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage=saved['resolution'];s.render.filepath=saved['filepath']
    s.cycles.samples=saved['samples'];s.cycles.device=saved['device'];s.render.engine=saved['engine']
    if floor:floor.location=saved['floor']
    for space,mode in saved['shading']:space.shading.type=mode
    bpy.context.view_layer.update()
    if bpy.app.driver_namespace.get(lock_key,{}).get('token')==lock_token:bpy.app.driver_namespace.pop(lock_key,None)
def step():
    try:
        if not views:
            restore();manifest={'status':'complete','elapsed_seconds':round(time.time()-started,2),'scene_file':bpy.data.filepath,'job':job,'renders':retained+results,'retained_previous_views':[v['view']['name'] for v in retained]}
            (out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');(out/'COMPLETE').write_text('Scene restored after completed review renders.');return None
        view=views.pop(0);reset_visibility();reset_actors(view.get('object_states'))
        for name,val in view['properties'].items():r[name]=val
        r.location=view.get('rig_location',[0,0,0]);r.update_tag();s.frame_set(view.get('frame',1));bpy.context.view_layer.update()
        for collection in view.get('hide_collections',[]):
            for ob in bpy.data.collections[collection].all_objects:ob.hide_render=True
        for name in view.get('hide_objects',[]):bpy.data.objects[name].hide_render=True
        if floor:floor.location=saved['floor']+Vector(view.get('floor_offset',[0,0,0]))
        camera.location=view['camera'];camera.rotation_euler=(Vector(view['target'])-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='PERSP';camera.data.lens=view.get('lens',60)
        s.render.resolution_x=job.get('width',900);s.render.resolution_y=job.get('height',1000);s.render.resolution_percentage=100
        destination=out/(view['name']+'.png');s.render.filepath=str(destination);bpy.ops.render.render(write_still=True)
        assert destination.exists() and destination.stat().st_size>1000,'Render output missing or empty'
        results.append({'view':view,'file':str(destination),'size_bytes':destination.stat().st_size});(out/'progress.json').write_text(json.dumps({'status':'running','done':len(results),'total':len(job['views']),'last':view['name']},indent=2));return .2
    except Exception:
        error=traceback.format_exc()
        try:restore()
        except Exception:error+='\nRESTORE ERROR\n'+traceback.format_exc()
        (out/'ERROR.json').write_text(json.dumps({'status':'failed','completed':[v['view']['name'] for v in results],'error':error},indent=2));return None
bpy.app.driver_namespace[lock_key]={'token':lock_token,'output_dir':str(out)}
bpy.app.timers.register(step,first_interval=.4)
print('REVIEW_RENDER_QUEUE_STARTED',json.dumps({'views':len(views),'output':str(out)}))
