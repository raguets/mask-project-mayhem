"""Physical lightly tinted glazing and a viewport that evaluates the shader."""
import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');T=P/'art_source/Thunderhawk';s=bpy.context.scene
assert bpy.data.objects.get('THK_Hood')
mat=bpy.data.materials.get('THK13_LightlyTintedGlass') or bpy.data.materials.new('THK13_LightlyTintedGlass')
mat.use_nodes=True;mat.diffuse_color=(.13,.22,.21,.28)
n=mat.node_tree.nodes;n.clear();links=mat.node_tree.links
out=n.new('ShaderNodeOutputMaterial');glass=n.new('ShaderNodeBsdfGlass');glass.name='Physical glass — reflection and refraction'
glass.inputs['Color'].default_value=(.93,.98,.965,1);glass.inputs['Roughness'].default_value=.025;glass.inputs['IOR'].default_value=1.50
absorb=n.new('ShaderNodeVolumeAbsorption');absorb.inputs['Color'].default_value=(.55,.80,.71,1);absorb.inputs['Density'].default_value=12
links.new(glass.outputs[0],out.inputs['Surface']);links.new(absorb.outputs[0],out.inputs['Volume'])
objects=[]
for ob in bpy.data.collections['THK9_Exterior'].objects:
    if ob.type=='MESH' and (ob.name=='THK_Windshield' or ob.name.startswith(('THK_DoorGlass','THK_RearGlass','THK_QuarterGlass','THK_DoorRoofInset'))):
        ob.data.materials.clear();ob.data.materials.append(mat);objects.append(ob.name)
s.cycles.max_bounces=16;s.cycles.transmission_bounces=12;s.cycles.transparent_max_bounces=12
s.cycles.preview_samples=16
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.shading.type='MATERIAL'
            area.spaces.active.shading.use_scene_world=False
            area.spaces.active.shading.studiolight_rotate_z=.6
s['THK_Version']='V13';s['THK13_Glass']='Physical glass, IOR 1.50, roughness .025, lightly green tinted. Thickness inherited from existing glazing; tint is an artistic estimate.'
s.name='THK_V13_Matt_Spectrum_Glazing'
bpy.ops.wm.save_as_mainfile(filepath=str(T/'Thunderhawk_V13.blend'),compress=True)
(T/'glass_v13.json').write_text(json.dumps({'objects':objects,'IOR':1.5,'roughness':.025,'viewport_before':'SOLID, grey opaque diffuse display','viewport_after':'MATERIAL','tint':'light green-grey, estimated'},indent=2))
print('V13_PHYSICAL_GLASS_SAVED',json.dumps(objects))
