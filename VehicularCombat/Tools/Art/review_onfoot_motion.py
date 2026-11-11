"""Blender MCP render/reopen review. No source blend is overwritten."""
import bpy,json,traceback,math
from datetime import datetime
from pathlib import Path
from mathutils import Vector
ROOT=Path('G:/DEV/mask-project-mayhem/VehicularCombat');OUT=ROOT/'Saved/Art/onfoot/review';OUT.mkdir(parents=True,exist_ok=True)
BACKUP=OUT/'session-before-review.blend'
if not BACKUP.exists():bpy.ops.wm.save_as_mainfile(filepath=str(BACKUP),copy=True)
elif (OUT/'ERROR.json').exists():bpy.ops.wm.save_as_mainfile(filepath=str(OUT/('session-error-'+datetime.now().strftime('%Y%m%d-%H%M%S')+'.blend')),copy=True)
jobs=[(actor,clip,frame,masked) for actor in ('Matt','Alex','Bruce','Hondo') for clip,frame,masked in [('Idle',1,True),('Idle',1,False),('Walk000',9,True),('Run000',6,True),('Jump',12,True)]]
state={'actor':None,'views':[]}
def step():
    try:
        if not jobs:
            (OUT/'manifest.json').write_text(json.dumps({'complete':True,'views':state['views']},indent=2),encoding='utf-8')
            bpy.ops.wm.open_mainfile(filepath=str(BACKUP));return None
        actor,clip,frame,masked=jobs.pop(0)
        if state['actor']!=actor:
            source=ROOT/'SourceArt/MASK/OnFoot'/actor/(actor+'_Locomotion.blend');bpy.ops.wm.open_mainfile(filepath=str(source));state['actor']=actor
            scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE')
            assert len([o for o in scene.objects if o.type=='ARMATURE'])==1
            scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True
            preferences=bpy.context.preferences.addons['cycles'].preferences;preferences.get_devices()
            scene.cycles.device='GPU' if any(d.use and d.type!='CPU' for d in preferences.devices) else 'CPU'
            scene.render.resolution_x=640;scene.render.resolution_y=760;scene.render.resolution_percentage=100
            world=bpy.data.worlds.new('OnFootReviewWorld');world.use_nodes=True
            background=world.node_tree.nodes.new('ShaderNodeBackground');output=world.node_tree.nodes.new('ShaderNodeOutputWorld')
            background.inputs[0].default_value=(.48,.55,.65,1);background.inputs[1].default_value=.6;world.node_tree.links.new(background.outputs[0],output.inputs['Surface']);scene.world=world
            bpy.ops.mesh.primitive_plane_add(size=12);floor=bpy.context.view_layer.objects.active;floor.name='OnFootReviewGround'
            mat=bpy.data.materials.new('OnFootReviewGround');mat.diffuse_color=(.16,.18,.21,1);floor.data.materials.append(mat)
            for name,position,power,size in [('Key',(3,-4,5),700,4),('Fill',(2,4,3),500,4),('Rim',(-3,1,4),650,3)]:
                data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
                ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob);ob.location=position;ob.rotation_euler=(Vector((0,0,.95))-ob.location).to_track_quat('-Z','Y').to_euler()
            camera_data=bpy.data.cameras.new('OnFootReviewCamera');camera=bpy.data.objects.new('OnFootReviewCamera',camera_data);scene.collection.objects.link(camera);scene.camera=camera
            camera.location=(3,-3,1.65);camera.rotation_euler=(Vector((0,0,.9))-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.lens=62
        scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE')
        rig['mask_on']=masked;rig.update_tag();rig.animation_data.action=bpy.data.actions[actor+'_OnFoot_'+clip];scene.frame_set(frame);bpy.context.view_layer.update()
        file=f'{actor}-{clip}-{frame}-'+('mask' if masked else 'face')+'.png';scene.render.filepath=str(OUT/file);bpy.ops.render.render(write_still=True)
        state['views'].append({'actor':actor,'clip':clip,'frame':frame,'mask':masked,'file':file,'source':str(ROOT/'SourceArt/MASK/OnFoot'/actor/(actor+'_Locomotion.blend'))})
        (OUT/'progress.json').write_text(json.dumps({'stage':'RENDERING','done':len(state['views']),'remaining':len(jobs)}),encoding='utf-8');return .2
    except Exception:
        (OUT/'ERROR.json').write_text(json.dumps({'error':traceback.format_exc()},indent=2),encoding='utf-8');return None
bpy.app.timers.register(step,first_interval=.1,persistent=True);print('ONFOOT_REVIEW_QUEUED')
