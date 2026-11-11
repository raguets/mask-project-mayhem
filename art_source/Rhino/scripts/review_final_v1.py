import bpy,json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
RENDER_JOB={'output_dir':str(P/'art_source/Rhino/renders/v1'),'rig':'Rhino_Control','rig_properties':['battle_mode','rear_detach','bullbar','cannons','rear_open','launcher_up'],'actors':{'AlexSector_Rig':['driving_pose','mask_on'],'BruceSato_Rig':['driving_pose','mask_on']},'floor':'Review_Floor','samples':24,'width':1280,'height':900,'device':'GPU','views':[]}
for name,cam,target,lens,frame in [
 ('road_front',(12,11,7),(.3,0,2),52,1),
 ('road_profile',(0,16,5),(.3,0,2),54,1),
 ('road_rear',(-10,10,7),(0,0,2),52,1),
 ('mid_transform',(13,16,10),(-1.9,-.9,1.9),47,101),
 ('transformed',(13,16,10),(-1.9,-.9,1.9),47,151),
 ('transformed_rear',(-14,12,9),(-1.9,-.9,1.9),48,151),
 ('split_wheels',(-6,8,4),(-3.4,-.9,.75),46,151),
 ('launcher',(-6.3,4.5,5.8),(-.8,0,3.15),56,151)]:
 RENDER_JOB['views'].append({'name':name,'camera':cam,'target':target,'lens':lens,'frame':frame,'properties':{}})
hidden=['RH_CabRoof','RH_CabVisor','RH_CabLowerFront','RH_Windshield_-1','RH_Windshield_1','RH_WindshieldCenter','RH_DoorGlass_1','RH_DoorGlass_-1','RH_DoorAFrame_1','RH_DoorAFrame_-1','RH_MirrorHousing_1','RH_MirrorHousing_-1']
hidden=[n for n in hidden if bpy.data.objects.get(n)]
for masked in [False,True]:
 RENDER_JOB['views'].append({'name':'cabin_mask' if masked else 'cabin','camera':[4.8,2.8,4.8],'target':[1.65,0,2.02],'lens':56,'frame':1,'properties':{},'hide_objects':hidden,'object_states':{name:{'properties':{'driving_pose':1,'mask_on':masked}} for name in ['AlexSector_Rig','BruceSato_Rig']}})
RENDER_JOB['views'].append({'name':'crew_fit','camera':[4.2,3.2,3.7],'target':[1.65,0,2.05],'lens':62,'frame':1,'properties':{},'hide_collections':['Rhino_Truck','Rhino_RearVehicle'],'object_states':{name:{'properties':{'driving_pose':1,'mask_on':False}} for name in ['AlexSector_Rig','BruceSato_Rig']}})
exec(compile((P/'art_source/shared_tools/render_review_queue.py').read_text(encoding='utf-8'),'<render_review_queue>','exec'))
