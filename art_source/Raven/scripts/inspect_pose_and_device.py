import bpy,json
from pathlib import Path
from mathutils import Vector
R=bpy.data.objects['CalhounBurns_Rig'];S=bpy.context.scene
old=R.location.copy();data={}
for pose in [0,1]:
    R.location=(0,0,0);R['driving_pose']=pose;R.update_tag();bpy.context.view_layer.update()
    data[str(pose)]={b.name:{'head':list(R.matrix_world@b.head),'tail':list(R.matrix_world@b.tail)} for b in R.pose.bones if b.name in ['head','neck','pelvis','chest','hand.L','hand.R','foot.L','foot.R','thigh.L']}
R['driving_pose']=0;R.location=old;R.update_tag();bpy.context.view_layer.update()
prefs=bpy.context.preferences.addons['cycles'].preferences
try:
    prefs.compute_device_type='OPTIX';prefs.get_devices()
    devices=[{'name':d.name,'type':d.type} for d in prefs.devices]
    for d in prefs.devices:d.use=d.type=='OPTIX'
    data['render_device']='GPU' if any(d.type=='OPTIX' for d in prefs.devices) else 'CPU'
except Exception as e:devices=[str(e)];data['render_device']='CPU'
data['devices']=devices
(Path('G:/DEV/mask-project-mayhem/art_source/Raven')/'pose_inventory_v1.json').write_text(json.dumps(data,indent=2))
print(json.dumps(data))
