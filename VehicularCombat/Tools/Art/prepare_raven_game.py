"""Live Blender MCP adapter of the proven mesh/atlas/centimetre FBX pipeline.

Preserves Raven V16. Each actual source controller keeps its own sampled track,
including the complete front roll, secondary wheel folds and gun hinges.
"""
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');TOOLS=P/'VehicularCombat/Tools/Art'
code=(TOOLS/'prepare_hurricane_game.py').read_text(encoding='utf-8-sig')
code=code.replace('Hurricane','Raven').replace('HondoMacLean','CalhounBurns').replace('Hondo','Calhoun').replace('HU_','RV_').replace('HMC_','CB_').replace('V7','V16')
code=code.replace("control['battle_mode']","control['transform']").replace("control['spare_eject']","control['disc_launch']")
code=code.replace("rig=bpy.data.objects['CalhounBurns_Rig'];rig['mask_on']=True;rig.update_tag()", "rig=bpy.data.objects['CalhounBurns_Rig'];rig['mask_on']=True;rig['driving_pose']=1.;rig['in_vehicle']=1.;rig.update_tag();control['hover_height']=0.;bpy.context.view_layer.update()")
code=code.replace("o.type=='MESH' and any(c.name in ('RV_Body'", "o.type in {'MESH','CURVE','FONT'} and any(c.name in ('RV_Body'")
a=code.index('        wheels=[]');b=code.index('        for i in range(97):',a)
code=code[:a]+'''        wheels=[]
        for axle,front in [('Front','F'),('Rear','R')]:
            for side,letter in [('L','L'),('R','R')]:
                ob=bpy.data.objects['RV_'+axle+'Tire_'+side]
                p=sum((ob.matrix_world @ Vector(c) for c in ob.bound_box),Vector())/8
                wheels.append({'prefix':axle,'label':front+letter,'fold':'RV_'+axle+'WheelFold_'+side,
                    'road_position_cm':[p.x*100,-p.y*100,p.z*100],'position_cm':[p.x*100,-p.y*100,p.z*100],
                    'radius_cm':33.5,'object':ob.name})
'''+code[b:]
a=code.index('        for w in wheels:\n            ob=');b=code.index("        control['transform']=0.",a)
code=code[:a]+code[b:]
code=code.replace("wheel=next((w for w in wheels if ob.name.startswith(w['prefix']+'_')),None)", "wheel=None\n            ancestor=ob\n            while ancestor:\n                wheel=next((w for w in wheels if ancestor.name==w['fold']),None)\n                if wheel:break\n                ancestor=ancestor.parent")
code=code.replace("key='SM_RV_'+wheel['label'] if wheel else 'SM_'+owner+('_Glass' if glass else '')", "privacy=any(s.material and 'RearPrivacyGlass' in s.material.name for s in ob.material_slots)\n            key='SM_'+owner+('_RearGlass' if privacy else '_Glass' if glass else '')")
# Curves have no vertex groups; their evaluated meshes still retain every trim.
code=code.replace('for group in o.vertex_groups:','for group in getattr(o,\'vertex_groups\',[]):')
code=code.replace("'RV_UpperChassisLift'", "'RV_CompleteFront_LongitudinalPivot'")
code=code.replace("for key in ('driving_pose','gunner_pose','vehicle_lift'):", "for key in ('driving_pose','gunner_pose','vehicle_lift'):")
code=code.replace("verts=[(x*2.55,y*.9,.72+z*.36)", "verts=[(x*2.175,y*.85,.52+z*.26)")
code=code.replace("'source':'Raven_V16_Assembly / CalhounBurns_V1'", "'source':'Raven_V16_Assembly / CalhounBurns_V2'")
code=code.replace("'spare_control':'RV_SpareEjection'", "'source_blend':'art_source/Raven/Raven_V16_Assembly.blend'")
# Save any live changes before loading the canonical source. Never overwrite it.
code=code.replace("bpy.app.driver_namespace['_mask_asset_review_active']=True;bpy.app.timers.register(run", "\nif bpy.data.is_dirty:\n    from datetime import datetime\n    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'art_source/Raven'/('Session_before_game_export_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.blend')),copy=True,compress=True)\nbpy.app.driver_namespace['_mask_asset_review_active']=True;bpy.app.timers.register(run")
exec(compile(code,'<raven-game-export>','exec'))
