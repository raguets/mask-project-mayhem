"""Read-only Unreal pose and skeleton inspection."""
import unreal,json
from pathlib import Path
report={'anim_pose_api':{}}
for name in ('AnimPoseExtensions','AnimPoseEvaluationOptions','AnimPose','AnimPoseSpaces'):
    cls=getattr(unreal,name,None)
    report['anim_pose_api'][name]={n:str(getattr(cls,n).__doc__)[:1800] for n in dir(cls) if any(v in n for v in ('pose_at','bone_pose','bone_names','evaluate','skeleton','reference'))} if cls else None
report['meshes']=[]
for actor,path in [('Matt','Thunderhawk/SK_Matt'),('Alex','Rhino/SK_Alex'),('Bruce','Rhino/SK_Bruce'),('Hondo','Hurricane/SK_Hondo')]:
    mesh=unreal.load_asset('/Game/MASK/'+path);skeleton=mesh.get_editor_property('skeleton')
    item={'actor':actor,'bounds':str(mesh.get_imported_bounds()),'skeleton_api':[n for n in dir(skeleton) if 'bone' in n.lower() or 'reference' in n.lower()]}
    sequence=unreal.load_asset('/Game/MASK/OnFoot/'+actor+'/AN_Idle')
    pose=unreal.AnimPoseExtensions.get_anim_pose_at_time(sequence,0.,unreal.AnimPoseEvaluationOptions())
    item['pose']={str(n):str(unreal.AnimPoseExtensions.get_bone_pose(pose,n,unreal.AnimPoseSpaces.WORLD)) for n in unreal.AnimPoseExtensions.get_bone_names(pose) if str(n) in ('pelvis','foot_L','foot_R') or 'GameRig' in str(n)}
    try:item['retarget_modes']=[str(n.get_editor_property('translation_retargeting_mode')) for n in skeleton.get_editor_property('bone_tree')]
    except Exception as e:item['retarget_info']=str(e)
    report['meshes'].append(item)
Path(unreal.Paths.project_dir(),'Saved/Art/onfoot/ground-unreal.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
