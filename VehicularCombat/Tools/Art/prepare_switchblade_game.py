"""Installed Blender MCP export: native helicopter/airplane, no road wheels."""
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');T=P/'VehicularCombat/Tools/Art'
code=(T/'prepare_hurricane_game.py').read_text(encoding='utf-8-sig')
code=code.replace('Hurricane','Switchblade').replace('HondoMacLean','MilesMayhem').replace('Hondo','Miles').replace('HU_','SB_').replace('HMC_','MM_').replace('V7','V22')
code=code.replace("control['battle_mode']","control['transform']").replace("control['spare_eject']","control['rotor_angle']")
code=code.replace("rig['mask_on']=True;rig.update_tag()", "rig['mask_on']=True;rig['driving_pose']=1.;rig['in_vehicle']=1.;control['canopy_open']=0.;control['hover_height']=0.;rig.update_tag();control.update_tag();bpy.context.view_layer.update()")
code=code.replace("o.type=='MESH' and any(c.name in ('SB_Body','SB_Interior','SB_RunningGear','SB_Weapons')", "o.type in {'MESH','CURVE','FONT'} and any(c.name in ('Switchblade_Vehicle','Switchblade_Interior')")
code=code.replace("c.name=='MM_Character'", "c.name=='Miles_Character'").replace("c.name=='MM_Mask'", "c.name=='Miles_ViperMask'")
code=code.replace('for group in o.vertex_groups:',"for group in getattr(o,'vertex_groups',[]):")
a=code.index('        wheels=[]');b=code.index('        for i in range(97):',a);code=code[:a]+'        wheels=[]\n'+code[b:]
code=code.replace("glass=any(s.material and 'Glass' in s.material.name for s in ob.material_slots)", "glass=any(s.material and ('Glass' in s.material.name or 'Glazing' in ob.name or 'Canopy' in s.material.name) for s in ob.material_slots)")
code=code.replace("'SB_UpperChassisLift'", "'Switchblade_Control'")
code=code.replace("'Hair' not in o.name", "not any(k in o.name for k in ['Hair','Scalp'])").replace("'Hair' in o.name", "any(k in o.name for k in ['Hair','Scalp'])")
code=code.replace("verts=[(x*2.55,y*.9,.72+z*.36)", "verts=[(-.45+x*3.45,y*.65,1.2+z*1.13)")
code=code.replace("'spare_control':'SB_SpareEjection'", "'spare_control':'NONE','source_blend':'art_source/Switchblade/Switchblade_V22_Assembly.blend','vehicle_category':'helicopter_airplane'")
code=code.replace("write('manifest.json',manifest);", "\n        for part in parts:\n            node=bpy.data.objects.get(part['control']);anc=[]\n            while node:anc.append(node.name);node=node.parent\n            if 'SB_MainRotorSpin' in anc:part.update(rotor_axis=[0,0,1],rotor_pivot_cm=[-43,0,234],rotor_speed=1440.,rotor_base_mode=True)\n        write('manifest.json',manifest);")
# Curve objects have no vertex groups; meshes are independently copied and baked.
exec(compile(code,'<switchblade-game-export>','exec'))
