import bpy,math,json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem/art_source/Thunderhawk');s=bpy.context.scene
c=bpy.data.collections['MT10_Character'];root=bpy.data.objects['MT_Root_Seated'];mask=bpy.data.objects['Spectrum_Mask_Attach']
silver=bpy.data.materials['Spectrum_SilverShell'];red=bpy.data.materials['MT_RedGlovesTrim'];blue=bpy.data.materials['Spectrum_BlueVisor'];black=bpy.data.materials['Spectrum_Recess']
source=(P/'scripts/build_thunderhawk_v10.py').read_text(encoding='utf-8-sig');exec(source[source.index('def own('):source.index('# Driver seated')])
for n in ['Spectrum_BlueVisor','Spectrum_VisorRecess','Spectrum_RedBrow']:
 o=bpy.data.objects.get(n)
 if o:bpy.data.objects.remove(o,do_unlink=True)
def surface(n,verts,faces,m,thick=.004):
 me=bpy.data.meshes.new(n);me.from_pydata(verts,[],faces);me.update();me.materials.append(m);o=bpy.data.objects.new(n,me);c.objects.link(o);o.parent=mask
 if thick:mod=o.modifiers.new('ShellThickness','SOLIDIFY');mod.thickness=thick
 bevel=o.modifiers.new('MoldedEdge','BEVEL');bevel.width=.003;bevel.segments=3
 for f in me.polygons:f.use_smooth=True
 return o
y=.4
# A single wraparound visor, rectangular perimeter, bowed around the face.
verts=[]
for z in [1.062,1.163]:
 for i in range(25):
  u=(i/24*2-1);verts.append((-.234-.047*u*u,y+.108*u,z-.009*u*u))
surface('Spectrum_BlueVisor',verts,[(i,i+1,i+26,i+25) for i in range(24)],blue)
# Broad swept brow with slanted trapezoid sides rather than a rectangular bar.
v=[(-.215,y-.115,1.166),(-.215,y+.115,1.166),(-.254,y+.125,1.218),(-.254,y-.125,1.218),(-.302,y-.115,1.166),(-.302,y+.115,1.166),(-.321,y+.125,1.218),(-.321,y-.125,1.218)]
surface('Spectrum_RedBrow',v,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(3,2,6,7),(0,3,7,4),(1,5,6,2)],red,0)
# Cheek plates connect the central breathing shield to helmet and collar.
for sg,side in [(1,'L'),(-1,'R')]:
 v=[(-.237,y+sg*.055,1.091),(-.272,y+sg*.107,1.067),(-.323,y+sg*.112,1.012),(-.276,y+sg*.087,.993),(-.230,y+sg*.058,1.002)]
 surface('Spectrum_Cheek_'+side,v,[(0,1,2,3,4)],silver)
# Widen the central shield and smooth its manufactured edges slightly.
o=bpy.data.objects['Spectrum_Respirator']
for v in o.data.vertices:
 v.co.y=y+(v.co.y-y)*.91
for m in o.modifiers:
 if m.type=='BEVEL':m.width=.007;m.segments=4
# Suit material should read as fabric, not polished armor.
m=bpy.data.materials['MT_GreyFlightSuit'];node=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');node.inputs['Roughness'].default_value=.78
noise=m.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=230
bump=m.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.0006
m.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],node.inputs['Normal'])
s.frame_set(97);bpy.ops.wm.save_as_mainfile(filepath=str(P/'Thunderhawk_V10.blend'),compress=True)
print('V10_MASK_CORRECTED')
