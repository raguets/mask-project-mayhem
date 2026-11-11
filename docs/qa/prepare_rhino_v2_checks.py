"""Version review configurations explicitly for the user's V2 mechanism changes."""
from pathlib import Path
P=Path(__file__).resolve().parents[2];A=P/'art_source/Rhino/scripts'
source=(A/'validate_rhino_v1.py').read_text(encoding='utf-8').replace('validation_v1','validation_v2')
source=source.replace("'launcher_up']","'launcher_up','cabinet_slide']")
source=source.replace("launcher=[ob.name for ob in bpy.data.objects if ob.name.startswith(('RH_LaunchTube_','RH_MissileNose_','RH_LauncherCradle'))]", "launcher=['RH_LauncherCradle','RH_MissileBody','RH_MissileNose','RH_MissileFin_-1','RH_MissileFin_1']")
source=source.replace("progress=(bpy.data.objects['RH_MissileLauncherLift'].location.z-2.72)/.55", "progress=(bpy.data.objects['RH_MissileLauncherLift'].location.z-2.74)/.90")
source=source.replace("rotation_euler.y/2.126", "rotation_euler.y/2.199")
source=source.replace("'launcher_progress':progress,", "'launcher_progress':progress,'cabinet_slide_progress':-bpy.data.objects['RH_RearCabinetSlide'].location.x/.80,")
source=source.replace("f['rear_open_progress']>.92", "(f['rear_open_progress']>.92 and f['cabinet_slide_progress']>.95)")
source=source.replace("def restore():", "# Sliding housing against fixed front cabin and fixed upper glazing.\nhousing=['RH_UpperCockpitSide_-1','RH_UpperCockpitSide_1','RH_UpperCockpitRoof','RH_RearCabinetWing_-1','RH_RearCabinetWing_1','RH_UpperCockpitFloor']\nstationary=[n for n in fixed if not any(k in n for k in ['UpperCockpitSide','UpperCockpitRoof','RearCabinetWing'])]+[ob.name for ob in bpy.data.objects if ob.name.startswith('RH_CabinetFrontJamb_')]\npairs.extend((a,b) for a in housing for b in stationary)\npairs=list(dict.fromkeys(pairs))\ndef restore():")
(A/'validate_rhino_v2.py').write_text(source,encoding='utf-8')
source=(A/'review_final_v1.py').read_text(encoding='utf-8').replace('renders/v1','renders/v2').replace("'launcher_up']","'launcher_up','cabinet_slide','radar_spin']")
(A/'review_final_v2.py').write_text(source,encoding='utf-8')
print('V2 surface checks and review configuration prepared')
