import bpy,json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');bpy.ops.wm.open_mainfile(filepath=str(P/'art_source/Thunderhawk/Thunderhawk_V12.blend'))
s=bpy.context.scene;report={'file':bpy.data.filepath,'objects':{},'materials':{},'shading':[],'light_paths':{k:getattr(s.cycles,k) for k in ['max_bounces','transmission_bounces','transparent_max_bounces']}}
for ob in bpy.data.collections['THK9_Exterior'].objects:
    if ob.type=='MESH' and ob.name.startswith(('THK_Windshield','THK_DoorGlass','THK_RearGlass','THK_QuarterGlass','THK_DoorRoofInset')):
        report['objects'][ob.name]={'materials':[m.name for m in ob.data.materials],'hidden':ob.hide_render,
            'modifiers':[{'name':m.name,'type':m.type,'thickness':getattr(m,'thickness',None)} for m in ob.modifiers]}
        for m in ob.data.materials:
            if m.name in report['materials']:continue
            nodes=[]
            for node in m.node_tree.nodes:
                vals={}
                for inp in node.inputs:
                    if hasattr(inp,'default_value'):
                        value=inp.default_value
                        try:value=list(value)
                        except TypeError:pass
                        if isinstance(value,(float,int,str,list,bool)):vals[inp.name]=value
                nodes.append({'name':node.name,'type':node.type,'inputs':vals})
            report['materials'][m.name]={'diffuse':list(m.diffuse_color),'nodes':nodes,'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links]}
for screen in bpy.data.screens:
    for ar in screen.areas:
        if ar.type=='VIEW_3D':report['shading'].append({'type':ar.spaces.active.shading.type,'color_type':ar.spaces.active.shading.color_type})
(P/'docs/qa/glass_before_v13.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
