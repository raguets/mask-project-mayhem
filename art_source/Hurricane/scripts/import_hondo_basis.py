import bpy,json
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Hurricane';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
assert not bpy.data.objects.get('HondoMacLean_Rig')
with bpy.data.libraries.load(str(P/'art_source/Bruce_Sato/BruceSato_V1.blend'),link=False) as (src,dst):dst.collections=['BS_Character']
char=dst.collections[0];S.collection.children.link(char);char.name='HMC_Character';r=next(o for o in char.all_objects if o.type=='ARMATURE');r.name='HondoMacLean_Rig';r.data=r.data.copy();r.data.name='HMC_EditableSkeleton';r.location=(0,0,0);r.scale=(1,1,1);r['driving_pose']=0.;r['mask_on']=False;r.update_tag();S.frame_set(1);bpy.context.view_layer.update()
mats={}
for o in list(char.all_objects):
    if o==r:continue
    o.name='HMC_'+o.name.removeprefix('BS_')
    if o.type=='MESH':
        o.data=o.data.copy();o.data.name=o.name+'_Editable'
        for i,m in enumerate(o.data.materials):
            if m not in mats:mats[m]=m.copy();mats[m].name='HMC_'+m.name
            o.data.materials[i]=mats[m]
    if o.animation_data:
        for f in o.animation_data.drivers:
            for v in f.driver.variables:
                for t in v.targets:
                    if isinstance(t.id,bpy.types.Object) and t.id.type=='ARMATURE':t.id=r
    for mod in o.modifiers:
        if mod.type=='ARMATURE':mod.object=r
    if o.type=='MESH' and o.data.shape_keys and o.data.shape_keys.animation_data:
        for f in o.data.shape_keys.animation_data.drivers:
            for v in f.driver.variables:
                for t in v.targets:
                    if isinstance(t.id,bpy.types.Object) and t.id.type=='ARMATURE':t.id=r
report={'objects':[{'name':o.name,'type':o.type,'vertices':len(o.data.vertices) if o.type=='MESH' else None,'hidden':o.hide_render,'materials':[m.name for m in o.data.materials] if o.type=='MESH' else []} for o in char.all_objects],'bones':{b.name:{'head':list(b.head_local),'tail':list(b.tail_local)} for b in r.data.bones},'head_shader_nodes':{m.name:[{'type':n.type,'attribute':getattr(n,'attribute_name',None)} for n in m.node_tree.nodes] for m in bpy.data.objects['HMC_Head_AnatomicalSurface'].data.materials if m and m.use_nodes}}
(A/'hondo_basis_inventory.json').write_text(json.dumps(report,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(A/'Hurricane_V2_with_Hondo_basis.blend'),compress=True);print('HONDO_BASIS_IMPORTED',len(char.all_objects))
