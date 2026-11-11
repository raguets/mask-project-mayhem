"""Render the same standalone character in four states through live MCP."""
import bpy,json,traceback
from pathlib import Path
from mathutils import Vector
A=Path('G:/DEV/mask-project-mayhem/art_source/Matt_Trakker');O=A/'renders/pose_controls';O.mkdir(parents=True,exist_ok=True)
(O/'COMPLETE').unlink(missing_ok=True)
s=bpy.context.scene;r=bpy.data.objects['MattTrakker_Rig'];c=s.camera
assert not bpy.data.objects.get('THK_Hood')
original=(c.matrix_world.copy(),c.data.lens,s.render.filepath)
s.render.engine='CYCLES';s.cycles.samples=20;s.cycles.use_denoising=True
try:
    pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='OPTIX';pref.get_devices()
    for d in pref.devices:d.use=d.type!='CPU'
    s.cycles.device='GPU'
except Exception:pass
states=[('debout',0,False),('debout_casque',0,True),('assis',1,False),('assis_casque',1,True)];report=[]
def render_next():
    try:
        if not states:
            c.matrix_world=original[0];c.data.lens=original[1];s.render.filepath=original[2]
            r['driving_pose']=0;r['mask_on']=False;r.update_tag();s.frame_set(1);bpy.context.view_layer.update()
            (O/'manifest.json').write_text(json.dumps(report,indent=2));(O/'COMPLETE').write_text('four states rendered; standing restored');return None
        name,pose,mask=states.pop(0);r['driving_pose']=pose;r['mask_on']=mask;r.update_tag();s.frame_set(1+pose);bpy.context.view_layer.update()
        target=Vector((0,0,.94 if not pose else .72));c.location=(3.5,3.4,1.9 if not pose else 1.65)
        c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=62 if not pose else 72
        s.render.resolution_x=800;s.render.resolution_y=950;s.render.resolution_percentage=100
        s.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
        report.append({'image':name,'driving_pose':pose,'mask_on':mask,'same_character':True});return .2
    except Exception:
        (O/'ERROR.txt').write_text(traceback.format_exc());return None
bpy.app.timers.register(render_next,first_interval=.5)
print('MATT_FOUR_STATE_RENDER_STARTED')
