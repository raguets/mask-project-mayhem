import bpy
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Hurricane';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
S.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Hurricane_V7_before_side_UV.blend'),copy=True,compress=True)
image=bpy.data.images.load(str(A/'textures/side_flames_rgba.png'),check_existing=True);image.pack()
for label in ['L','R']:
 o=bpy.data.objects['HU_SculptedSide_'+label];mat=bpy.data.materials['HU_TurquoisePaint'].copy();mat.name='HU_SideFlameFinish_'+label;n=mat.node_tree.nodes;l=mat.node_tree.links;p=next(q for q in n if q.type=='BSDF_PRINCIPLED');mix=n.new('ShaderNodeMixRGB');mix.inputs[1].default_value=p.inputs['Base Color'].default_value;tex=n.new('ShaderNodeTexImage');tex.image=image;tex.extension='CLIP';uv=n.new('ShaderNodeUVMap');uv.uv_map='FlameProjectionUV';l.new(uv.outputs['UV'],tex.inputs['Vector']);l.new(tex.outputs['Color'],mix.inputs[2]);l.new(tex.outputs['Alpha'],mix.inputs[0]);l.new(mix.outputs['Color'],p.inputs['Base Color']);o.data.materials.clear();o.data.materials.append(mat)
 layer=o.data.uv_layers.get('FlameProjectionUV') or o.data.uv_layers.new(name='FlameProjectionUV')
 for f in o.data.polygons:
  f.material_index=0
  for li in f.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co;layer.data[li].uv=((v.x+2.7)/5.4,(v.z-.30)/1.10)
for o in list(S.objects):
 if o.name.startswith(('HU_SweptFlames_','HU_FlameEmber_')):bpy.data.objects.remove(o,do_unlink=True)
S['side_paint_note']='UV-projected editable original flame outlines, packed RGBA texture; avoids geometric paint crossing wheel arch surfaces. Texture generator and polygon JSON retained. Hood/roof/trunk paint remains editable geometry.'
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Hurricane_V7_Assembly.blend'),compress=True);print('SIDE_PAINT_UV_SAVED')
