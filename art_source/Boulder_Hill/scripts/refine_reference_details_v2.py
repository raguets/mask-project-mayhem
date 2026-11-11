import bpy,bmesh,math
from pathlib import Path
from math import sin,cos,pi
from mathutils import noise,Vector
P=Path('G:/DEV/mask-project-mayhem');S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
S.frame_set(1);R=bpy.data.objects['BoulderHill_Control']
# Broader taper under the cap follows the photographed sandstone mass above the garage.
ob=bpy.data.objects['BH_RockColumnOuter'];N=128;H=49
for j in range(H):
    t=j/(H-1);z=6.72+t*5.30;base=7.2*(1-t)**1.12+2.55*t
    for i in range(N):
        a=i*2*pi/N;nn=noise.noise(Vector((cos(a)*2.8,sin(a)*2.8,t*1.7)))
        r=base+(.34*nn+.07*noise.noise(Vector((cos(a)*10,sin(a)*10,t*4))))*sin(pi*t)
        ob.data.vertices[j*N+i].co=(7+r*cos(a),6+r*sin(a),z+.025*sin(a*5+t))
ob.data.update()
def boxgeom(x0,x1,y0,y1,z0,z1):
    v=[(x,y,z) for x in [x0,x1] for y in [y0,y1] for z in [z0,z1]]
    f=[(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)];return v,f
def addbox(name,bounds,material):
    me=bpy.data.meshes.new(name+'_Editable');v,f=boxgeom(*bounds);me.from_pydata(v,[],f);me.materials.append(bpy.data.materials[material]);me.update();o=bpy.data.objects.new(name,me);bpy.data.collections['BH_Shop'].objects.link(o);o.parent=R;o['BH_group']='shop_static';o['BH_module']='shop';return o
wall=bpy.data.objects['BH_ShopSideWall_-0.08'];vs=[];fs=[]
for bd in [(-.16,0,-11,.10,.05,1.0),(-.16,0,-11,.10,4.70,5.85)]+[(-.16,0,y-.075,y+.075,1,4.7) for y in [-10.92,-7.4,-3.9,.025]]:
    v,f=boxgeom(*bd);offset=len(vs);vs+=v;fs.extend(tuple(i+offset for i in p) for p in f)
me=bpy.data.meshes.new('BH_ShopSideGlazedWall_V2');me.from_pydata(vs,[],fs);me.materials.append(bpy.data.materials['BH_StationPaint']);me.update();wall.data=me
for i,(a,b) in enumerate([(-10.83,-7.49),(-7.31,-3.99),(-3.81,-.065)]):
    addbox('BH_ShopSideWindow_'+str(i),(-.09,-.072,a,b,1.04,4.66),'BH_StationGlass')
    for z in [1.,4.70]:addbox('BH_ShopSideWindowRail_'+str((i,z)),(-.18,.02,a,b,z-.045,z+.045),'BH_ArmorEdges')
# Correct all newly created closed meshes.
for o in [wall]+[o for o in bpy.data.objects if o.name.startswith('BH_ShopSideWindow')]:
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(o.data);bm.free()
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P/'art_source/Boulder_Hill/BoulderHill_V2_Assembly.blend'),compress=True)
print('REFERENCE_DETAILS_V2')
