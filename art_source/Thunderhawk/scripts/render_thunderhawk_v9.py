"""Render the saved V9 in a separate Blender process, without saving the scene."""
import bpy, os, json
from pathlib import Path
from mathutils import Vector
S=bpy.context.scene
OUT=Path('G:/DEV/mask-project-mayhem/art_source/Thunderhawk/renders/v9')
OUT.mkdir(parents=True,exist_ok=True)
S.cycles.samples=int(os.getenv('THK9_SAMPLES','24'))
S.render.resolution_x=1400;S.render.resolution_y=1000
try:
    pref=bpy.context.preferences.addons['cycles'].preferences
    pref.compute_device_type='OPTIX';pref.get_devices()
    devices=[d for d in pref.devices if d.type!='CPU']
    if devices:
        for d in pref.devices:d.use=d.type!='CPU'
        S.cycles.device='GPU'
        print('THK9_RENDER_GPU',[(d.name,d.type) for d in devices])
except Exception as ex:print('THK9_GPU_FALLBACK',str(ex))
views={
 'perspective':((6.7,-6.9,3.5),(.05,0,.66),'PERSP',55,1),
 'front':((8,0,.72),(0,0,.72),'ORTHO',5.50,1),
 'rear':((-8,0,.72),(0,0,.72),'ORTHO',5.50,1),
 'side':((0,-8,.72),(0,0,.72),'ORTHO',5.50,1),
 'top':((0,0,8),(0,0,0),'ORTHO',5.50,1),
 'rear_road':((-6.5,-6.6,3.1),(-.05,0,.67),'PERSP',55,1),
 'flight':((6.8,-7.0,4.1),(0,0,.9),'PERSP',50,97),
 'rear_flight':((-6.5,-6.5,3.2),(-.1,0,.85),'PERSP',50,97),
 'mid_open':((5.8,-6.0,3.3),(0,0,.85),'PERSP',50,65),
 'mid_return':((-6.5,-6.5,3.2),(-.1,0,.85),'PERSP',50,151)
}
requested=os.getenv('THK9_VIEWS',','.join(views)).split(',')
results=[]
for name in requested:
    loc,target,kind,size,frame=views[name]
    S.frame_set(frame);c=S.camera;c.location=loc;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler()
    c.data.type=kind
    bpy.data.objects['Review_Floor'].hide_render=(kind=='ORTHO')
    if kind=='ORTHO':c.data.ortho_scale=size
    else:c.data.lens=size
    S.render.filepath=str(OUT/(name+'.png'))
    bpy.ops.render.render(write_still=True)
    results.append({'view':name,'frame':frame,'file':S.render.filepath})
    print('THK9_VIEW_COMPLETE',name,flush=True)
(OUT/'last_render_run.json').write_text(json.dumps({'source':bpy.data.filepath,'samples':S.cycles.samples,'views':results},indent=2),encoding='utf-8')
