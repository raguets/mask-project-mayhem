"""User-requested parcel shelf and M.A.S.K. plate, editable separate parts."""
import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');T=P/'art_source/Thunderhawk';s=bpy.context.scene;co=bpy.data.collections['THK11_Interior'];root=bpy.data.objects['THK_Root']
def material(name,col,metal=0,rough=.6):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*col,1);p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
carpet=material('THK13_ParcelShelfCarpet',(.023,.027,.031),0,.88);black=material('THK13_PlateBacking',(.006,.008,.011),.1,.46);edge=material('THK13_PlateFrame',(.23,.27,.29),.72,.32)
ns=carpet.node_tree.nodes;ls=carpet.node_tree.links;noise=ns.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=230;bump=ns.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.0008;bump.inputs['Strength'].default_value=.28;ls.new(noise.outputs['Fac'],bump.inputs['Height']);ls.new(bump.outputs[0],next(n for n in ns if n.type=='BSDF_PRINCIPLED').inputs['Normal'])
def mesh(name,vv,ff,mat,thick=0,bevel=0):
    old=bpy.data.objects.get(name)
    if old:bpy.data.objects.remove(old,do_unlink=True)
    me=bpy.data.meshes.new(name+'_Editable');me.from_pydata(vv,[],ff);me.update();ob=bpy.data.objects.new(name,me);co.objects.link(ob);me.materials.append(mat);ob.parent=root
    if thick:mod=ob.modifiers.new('PanelThickness','SOLIDIFY');mod.thickness=thick
    if bevel:mod=ob.modifiers.new('RoundedEdges','BEVEL');mod.width=bevel;mod.segments=3
    return ob
def box(name,p,d,mat,bevel=.003):
    vv=[(p[0]+sx*d[0]/2,p[1]+sy*d[1]/2,p[2]+sz*d[2]/2) for sx,sy,sz in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
    return mesh(name,vv,[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)],mat,bevel=bevel)
shelf=mesh('THK_ParcelShelf',[(-.795,-.79,.824),(-.795,.79,.824),(-1.76,.78,.819),(-1.76,-.78,.819)],[(0,1,2,3)],carpet,thick=.022,bevel=.005)
shelf['design_note']='Interpreted parcel shelf explicitly requested by user 2026-11-02; occludes trunk from cabin/rear glazing. Dimensions estimated.'
box('THK_ParcelShelf_FrontLip',(-.795,0,.832),(.028,1.58,.036),carpet,.006)
box('THK_RearPlate_Backing',(-2.443,0,.428),(.012,.340,.086),black,.005)
for y in [-.169,.169]:box('THK_RearPlate_FrameSide_'+str(y),(-2.451,y,.428),(.004,.005,.086),edge,.001)
for z in [.386,.470]:box('THK_RearPlate_FrameEdge_'+str(z),(-2.451,0,z),(.004,.340,.004),edge,.001)
# The original supplied image remains unchanged. UV mapping samples its actual
# M.A.S.K. wordmark, rather than inventing a replacement logo or external image.
logo=material('THK13_MASK_Logo_FromUserReference',(1,1,1),0,.56);n=logo.node_tree.nodes;l=logo.node_tree.links;bs=next(n for n in n if n.type=='BSDF_PRINCIPLED')
image=bpy.data.images.load(str(P/'Images de reference/Matt Trakker/images (7).jpg'),check_existing=True);image.pack()
tex=n.new('ShaderNodeTexImage');tex.image=image;tex.interpolation='Linear';uv=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY_ADD';mapping.inputs[1].default_value=(276/413,46/484,1);mapping.inputs[2].default_value=(125/413,1-405/484,0)
l.new(uv.outputs['UV'],mapping.inputs[0]);l.new(mapping.outputs[0],tex.inputs['Vector']);l.new(tex.outputs['Color'],bs.inputs['Base Color'])
plate=mesh('THK_RearPlate_MASK_Logo',[(-2.4525,.150,.403),(-2.4525,-.150,.403),(-2.4525,-.150,.453),(-2.4525,.150,.453)],[(0,1,2,3)],logo)
uvlayer=plate.data.uv_layers.new(name='LogoCropUV')
for loop,coord in zip(uvlayer.data,[(0,0),(1,0),(1,1),(0,1)]):loop.uv=coord
for y in [-.151,.151]:
    for z in [.394,.462]:box('THK_RearPlate_Fastener_'+str(y)+'_'+str(z),(-2.455,y,z),(.004,.007,.007),edge,.002)
box('THK_RearPlate_CentralMount',(-2.347,0,.428),(.18,.08,.045),black,.003)
plate['logo_source']='User-supplied portrait images (7).jpg, M.A.S.K. wordmark sampled through editable UV mapping; reference file unchanged.'
plate['mount']='Fixed central rear mount, between reactor housings; rear cover translates behind it.'
s['V13_RearAdditions']='User-requested carpeted parcel shelf and M.A.S.K. logo plate between reactors; estimated construction.'
bpy.ops.wm.save_as_mainfile(filepath=str(T/'Thunderhawk_V13.blend'),compress=True)
print('V13_PARCEL_SHELF_AND_MASK_PLATE_SAVED')
