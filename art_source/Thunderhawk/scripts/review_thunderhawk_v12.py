"""Render review views in the live Blender MCP scene and restore its state."""
import bpy,json,traceback
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem'); O=P/'art_source/Thunderhawk/renders/v12'; O.mkdir(parents=True,exist_ok=True)
(O/'COMPLETE').unlink(missing_ok=True);(O/'ERROR.txt').unlink(missing_ok=True)
s=bpy.context.scene;r=bpy.data.objects['MattTrakker_Rig'];c=s.camera
original={'frame':s.frame_current,'drive':r['driving_pose'],'mask':r['mask_on'],'loc':r.location.copy(),
          'hidden':{o.name:o.hide_render for o in s.objects},'camera':c.matrix_world.copy(),'lens':c.data.lens,
          'size':(s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage),'path':s.render.filepath,
          'floor_location':bpy.data.objects['Review_Floor'].location.copy()}
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    for d in prefs.devices:d.use=d.type!='CPU'
    s.cycles.device='GPU'
except Exception:pass
views=[
 ('standing',(3.5,3.4,1.9),(0,0,.96),False,False,False,1,62),
 ('standing_mask',(3.5,3.4,1.9),(0,0,.96),False,True,False,1,62),
 ('boots',(.85,.72,.36),(.045,0,.12),False,False,False,1,65),
 ('cabin',(1.45,1.95,1.45),(-.18,.22,.79),True,False,True,97,52),
 ('cabin_mask',(1.45,1.95,1.45),(-.18,.22,.79),True,True,True,97,52),
 ('pedals_cutaway',(1.02,1.12,.70),(.49,.41,.36),True,False,True,97,65),
 ('road',(5,5,2.8),(0,0,.7),True,True,True,1,44)]
import os
chosen=os.getenv('THK12_VIEWS','')
if chosen:views=[v for v in views if v[0] in chosen.split(',')]
reports=[]
if chosen and (O/'render_manifest.json').exists():
    reports=[v for v in json.loads((O/'render_manifest.json').read_text()) if v['view'] not in chosen.split(',')]
def restore():
    r['driving_pose']=original['drive'];r['mask_on']=original['mask'];r.location=original['loc'];r.update_tag();s.frame_set(original['frame'])
    for name,val in original['hidden'].items():
        ob=bpy.data.objects.get(name)
        if ob:ob.hide_render=val
    c.matrix_world=original['camera'];c.data.lens=original['lens']
    bpy.data.objects['Review_Floor'].location=original['floor_location']
    s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage=original['size'];s.render.filepath=original['path']
    bpy.context.view_layer.update()
def step():
    try:
        if not views:
            restore();(O/'render_manifest.json').write_text(json.dumps(reports,indent=2));(O/'COMPLETE').write_text('Rendered all requested views; live scene restored.');return None
        name,loc,target,drive,mask,vehicle,fr,lens=views.pop(0)
        bpy.data.objects['Review_Floor'].location=original['floor_location']
        if not vehicle:bpy.data.objects['Review_Floor'].location.z+=.016
        for co in ['THK9_Exterior','THK11_Interior']:
            for ob in bpy.data.collections[co].objects:ob.hide_render=not vehicle or original['hidden'].get(ob.name,False)
        if name in ('cabin','cabin_mask'):
            bpy.data.objects['THK_Windshield'].hide_render=True
        if name=='pedals_cutaway':
            for ob in bpy.data.collections['THK9_Exterior'].objects:ob.hide_render=True
            for ob in bpy.data.collections['THK11_Interior'].objects:
                if ob.name.startswith(('THK_Dash','THK_Glove','THK_Seat','THK_Door','THK_Steering','THK_Instrument','THK_Headrest','THK_Indicator')):ob.hide_render=True
        r['driving_pose']=int(drive);r['mask_on']=mask;r.location=(0,.4 if vehicle else 0,0);r.update_tag();s.frame_set(fr);bpy.context.view_layer.update()
        c.location=loc;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='PERSP';c.data.lens=lens
        s.render.resolution_x=900;s.render.resolution_y=1000;s.render.resolution_percentage=100
        s.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
        reports.append({'view':name,'drive':drive,'mask':mask,'frame':fr,'cutaway':name in ('cabin','cabin_mask','pedals_cutaway')})
        (O/'progress.json').write_text(json.dumps(reports,indent=2));return .25
    except Exception:
        (O/'ERROR.txt').write_text(traceback.format_exc());restore();return None
bpy.app.timers.register(step,first_interval=.5)
print('V12_RENDER_QUEUE_STARTED')
