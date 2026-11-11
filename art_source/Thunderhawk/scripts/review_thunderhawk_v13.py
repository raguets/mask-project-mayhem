"""Render and restore the live V13 scene; optional THK13_VIEWS filter."""
import bpy,json,os,traceback
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');O=P/'art_source/Thunderhawk/renders/v13';O.mkdir(parents=True,exist_ok=True)
(O/'COMPLETE').unlink(missing_ok=True);(O/'ERROR.txt').unlink(missing_ok=True)
s=bpy.context.scene;r=bpy.data.objects['MattTrakker_Rig'];c=s.camera
orig={'frame':s.frame_current,'drive':r['driving_pose'],'mask':r['mask_on'],'loc':r.location.copy(),
      'hidden':{o.name:o.hide_render for o in s.objects},'camera':c.matrix_world.copy(),'lens':c.data.lens,
      'floor':bpy.data.objects['Review_Floor'].location.copy(),'path':s.render.filepath,
      'shading':[(ar,ar.spaces.active.shading.type) for screen in bpy.data.screens for ar in screen.areas if ar.type=='VIEW_3D']}
for area,mode in orig['shading']:area.spaces.active.shading.type='SOLID'
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
try:
    pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='OPTIX';pref.get_devices()
    for d in pref.devices:d.use=d.type!='CPU'
    s.cycles.device='GPU'
except Exception:pass
views=[
 ('face_front',(.72,0,1.70),(0,0,1.69),0,False,False,1,85),
 ('face',(.64,.35,1.71),(0,0,1.69),0,False,False,1,85),
 ('face_profile',(0,.72,1.70),(0,0,1.69),0,False,False,1,80),
 ('spectrum',(.69,.48,1.74),(0,0,1.69),0,True,False,1,70),
 ('spectrum_front',(.86,0,1.71),(0,0,1.69),0,True,False,1,75),
 ('spectrum_profile',(0,.82,1.72),(0,0,1.69),0,True,False,1,72),
 ('standing',(3.5,3.4,1.9),(0,0,.96),0,False,False,1,62),
 ('standing_mask',(3.5,3.4,1.9),(0,0,.96),0,True,False,1,62),
 ('cabin',(1.45,1.95,1.45),(-.18,.22,.79),1,False,True,97,52),
 ('cabin_mask',(1.45,1.95,1.45),(-.18,.22,.79),1,True,True,97,52),
 ('road',(5,5,2.8),(0,0,.7),1,False,True,1,44),
 ('glass',(2.8,2.6,1.8),(-.22,.2,.97),1,False,True,1,64),
 ('rear_road',(-5.4,0,1.1),(-1.7,0,.65),1,False,True,1,58),
 ('rear_flight',(-5.5,3,2.1),(-1.7,0,.65),1,True,True,97,60),
 ('rear_plate',(-4,0,.7),(-2.35,0,.44),1,False,True,97,32),
 ('shelf_cutaway',(-1.75,1.6,1.75),(-1.2,0,.82),1,False,True,1,60)]
chosen=os.getenv('THK13_VIEWS','')
if chosen:views=[v for v in views if v[0] in chosen.split(',')]
reports=[]
if chosen and (O/'manifest.json').exists():reports=[x for x in json.loads((O/'manifest.json').read_text()) if x['view'] not in chosen.split(',')]
def restore():
    r['driving_pose']=orig['drive'];r['mask_on']=orig['mask'];r.location=orig['loc'];r.update_tag();s.frame_set(orig['frame'])
    for name,val in orig['hidden'].items():
        ob=bpy.data.objects.get(name)
        if ob:ob.hide_render=val
    c.matrix_world=orig['camera'];c.data.lens=orig['lens'];s.render.filepath=orig['path'];bpy.data.objects['Review_Floor'].location=orig['floor']
    for area,mode in orig['shading']:area.spaces.active.shading.type=mode
    bpy.context.view_layer.update()
def step():
    try:
        if not views:
            restore();(O/'manifest.json').write_text(json.dumps(reports,indent=2));(O/'COMPLETE').write_text('done; scene restored');return None
        name,loc,target,pose,masked,vehicle,fr,lens=views.pop(0)
        for co in ['THK9_Exterior','THK11_Interior']:
            for ob in bpy.data.collections[co].objects:ob.hide_render=not vehicle or orig['hidden'][ob.name]
        if name in ['cabin','cabin_mask']:bpy.data.objects['THK_Windshield'].hide_render=True
        if name=='shelf_cutaway':bpy.data.objects['THK_RearGlass'].hide_render=True
        bpy.data.objects['Review_Floor'].location=orig['floor']
        if not vehicle:bpy.data.objects['Review_Floor'].location.z+=.016
        r['driving_pose']=pose;r['mask_on']=masked;r.location=(0,.4 if vehicle else 0,0);r.update_tag();s.frame_set(fr);bpy.context.view_layer.update()
        c.location=loc;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens
        s.render.resolution_x=1000;s.render.resolution_y=1100;s.render.resolution_percentage=100
        s.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
        reports.append({'view':name,'driving_pose':pose,'mask_on':masked,'frame':fr,'windshield_hidden':name in ['cabin','cabin_mask']})
        (O/'progress.json').write_text(json.dumps(reports,indent=2));return .2
    except Exception:
        (O/'ERROR.txt').write_text(traceback.format_exc());restore();return None
bpy.app.timers.register(step,first_interval=.5)
print('V13_RENDER_REVIEW_STARTED')
