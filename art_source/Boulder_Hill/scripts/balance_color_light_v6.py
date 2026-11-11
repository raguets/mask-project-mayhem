import bpy,json,hashlib,struct
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Boulder_Hill';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
assert Path(bpy.data.filepath).name=='BoulderHill_V5_Assembly.blend'
def digest():
    result={}
    for o in S.objects:
        if o.type!='MESH':continue
        h=hashlib.sha256()
        for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
        for f in o.data.polygons:h.update(struct.pack('<'+'I'*len(f.vertices),*f.vertices))
        result[o.name]=h.hexdigest()
    return result
before=digest();mat=bpy.data.materials['BH_Sandstone']
for node in mat.node_tree.nodes:
    if node.type=='VALTORGB':
        low=(.085,.026,.011,1);high=(.335,.124,.053,1)
        for e in node.color_ramp.elements:e.color=tuple(low[i]*(1-e.position)+high[i]*e.position for i in range(4))
mat.diffuse_color=(.21,.075,.032,1);mat['palette_note']='Warm medium brown: lighter than rejected V5, retaining a brown hue instead of V4 beige.'
bg=next(n for n in S.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Strength'].default_value=.85
bpy.data.objects['BH_DesertSun'].data.energy=3.0
bpy.data.objects['BH_Key'].data.energy=5000
ld=bpy.data.lights.new('BH_SoftDayFill','AREA');ld.energy=14000;ld.shape='DISK';ld.size=26;ld.color=(1.,.96,.91)
light=bpy.data.objects.new(ld.name,ld);bpy.data.collections['BH_Studio'].objects.link(light);light.location=(-14,-24,28);light.rotation_euler=(Vector((0,5,9))-light.location).to_track_quat('-Z','Y').to_euler()
S.view_settings.exposure=.25
viewports=[]
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.shading.type='MATERIAL'
            if hasattr(sp.shading,'use_scene_lights'):sp.shading.use_scene_lights=True
            if hasattr(sp.shading,'use_scene_world'):sp.shading.use_scene_world=True
            viewports.append({'scene_lights':sp.shading.use_scene_lights,'scene_world':sp.shading.use_scene_world})
assert before==digest()
S['BoulderVersion']='V6';S.name='BoulderHill_V6_Assembly';S['color_lighting_note']='User revision: V5 too dark, scene lacked light. Warm intermediate brown, stronger daylight ambient and broad soft frontal fill. Geometry and mechanisms unchanged.'
S.frame_set(211);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'BoulderHill_V6_Assembly.blend'),compress=True)
(A/'color_light_v6.json').write_text(json.dumps({'source':'BoulderHill_V5_Assembly.blend','output':'BoulderHill_V6_Assembly.blend','geometry_unchanged':True,'meshes_compared':len(before),'diffuse':list(mat.diffuse_color),'world_strength':.85,'sun_strength':3.,'key_power_w':5000,'soft_fill_power_w':14000,'exposure_stops':.25,'viewport':viewports},indent=2))
print('BROWN_DAYLIGHT_V6_SAVED GEOMETRY_UNCHANGED',len(before))
