import bpy,bmesh
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');S=bpy.context.scene;R=bpy.data.objects['BoulderHill_Control']
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
S.frame_set(1)
# Remove coplanar asphalt under the hangar floor, retaining the front forecourt.
for v in bpy.data.objects['BH_StationSlab'].data.vertices:
    if v.co.y>38:v.co.y=0
def drv(ob,path,index,expr,variables):
    f=ob.driver_add(path,index) if index is not None else ob.driver_add(path);d=f.driver
    while d.variables:d.variables.remove(d.variables[0])
    for name,key in variables:
        v=d.variables.new();v.name=name;v.type='SINGLE_PROP';v.targets[0].id=R;v.targets[0].data_path='["'+key+'"]'
    d.expression=expr
R['_sign_gun']=0.
drv(R,'["_sign_gun"]',None,'min(max(v,min(1,max(0,(b-.40)/.15))),min(1,max(0,(max(h,min(1,max(0,(b-.20)/.22)))-.85)/.15)))',[('v','sign_guns'),('b','battle_mode'),('h','sign_open')])
gun=bpy.data.objects['BH_SignCannonSlide'];drv(gun,'location',1,'1.75-.44*p',[('p','_sign_gun')]);drv(gun,'scale',1,'.20+.80*p',[('p','_sign_gun')])
# Correct closed manufactured mesh normals before final inspection.
for ob in S.objects:
    if ob.type=='MESH' and ob.get('BH_module') not in {None,'rock'}:
        bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(ob.data);bm.free()
for o in S.objects:
    if o.animation_data:
        for f in o.animation_data.drivers:f.driver.expression+=' + 0.0'
    o.update_tag()
S.frame_set(181);S.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(P/'art_source/Boulder_Hill/BoulderHill_V2_Assembly.blend'),compress=True)
print('MECHANISMS_V2_REFINED')
