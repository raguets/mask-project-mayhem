import bpy,numpy as np,json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Switchblade';(A/'textures').mkdir(exist_ok=True)
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
root=bpy.data.objects['Switchblade_Control'];bpy.context.scene.frame_set(121);root.update_tag();bpy.context.view_layer.update()
polygons=[]
for o in bpy.data.objects:
 if o.type=='MESH' and (o.name.startswith('SB_WingOrangeFlash_1') or o.name.startswith('SB_WingRedFlash_1')) and sum(v.co.z for v in o.data.vertices)/len(o.data.vertices)>1.5:
  polygons.append({'points':[(v.co.x,abs(v.co.y)) for v in list(o.data.vertices)[:4]],'color':(.9,.115,.008) if 'Orange' in o.name else (.48,.009,.035)})
W=512;H=1024;xmin=-1.10;xmax=.25;ymin=.60;ymax=3.95
x,y=np.meshgrid(np.linspace(xmin,xmax,W),np.linspace(ymin,ymax,H));rgba=np.zeros((H,W,4),dtype=np.float32)
for item in polygons:
 pts=item['points'];inside=np.zeros((H,W),dtype=bool)
 for i in range(len(pts)):
  ax,ay=pts[i];bx,by=pts[(i+1)%len(pts)];inside ^= ((ay>y)!=(by>y)) & (x<(bx-ax)*(y-ay)/(by-ay+1e-12)+ax)
 rgba[inside,:3]=item['color'];rgba[inside,3]=1
im=bpy.data.images.new('SB_FlushWingMarkings',width=W,height=H,alpha=True);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(rgba.ravel());im.filepath_raw=str(A/'textures/WingMarkings.png');im.file_format='PNG';im.save();im.pack()
mat=bpy.data.materials['SB_DeepNavyPaint'].copy();mat.name='SB_WingPaint_FlushMarkings';nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');tex=nodes.new('ShaderNodeTexImage');tex.image=im;tex.interpolation='Linear';mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[1].default_value=(.016,.043,.095,1);links.new(tex.outputs['Alpha'],mix.inputs[0]);links.new(tex.outputs['Color'],mix.inputs[2]);links.new(mix.outputs[0],bs.inputs['Base Color'])
for side in [-1,1]:
 o=bpy.data.objects['SB_MainWing_'+str(side)];o.data.materials.clear();o.data.materials.append(mat);uv=o.data.uv_layers.get('WingPlanarUV') or o.data.uv_layers.new(name='WingPlanarUV')
 for face in o.data.polygons:
  for li in face.loop_indices:
   p=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=((p.x-xmin)/(xmax-xmin),(abs(p.y)-ymin)/(ymax-ymin))
for o in list(bpy.data.objects):
 if o.name.startswith('SB_WingOrangeFlash') or o.name.startswith('SB_WingRedFlash'):bpy.data.objects.remove(o,do_unlink=True)
(A/'textures/wing_marking_polygons.json').write_text(json.dumps(polygons,indent=2));root['markings_note']='UV planar RGBA texture packed in blend, no floating decal surfaces. Polygon source retained in textures/wing_marking_polygons.json.'
bpy.context.scene.frame_set(1);root.update_tag();bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Switchblade_V14_Assembly.blend'),compress=True)
print('FLUSH_WING_MARKINGS_V14_SAVED',len(polygons))
