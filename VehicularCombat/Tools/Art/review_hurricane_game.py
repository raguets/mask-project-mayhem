"""MCP render inspection of reopened Rhino game source and actual baked atlases."""
import bpy,json,traceback
from pathlib import Path
from mathutils import Vector,Quaternion
ROOT=Path('G:/DEV/mask-project-mayhem');PROJECT=ROOT/'VehicularCombat'
OUT=PROJECT/'Saved/Art/hurricane-game-review-01';OUT.mkdir(parents=True,exist_ok=True)
def run():
    try:
        if bpy.app.driver_namespace.get('_mask_asset_review_active'):raise RuntimeError('Another art job is active')
        bpy.app.driver_namespace['_mask_asset_review_active']=True
        bpy.ops.wm.open_mainfile(filepath=str(ROOT/'art_source/GameReady/Hurricane/Hurricane_GameReady.blend'))
        with bpy.context.temp_override(window=bpy.context.window_manager.windows[0]):
            scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=12
            scene.render.resolution_x=1100;scene.render.resolution_y=800;scene.render.resolution_percentage=100
            scene.world=bpy.data.worlds.new('HurricaneGameReviewWorld');scene.world.use_nodes=True
            background=scene.world.node_tree.nodes.new('ShaderNodeBackground');output=scene.world.node_tree.nodes.new('ShaderNodeOutputWorld')
            scene.world.node_tree.links.new(background.outputs[0],output.inputs['Surface'])
            background.inputs[0].default_value=(.32,.38,.46,1);background.inputs[1].default_value=.8
            for name,pos,power,size in [('Key',(6,-6,9),3000,5),('Fill',(0,6,7),2500,5),('Rim',(-7,-1,8),3000,4)]:
                data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
                ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector((0,0,2))-ob.location).to_track_quat('-Z','Y').to_euler()
            data=bpy.data.cameras.new('HurricaneGameReviewCamera');camera=bpy.data.objects.new('HurricaneGameReviewCamera',data);scene.collection.objects.link(camera);scene.camera=camera;data.lens=50
            source=PROJECT/'SourceArt/MASK/Hurricane';manifest=json.loads((source/'manifest.json').read_text(encoding='utf-8'))
            visible=[o for o in scene.objects if o.type=='MESH' and (o.name.startswith('SM_') or o.name in ('HondoBody','HondoHair','HondoMask'))]
            stats=[]
            for ob in visible:
                ob.data.calc_loop_triangles();stats.append({'name':ob.name,'triangles':len(ob.data.loop_triangles)})
                image=source/(ob.name+'_BaseColor.png')
                for slot in ob.material_slots:
                    mat=slot.material.copy();slot.material=mat;p=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
                    if p and image.exists():
                        n=mat.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(image),check_existing=True);mat.node_tree.links.new(n.outputs['Color'],p.inputs['Base Color'])
            for ob in scene.objects:
                if ob.type=='MESH' and ob not in visible:ob.hide_render=True
            views=[('road',0,True,'Transform',(8,-8,5),(0,0,1),False),
                   ('combat',96,True,'Transform',(7,-8,5),(0,0,1.5),False),
                   ('half-transform',48,True,'Transform',(7,-8,5),(0,0,1.5),False),
                   ('driver-mask',0,True,'Transform',(2.5,-3,2.2),(0,.37,1.35),False),
                   ('gunner-mask',96,True,'Transform',(2.5,-3,3.1),(.06,0,2.25),False),
                   ('hondo-standing-mask',0,True,'Standing',(3,-3,2.1),(0,0,1),True),
                   ('hondo-standing-face',0,False,'Standing',(3,-3,2.1),(0,0,1),True)]
            for name,index,mask,pose,pos,target,isolated in views:
                for ob in visible:
                    ob.hide_render=(isolated and not ob.name.startswith('Hondo')) or (ob.name.endswith('Mask') and not mask) or (ob.name.endswith('Hair') and mask)
                rig=bpy.data.objects['Hondo_GameRig'];action=bpy.data.actions['Hondo_'+pose]
                rig.animation_data.action=action;rig.animation_data.action_slot=action.slots[0];rig.data.pose_position='POSE'
                loc=manifest['driver_tracks'][index]['t'];rig.location=(0,0,0) if isolated else (loc[0]/100,-loc[1]/100,loc[2]/100)
                for part in manifest['parts']:
                    ob=bpy.data.objects[part['name']];s=part['samples'][index];q=s['q'];ob.location=(s['t'][0]/100,-s['t'][1]/100,s['t'][2]/100);ob.rotation_mode='QUATERNION';ob.rotation_quaternion=Quaternion((q[3],-q[0],q[1],-q[2]));ob.scale=s['s']
                scene.frame_set(index+1 if pose=='Transform' else 1);bpy.context.view_layer.update();camera.location=pos;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
                scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
                (OUT/'progress.json').write_text(json.dumps({'rendered':name}))
            (OUT/'inspection.json').write_text(json.dumps({'meshes':stats,'views':[v[0] for v in views],'same_rigs':True},indent=2))
            (OUT/'COMPLETE').write_text('Reopened game source, actual atlases, source articulation and same Hondo rig.')
            bpy.ops.wm.open_mainfile(filepath=str(ROOT/'art_source/Hurricane/Hurricane_V7_Assembly.blend'))
    except Exception:(OUT/'ERROR.json').write_text(json.dumps({'error':traceback.format_exc()}))
    finally:bpy.app.driver_namespace.pop('_mask_asset_review_active',None)
    return None
bpy.app.timers.register(run,first_interval=1.)
print('HURRICANE_GAME_REVIEW_QUEUED')
