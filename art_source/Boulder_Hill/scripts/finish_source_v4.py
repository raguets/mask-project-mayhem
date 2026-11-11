import bpy,bmesh,json,math,ast
from pathlib import Path
from mathutils import Vector
from math import pi,sin,cos
P=Path('G:/DEV/mask-project-mayhem');S=bpy.context.scene;R=bpy.data.objects['BoulderHill_Control']
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
S.frame_set(1)
# Blend the promontory's lower half into a broad natural spur of the mountain.
def spur(x,y):return 1.3*math.exp(-((x-7)/7)**2-((y-6)/6)**2)
roof=bpy.data.objects['BH_SandstoneRoof']
for v in roof.data.vertices:v.co.z+=spur(v.co.x,v.co.y)
front=bpy.data.objects['BH_SandstoneCliff_front'];N=211;H=36
for j in range(H):
    for v in front.data.vertices[j*N:(j+1)*N]:v.co.z+=spur(v.co.x,v.co.y)*j/(H-1)
# Solid flashing bridges the visible slot between the blue shop roof and the mountain.
name='BH_ShopMountainFlashing';assert name not in bpy.data.objects
v=[(x,y,z) for x in [-10.25,.03] for y in [.10,.85] for z in [6.35,6.64]];f=[(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)]
me=bpy.data.meshes.new(name+'_Editable');me.from_pydata(v,[],f);me.materials.append(bpy.data.materials['BH_WeatheredAzure']);me.update();o=bpy.data.objects.new(name,me);bpy.data.collections['BH_Shop'].objects.link(o);o.parent=R;o['BH_group']='shop_static';o['BH_module']='shop';be=o.modifiers.new('FlashingEdges','BEVEL');be.width=.018;be.segments=2
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
# Thunderhawk continues onto the surrounding terrain, leaving space for Rhino.
tree=ast.parse((P/'art_source/Boulder_Hill/scripts/build_base_v1.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='exit_route');exec(ast.unparse(fn).replace('* 15','* 22'))
pts,length=exit_route(15);route=bpy.data.objects['BH_Thunderhawk_ExitRoute']
for point,xyz in zip(route.data.splines[0].points,pts):point.co=(*xyz,1)
target=Vector((.2+12/2**.5,-12/2**.5,0))+Vector((1,-1,0)).normalized()*1.2
nearest=min(range(len(pts)),key=lambda i:(Vector(pts[i])-target).length);thk_frame=round(211+120*nearest/240)
meta=json.loads((P/'art_source/Boulder_Hill/exit_routes_v3.json').read_text());meta['Thunderhawk'].update(samples=pts,path_length_m=length,review_progress=nearest/240,review_frame=thk_frame);(P/'art_source/Boulder_Hill/exit_routes_v4.json').write_text(json.dumps(meta,indent=2))
for marker in S.timeline_markers:
    if marker.name=='THUNDERHAWK SORT':marker.frame=thk_frame
    elif marker.name=='RHINO SORT':marker.frame=510
S.timeline_markers.new('PRISME MI-BASCULE',frame=65)
text=bpy.data.texts.get('ASSET_README');text.clear();text.write((P/'art_source/Boulder_Hill/README.md').read_text(encoding='utf-8'))
S.camera.location=(33,-43,20);S.camera.rotation_euler=(Vector((0,-2,7))-S.camera.location).to_track_quat('-Z','Y').to_euler();S.camera.data.lens=43
bpy.ops.object.select_all(action='DESELECT');R.hide_set(False);R.select_set(True);bpy.context.view_layer.objects.active=R
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.shading.type='MATERIAL';sp.overlay.show_extras=False;sp.region_3d.view_location=(0,-2,7);sp.region_3d.view_distance=57;sp.region_3d.view_rotation=(Vector((33,-43,20))-Vector((0,-2,7))).to_track_quat('Z','Y')
        elif area.type=='PROPERTIES':area.spaces.active.context='OBJECT';area.spaces.active.pin_id=R
S.frame_set(211);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P/'art_source/Boulder_Hill/BoulderHill_V4_Assembly.blend'),compress=True)
print('SOURCE_V4_READY THUNDERHAWK_REVIEW_FRAME',thk_frame)
