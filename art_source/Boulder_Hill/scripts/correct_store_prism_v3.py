"""User correction: the storefront IS a triangular prism, pivoting as one part."""
import bpy,bmesh,math
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');S=bpy.context.scene;R=bpy.data.objects['BoulderHill_Control']
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
S.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(P/'art_source/Boulder_Hill/Session_before_prism_v3.blend'),copy=True,compress=True)
pivot=bpy.data.objects['BH_StorefrontPivot']
remove=[o for o in S.objects if o.name.startswith(('BH_ArmorSheet','BH_ArmorPanelRib','BH_ArmorRivet','BH_ArmorMaskWordmark'))]
for ob in remove:bpy.data.objects.remove(ob,do_unlink=True)
children=list(pivot.children)
pivot.animation_data_clear();pivot.location=(-5,-11,.25);pivot.rotation_euler=(0,0,0);bpy.context.view_layer.update()
for ob in children:ob.matrix_parent_inverse=pivot.matrix_world.inverted()
co=bpy.data.collections['BH_Shop'];steel=bpy.data.materials['BH_ArmorSteel'];edge=bpy.data.materials['BH_ArmorEdges']
def mesh(name,v,f,mat):
    me=bpy.data.meshes.new(name+'_Editable');me.from_pydata(v,[],f);me.materials.append(mat);me.update();o=bpy.data.objects.new(name,me);co.objects.link(o);o.parent=pivot;o.matrix_parent_inverse=pivot.matrix_world.inverted();o['BH_group']='store_armor';o['BH_module']='shop';return o
# Cross-section A = glazed foot, B = glazed header, C = rear foot.
# One quarter-turn about AB's lower edge puts the original glass against the ground.
xl,xr=-9.65,-.35;ya,yc=-11.,-5.70;za,zb=.25,5.55
v=[(x,y,z) for x in [xl,xr] for y,z in [(ya,za),(ya,zb),(yc,za)]]
body=mesh('BH_StorefrontTriangularPrism',v,[(0,2,1),(3,4,5),(0,3,5,2),(1,2,5,4)],steel)
solid=body.modifiers.new('EditableArmorThickness','SOLIDIFY');solid.thickness=.055;solid.offset=-1
bevel=body.modifiers.new('ArmorEdgeBevel','BEVEL');bevel.width=.016;bevel.segments=3
# Five structural channels on the inclined face, retained on the same prism.
def beam(name,a,b,width,depth):
    a,b=Vector(a),Vector(b);q=(b-a).to_track_quat('Z','Y');center=(a+b)/2;L=(b-a).length
    vv=[tuple(center+q@Vector((x,y,z))) for x in [-width/2,width/2] for y in [-depth/2,depth/2] for z in [-L/2,L/2]]
    ob=mesh(name,vv,[(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)],edge);mod=ob.modifiers.new('ChannelEdges','BEVEL');mod.width=.018;mod.segments=3;return ob
for i,x in enumerate([-8.8,-6.9,-5,-3.1,-1.2]):
    beam('BH_PrismArmorChannel_'+str(i),(x,-10.84,5.45),(x,-5.64,.25),.13,.13)
    for j,(y,z) in enumerate([(-10.65,5.26),(-5.85,.46)]):beam('BH_PrismChannelFastener_'+str((i,j)),(x,y+.045,z+.045),(x,y+.095,z+.095),.20,.20)
# Continuous steel edge along the prism's two triangular end plates.
for i,x in enumerate([xl,xr]):
    for j,(a,b) in enumerate([((x,ya,za),(x,ya,zb)),((x,ya,zb),(x,yc,za)),((x,yc,za),(x,ya,za))]):beam('BH_PrismSideEdge_'+str((i,j)),a,b,.07,.07)
# Recess furniture behind the physical sweep instead of letting it intersect the prism.
for name in ['BH_ServiceCounter','BH_Countertop']:bpy.data.objects[name].location.y+=3.1
f=pivot.driver_add('rotation_euler',0);d=f.driver
for name,key in [('v','store_armor'),('b','battle_mode')]:
    var=d.variables.new();var.name=name;var.type='SINGLE_PROP';var.targets[0].id=R;var.targets[0].data_path='["'+key+'"]'
d.expression='1.57079632679*max(v,min(1,max(0,(b-.05)/.35)))'
R.id_properties_ui('store_armor').update(description='Bascule du prisme entier : vitrine au sol, face acier inclinee visible. 0/1.')
pivot['mechanism']='Single triangular prism, 90 degree rotation about the lower storefront edge. Glazed face becomes the lower horizontal face; inclined steel side emerges from inside the shop.'
pivot['cross_section_m']=[5.3,5.3];pivot['user_reference']='Images de reference/prisme-triangulaire-k9-en.webp; user correction 2026-11-05'
for ob in list(pivot.children):
    if ob.type=='MESH':
        bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(ob.data);bm.free()
for ob in S.objects:
    if ob.animation_data:
        for f in ob.animation_data.drivers:f.driver.expression+=' + 0.0'
    ob.update_tag()
S.frame_set(181);S.frame_set(1);bpy.context.view_layer.update()
S['BoulderVersion']='V3';S['storefront_mechanism']='User-corrected single triangular prism, glazed face pivots to the ground; no separate emergence of an armor part.'
bpy.ops.wm.save_as_mainfile(filepath=str(P/'art_source/Boulder_Hill/BoulderHill_V3_Assembly.blend'),compress=True)
print('SINGLE_STOREFRONT_PRISM_V3_SAVED')
