"""Unsaved diagnostic view of actual control edges, before surface modifiers."""
import bpy
from pathlib import Path
from mathutils import Vector
s=bpy.context.scene;s.frame_set(1)
prefixes=('THK_Hood','THK_FrontFenderCrown','THK_RearFenderCrown','THK_FrontQuarterSkin','THK_RearQuarterSkin',
          'THK_DoorShell','THK_DoorAFrame','THK_C_Pillar','THK_RoofSpine','THK_RearDeck','THK_NoseFascia','THK_RearPanel')
keep=[o for o in s.objects if o.type=='MESH' and o.name.startswith(prefixes) and not any(t in o.name for t in ('Paint','Lightning','RubStrip','Return'))]
gray=bpy.data.materials.new('Diagnostic_ControlGray');gray.diffuse_color=(.56,.58,.60,1)
black=bpy.data.materials.new('Diagnostic_EdgeBlack');black.diffuse_color=(.008,.01,.012,1)
for ob in s.objects:
    if ob.type=='MESH':ob.hide_render=ob not in keep and not ob.name.startswith('THK_Tire_')
curve=bpy.data.curves.new('Actual_Control_Edges','CURVE');curve.dimensions='3D';curve.bevel_depth=.00085;curve.bevel_resolution=0;curve.resolution_u=1
for ob in keep:
    for m in ob.modifiers:m.show_render=False
    ob.data.materials.clear();ob.data.materials.append(gray)
    for e in ob.data.edges:
        line=curve.splines.new('POLY');line.points.add(1)
        for point,vi in zip(line.points,e.vertices):
            p=ob.matrix_world@(ob.data.vertices[vi].co+ob.data.vertices[vi].normal*.0007);point.co=(*p,1)
edge_ob=bpy.data.objects.new('Diagnostic_Wires',curve);s.collection.objects.link(edge_ob);curve.materials.append(black)
s.render.engine='BLENDER_WORKBENCH';s.display.shading.color_type='MATERIAL';s.display.shading.light='STUDIO'
s.display.shading.show_cavity=True;s.display.shading.show_shadows=False;s.view_settings.view_transform='Standard'
s.camera.location=(6.6,-6.8,4.1);s.camera.rotation_euler=(Vector((0,0,.66))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=5.65
s.render.resolution_x=1600;s.render.resolution_y=1100;s.render.image_settings.file_format='PNG'
s.render.filepath='G:/DEV/mask-project-mayhem/art_source/Thunderhawk/renders/v9/control_cage.png'
bpy.ops.render.render(write_still=True)
print('THK9_ACTUAL_CONTROL_EDGES',len(keep),'surfaces; source not saved')
