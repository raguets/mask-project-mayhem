"""Installed Blender MCP export of the inspected V24 source, preserving all pivots."""
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');T=P/'VehicularCombat/Tools/Art'
code=(T/'prepare_hurricane_game.py').read_text(encoding='utf-8-sig')
for a,b in [('Hurricane','Manta'),('HondoMacLean','VanessaWarfield'),('Hondo','Vanessa'),('HU_','MA_'),('HMC_','VW_'),('V7','V24')]:code=code.replace(a,b)
code=code.replace("control['battle_mode']","control['transform']").replace("control['spare_eject']","control['door_open']")
code=code.replace("rig['mask_on']=True;rig.update_tag()", "rig['mask_on']=True;rig['in_vehicle']=1.;rig['driving_pose']=1.;rig.update_tag();bpy.context.view_layer.update()")
code=code.replace("o.type=='MESH' and any(c.name in ('MA_Body','MA_Interior','MA_RunningGear','MA_Weapons')", "o.type in {'MESH','CURVE','FONT'} and any(c.name in ('Manta_Vehicle','Manta_Interior')")
code=code.replace("c.name=='VW_Character'", "c.name=='Vanessa_Character'").replace("c.name=='VW_Mask'","c.name=='Whip_Mask'")
a=code.index('        wheels=[]');b=code.index('        for i in range(97):',a)
code=code[:a]+'''        wheels=[]
        for axle,letter in [('Front','F'),('Rear','R')]:
            for side,label in [(1,'L'),(-1,'R')]:
                ob=bpy.data.objects[f'MA_{axle}Wheel_{side}_Tire']
                p=sum((ob.matrix_world @ Vector(c) for c in ob.bound_box),Vector())/8
                wheels.append({'prefix':axle,'label':letter+label,'source_prefix':f'MA_{axle}Wheel_{side}_',
                    'fold':f'MA_FrontWheelFlip_{side}' if axle=='Front' else f'MA_RearWheelCarrier_{side}',
                    'road_position_cm':[p.x*100,-p.y*100,p.z*100],'position_cm':[p.x*100,-p.y*100,p.z*100],
                    'radius_cm':29.6,'object':ob.name})
'''+code[b:]
a=code.index('        for w in wheels:\n            ob=');b=code.index("        control['transform']=0.",a);code=code[:a]+code[b:]
code=code.replace("wheel=next((w for w in wheels if ob.name.startswith(w['prefix']+'_')),None)","wheel=next((w for w in wheels if ob.name.startswith(w['source_prefix'])),None)")
# Distinguish tires from the winglet/gun attached to the same front bearing.
code=code.replace("key='SM_MA_'+wheel['label'] if wheel else 'SM_'+owner+('_Glass' if glass else '')", "key='SM_MA_'+wheel['label'] if wheel else 'SM_'+owner+('_Glass' if glass else '')")
code=code.replace('for group in o.vertex_groups:',"for group in getattr(o,'vertex_groups',[]):")
code=code.replace("'Hair' not in o.name", "not any(s in o.name for s in ('Hair','Scalp','Fringe','Lock','Forelock'))").replace("'Hair' in o.name", "any(s in o.name for s in ('Hair','Scalp','Fringe','Lock','Forelock'))")
code=code.replace('ContinuousFlightSuit','ContinuousBodyAndFace')
code=code.replace("verts=[(x*2.55,y*.9,.72+z*.36)","verts=[(.08+x*2.26,y*.87,.55+z*.26)")
code=code.replace("'spare_control':'MA_SpareEjection'", "'source_blend':'art_source/Manta/Manta_V24_Assembly.blend','faction':'VENOM','category':'road_airplane'")
# Drivers on custom properties (tail_raise) must settle BEFORE dependent pivots
# are sampled or baked. A single update can retain the previous endpoint.
settle="for item in source.objects:item.update_tag(refresh={'OBJECT','DATA','TIME'})\n        source.frame_set(2);source.frame_set(1);bpy.context.view_layer.update()"
code=code.replace("controllers=[o for o in source.objects",settle+"\n        controllers=[o for o in source.objects")
code=code.replace("control['transform']=i/96.;control.update_tag();rig.update_tag(refresh={'OBJECT','DATA','TIME'});bpy.context.view_layer.update()", "control['transform']=i/96.;control.update_tag();rig.update_tag(refresh={'OBJECT','DATA','TIME'});bpy.context.view_layer.update()\n            source.frame_set(2);source.frame_set(1);bpy.context.view_layer.update()")
marker="        for key in ('driving_pose','gunner_pose','vehicle_lift'):"
code=code.replace(marker, "        "+settle+"\n        rest_errors={o.name:max(abs(o.matrix_world[r][c]-rest[o.name][r][c]) for r in range(4) for c in range(4)) for o in controllers}\n        write('rest_validation.json',rest_errors)\n        assert max(rest_errors.values())<.00001,rest_errors\n"+marker)
code=code.replace("bpy.app.driver_namespace['_mask_asset_review_active']=True;bpy.app.timers.register(run", "\nif bpy.data.is_dirty:\n    from datetime import datetime\n    bpy.ops.wm.save_as_mainfile(filepath=str(P/'art_source/Manta'/('Session_before_game_export_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.blend')),copy=True,compress=True)\nbpy.app.driver_namespace['_mask_asset_review_active']=True;bpy.app.timers.register(run")
exec(compile(code,'<manta-game-export>','exec'))
