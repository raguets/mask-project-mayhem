"""MCP inspection of the reopened game copy, with actual baked textures applied."""
import bpy,json,traceback,math
from pathlib import Path
from mathutils import Vector,Quaternion
ROOT=Path('G:/DEV/mask-project-mayhem');OUT=ROOT/'VehicularCombat/Saved/Art/game-review'
OUT.mkdir(parents=True,exist_ok=True)
SOURCE=ROOT/'VehicularCombat/SourceArt/MASK/Thunderhawk'

def run():
    try:
        if bpy.app.driver_namespace.get('_mask_asset_review_active'):raise RuntimeError('Another queue is active')
        bpy.app.driver_namespace['_mask_asset_review_active']=True
        bpy.ops.wm.open_mainfile(filepath=str(ROOT/'art_source/GameReady/Thunderhawk/Thunderhawk_GameReady.blend'))
        window=bpy.context.window_manager.windows[0]
        with bpy.context.temp_override(window=window):
            scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.device='CPU'
            scene.render.resolution_x=1100;scene.render.resolution_y=750;scene.render.resolution_percentage=100
            scene.world=bpy.data.worlds.new('GameReviewWorld');scene.world.use_nodes=True
            background=scene.world.node_tree.nodes.new('ShaderNodeBackground')
            output=scene.world.node_tree.nodes.new('ShaderNodeOutputWorld')
            scene.world.node_tree.links.new(background.outputs[0],output.inputs['Surface'])
            background.inputs[0].default_value=(.24,.29,.35,1)
            background.inputs[1].default_value=.7
            for name,position,power,size in [('Key',(4,-5,7),1500,6),('Fill',(0,5,5),1800,5),('Rim',(-6,-1,4),1200,4)]:
                data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
                ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob);ob.location=position
                ob.rotation_euler=(Vector((0,0,.7))-ob.location).to_track_quat('-Z','Y').to_euler()
            data=bpy.data.cameras.new('GameReviewCamera');camera=bpy.data.objects.new('GameReviewCamera',data);scene.collection.objects.link(camera);scene.camera=camera
            rig=bpy.data.objects['Matt_GameRig'];rig.data.pose_position='POSE'
            manifest=json.loads((SOURCE/'manifest.json').read_text(encoding='utf-8'))
            visible=[o for o in scene.objects if o.type=='MESH' and (o.name.startswith('SM_THK_') or o.name in ('MattBody','MattHair','Spectrum'))]
            stats=[]
            for ob in visible:
                ob.data.calc_loop_triangles();stats.append({'name':ob.name,'triangles':len(ob.data.loop_triangles),'uv_layers':len(ob.data.uv_layers)})
                image_path=SOURCE/(ob.name+'_BaseColor.png')
                for slot in ob.material_slots:
                    mat=slot.material.copy();slot.material=mat;nodes=mat.node_tree.nodes;links=mat.node_tree.links
                    p=next((n for n in nodes if n.type=='BSDF_PRINCIPLED'),None)
                    if 'Glass' in ob.name:
                        nodes.clear();p=nodes.new('ShaderNodeBsdfPrincipled');output=nodes.new('ShaderNodeOutputMaterial')
                        p.inputs['Base Color'].default_value=(.3,.4,.43,1);p.inputs['Transmission Weight'].default_value=1.
                        p.inputs['IOR'].default_value=1.45;p.inputs['Roughness'].default_value=.08
                        links.new(p.outputs[0],output.inputs['Surface'])
                    if image_path.exists() and p:
                        n=nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(image_path),check_existing=True)
                        links.new(n.outputs['Color'],p.inputs['Base Color'])
            for o in scene.objects:
                if o.type=='MESH' and o not in visible:o.hide_render=True
            views=[('road',False,False,'Driving',1,(6,-6,3.4),(0,0,.8)),
                   ('flight',False,True,'Driving',97,(-6,-6,3.6),(0,0,1.)),
                   ('driving_mask',False,True,'Driving',1,(2.8,-2.4,1.9),(0,-.35,1.1)),
                   ('standing',True,False,'Standing',1,(3,-3,1.9),(0,0,.95)),
                   ('standing_mask',True,True,'Standing',1,(3,-3,1.9),(0,0,.95))]
            poses={}
            for name,isolated,mask,pose,frame,position,target in views:
                for o in visible:o.hide_render=(isolated and o.name.startswith('SM_THK_')) or (o.name=='Spectrum' and not mask) or (o.name=='MattHair' and mask)
                rig.animation_data.action=bpy.data.actions['Matt_'+pose];scene.frame_set(1)
                rig.location=(0,0,0) if isolated else (0,.4,0)
                for part in manifest['parts']:
                    ob=bpy.data.objects[part['name']];sample=part['samples'][frame-1]
                    # Reverse the recorded UE delta to the Blender review frame.
                    ob.location=(sample['t'][0]/100,-sample['t'][1]/100,sample['t'][2]/100)
                    q=sample['q'];ob.rotation_mode='QUATERNION';ob.rotation_quaternion=Quaternion((q[3],-q[0],q[1],-q[2]));ob.scale=sample['s']
                bpy.context.view_layer.update()
                poses[name]={b.name:list((rig.matrix_world @ b.matrix).translation) for b in rig.pose.bones if b.name in ('pelvis','head','hand.L','foot.L')}
                camera.location=position;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();data.lens=50
                scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
            (OUT/'inspection.json').write_text(json.dumps({'meshes':stats,'poses':poses,'views':[v[0] for v in views]},indent=2),encoding='utf-8')
            (OUT/'COMPLETE').write_text('Rendered reopened game copy with baked atlases, source actions and source pivots.',encoding='utf-8')
    except Exception:
        (OUT/'ERROR.json').write_text(json.dumps({'traceback':traceback.format_exc()},indent=2),encoding='utf-8')
    finally:
        bpy.app.driver_namespace.pop('_mask_asset_review_active',None)
    return None

bpy.app.timers.register(run,first_interval=1.0)
print('GAME_REVIEW_QUEUED')
