"""Fresh camera per view, explicit evaluated-camera verification. MCP GUI only."""
import bpy,json,time,traceback
from pathlib import Path
from mathutils import Vector,Matrix
job=RENDER_JOB;scene=bpy.context.scene;actor=bpy.data.objects[job['rig']];original_camera=scene.camera
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
out=Path(job['output_dir']);out.mkdir(parents=True,exist_ok=True)
for n in ['COMPLETE','ERROR.json']:(out/n).unlink(missing_ok=True)
saved={'frame':scene.frame_current,'camera':original_camera,'properties':{k:actor[k] for k in job['rig_properties']},'hidden':{c.name:c.hide_render for c in bpy.data.collections},'resolution':(scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage),'samples':scene.cycles.samples,'path':scene.render.filepath,'shading':[(a.spaces.active,a.spaces.active.shading.type) for screen in bpy.data.screens for a in screen.areas if a.type=='VIEW_3D']}
for sp,mode in saved['shading']:sp.shading.type='SOLID'
for o in scene.objects:
 if o.type=='MESH':o.data.update()
 o.update_tag()
views=list(job['views']);results=[];started=time.time();live=[];token=str(time.time_ns())
scene.render.resolution_x=job.get('width',1200);scene.render.resolution_y=job.get('height',900);scene.render.resolution_percentage=100;scene.cycles.samples=job.get('samples',20);scene.cycles.use_denoising=True
def restore():
 scene.camera=saved['camera']
 for o in list(live):
  if o.name in bpy.data.objects:bpy.data.objects.remove(o,do_unlink=True)
 live.clear()
 for k,v in saved['properties'].items():actor[k]=v
 actor.update_tag();scene.frame_set(saved['frame'])
 for n,v in saved['hidden'].items():
  if n in bpy.data.collections:bpy.data.collections[n].hide_render=v
 scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage=saved['resolution'];scene.cycles.samples=saved['samples'];scene.render.filepath=saved['path']
 for sp,mode in saved['shading']:sp.shading.type=mode
 bpy.context.view_layer.update();bpy.app.driver_namespace.pop('_mask_asset_review_active',None);bpy.app.driver_namespace.pop('_manta_review_restore',None)
def step():
 try:
  if not views:
   restore();(out/'manifest.json').write_text(json.dumps({'status':'complete','source':bpy.data.filepath,'elapsed_seconds':time.time()-started,'views':results},indent=2));(out/'COMPLETE').write_text('All views rendered with individually verified evaluated cameras.');return None
  v=views.pop(0)
  for n,val in saved['hidden'].items():
   if n in bpy.data.collections:bpy.data.collections[n].hide_render=val
  for n in v.get('hide_collections',[]):bpy.data.collections[n].hide_render=True
  for k,val in saved['properties'].items():actor[k]=v.get('properties',{}).get(k,val)
  actor.update_tag();scene.frame_set(v.get('frame',1));bpy.context.view_layer.update()
  # A new camera ID forces lens/transform evaluation and avoids stale preview data.
  data=original_camera.data.copy();data.name='Manta_QA_'+v['name'];data.type='PERSP';data.lens=v.get('lens',53);data.clip_start=.03;data.clip_end=300
  cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam);live.append(cam)
  pos=Vector(v['camera']);target=Vector(v['target']);quat=(target-pos).to_track_quat('-Z','Y');cam.matrix_world=Matrix.Translation(pos)@quat.to_matrix().to_4x4();cam.update_tag();data.update_tag();scene.camera=cam;scene.update_tag();bpy.context.view_layer.update()
  ev=cam.evaluated_get(bpy.context.evaluated_depsgraph_get());actual=ev.matrix_world.translation.copy();assert (actual-pos).length<.00001,(v['name'],actual,pos)
  destination=out/(v['name']+'.png');scene.render.filepath=str(destination);bpy.ops.render.render(write_still=True)
  results.append({'name':v['name'],'frame':scene.frame_current,'properties':v.get('properties',{}),'camera_expected':list(pos),'camera_evaluated':list(actual),'lens':data.lens,'file':str(destination),'bytes':destination.stat().st_size})
  scene.camera=original_camera;bpy.data.objects.remove(cam,do_unlink=True);live.remove(cam)
  (out/'progress.json').write_text(json.dumps({'done':len(results),'total':len(job['views']),'last':v['name']},indent=2));return .2
 except Exception:
  err=traceback.format_exc()
  try:restore()
  except:err+='\n'+traceback.format_exc()
  (out/'ERROR.json').write_text(err);return None
bpy.app.driver_namespace['_mask_asset_review_active']={'token':token,'output_dir':str(out)};bpy.app.driver_namespace['_manta_review_restore']=restore;bpy.app.timers.register(step,first_interval=.3)
print('MANTA_VERIFIED_CAMERA_REVIEW_STARTED',len(views),str(out))
