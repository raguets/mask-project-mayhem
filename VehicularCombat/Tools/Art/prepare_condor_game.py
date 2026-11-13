"""Installed Blender MCP: Condor V20, persistent two wheels and Brad's own rig."""
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');T=P/'VehicularCombat/Tools/Art'
code=(T/'prepare_hurricane_game.py').read_text(encoding='utf-8-sig')
code=code.replace('Hurricane','Condor').replace('HondoMacLean','BradTurner').replace('Hondo','Brad').replace('HU_','CD_').replace('HMC_','BT_').replace('V7','V20')
code=code.replace("control['battle_mode']","control['transform']").replace("control['spare_eject']","control['rotor_angle']")
code=code.replace("rig['mask_on']=True;rig.update_tag()", "rig['mask_on']=True;rig['driving_pose']=1.;rig['in_vehicle']=1.;control['hover_height']=0.;control['forward_flight']=0.;rig.update_tag();control.update_tag();bpy.context.view_layer.update()")
code=code.replace("o.type=='MESH' and any(c.name in ('CD_Body','CD_Interior','CD_RunningGear','CD_Weapons')", "o.type in {'MESH','CURVE','FONT'} and any(c.name in ('Condor_Vehicle',)")
code=code.replace('for group in o.vertex_groups:','for group in getattr(o,\'vertex_groups\',[]):')
a=code.index('        wheels=[]');b=code.index('        for i in range(97):',a)
code=code[:a]+'''        wheels=[]
        for label,front,fold in [('F',True,'Condor_FrontWheel'),('R',False,'Condor_TailRotorSpin')]:
            ob=bpy.data.objects['Condor_'+('Front' if front else 'Rear')+'_PersistentTire']
            ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
            points=[ev.matrix_world@v.co for v in me.vertices];p=Vector([(min(v[k] for v in points)+max(v[k] for v in points))/2 for k in range(3)]);ev.to_mesh_clear()
            wheels.append({'prefix':'Front' if front else 'Rear','label':label,'fold':fold,'road_position_cm':[p.x*100,-p.y*100,p.z*100],'position_cm':[p.x*100,-p.y*100,p.z*100],'radius_cm':35.3,'object':ob.name})
'''+code[b:]
a=code.index('        for w in wheels:\n            ob=');b=code.index("        control['transform']=0.",a);code=code[:a]+code[b:]
code=code.replace("wheel=next((w for w in wheels if ob.name.startswith(w['prefix']+'_')),None)", "wheel=None\n            ancestor=ob\n            while ancestor:\n                wheel=next((w for w in wheels if ancestor.name==w['fold']),None)\n                if wheel:break\n                ancestor=ancestor.parent")
code=code.replace("glass=any(s.material and 'Glass' in s.material.name for s in ob.material_slots)", "glass=any(s.material and ('Glass' in s.material.name or 'Windshield' in s.material.name) for s in ob.material_slots)")
code=code.replace("key='SM_CD_'+wheel['label'] if wheel else 'SM_'+owner+('_Glass' if glass else '')", "key='SM_'+owner+('_Glass' if glass else '')")
code=code.replace("'CD_UpperChassisLift'", "'Condor_Control'")
code=code.replace("verts=[(x*2.55,y*.9,.72+z*.36)", "verts=[(-.05+x*1.15,y*.19,.65+z*.25)")
code=code.replace("'spare_control':'CD_SpareEjection'", "'spare_control':'NONE','source_blend':'art_source/Condor/Condor_V20_Assembly.blend','vehicle_category':'road_helicopter'")
# Retain central rotor ownership for runtime rotation, without duplicating either tire.
code=code.replace("write('manifest.json',manifest);", "\n        for part in parts:\n            node=bpy.data.objects.get(part['control']);anc=[]\n            while node:anc.append(node.name);node=node.parent\n            if 'Condor_MainRotorHub' in anc:part.update(rotor_axis=[0,0,1],rotor_pivot_cm=[-44,0,169],rotor_speed=1440.)\n            elif 'Condor_TailRotorSpin' in anc:part.update(rotor_axis=[0,1,0],rotor_pivot_cm=[-200,0,65],rotor_speed=2160.)\n        write('manifest.json',manifest);")
# Exact pivots are sampled from the live end state, replacing approximate fallback.
code=code.replace("        control['transform']=0.;control.update_tag();bpy.context.view_layer.update()\n        for key", "        rotor_centers={n:[v*100 for v in bpy.data.objects[n].matrix_world.translation] for n in ['Condor_MainRotorHub','Condor_TailRotorSpin']}\n        control['transform']=0.;control.update_tag();bpy.context.view_layer.update()\n        for key")
code=code.replace("part.update(rotor_axis=[0,0,1],rotor_pivot_cm=[-44,0,169],rotor_speed=1440.)", "part.update(rotor_axis=[0,0,1],rotor_pivot_cm=[rotor_centers['Condor_MainRotorHub'][0],-rotor_centers['Condor_MainRotorHub'][1],rotor_centers['Condor_MainRotorHub'][2]],rotor_speed=1440.)")
code=code.replace("part.update(rotor_axis=[0,1,0],rotor_pivot_cm=[-200,0,65],rotor_speed=2160.)", "part.update(rotor_axis=[0,1,0],rotor_pivot_cm=[rotor_centers['Condor_TailRotorSpin'][0],-rotor_centers['Condor_TailRotorSpin'][1],rotor_centers['Condor_TailRotorSpin'][2]],rotor_speed=2160.)")
exec(compile(code,'<condor-game-export>','exec'))
