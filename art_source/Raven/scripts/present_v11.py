import bpy,json
from pathlib import Path
from mathutils import Vector
A=Path('G:/DEV/mask-project-mayhem/art_source/Raven');S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
root=bpy.data.objects['Raven_Control'];R=bpy.data.objects['CalhounBurns_Rig'];root['hover_height']=0.;root['disc_launch']=0.;R['in_vehicle']=1.;R['driving_pose']=1.;R['mask_on']=False;R.update_tag();S.frame_set(1);bpy.context.view_layer.update()
bpy.ops.object.select_all(action='DESELECT');root.select_set(True);bpy.context.view_layer.objects.active=root
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            space=area.spaces.active;space.shading.type='MATERIAL';space.overlay.show_extras=False;space.region_3d.view_location=(0,0,.65);space.region_3d.view_distance=5.5;space.region_3d.view_rotation=(Vector((6,-6,3))-Vector((0,0,.65))).to_track_quat('Z','Y')
        elif area.type=='PROPERTIES':
            area.spaces.active.pin_id=root
            try:area.spaces.active.context='OBJECT'
            except TypeError:pass
text=bpy.data.texts.get('ASSET_README') or bpy.data.texts.new('ASSET_README');text.clear();text.write('Raven V11 first reference-based pass. Select Raven_Control. Frames1/31 road;31–91 entire front unit rolls with wheels,91–121 secondary front wheel fold;151 deployed. hover_height is presentation only. Disc independent. Short vertical rear cover, curved doors, recessed diametric rim guns raising45deg. Calhoun same articulated body/head with driving_pose and mask_on. Independent files exported/reopened; see external README and reports. Fine realism, game topology and full volume clearances remain work in progress.')
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Raven_V11_Assembly.blend'),compress=True)
print(json.dumps({'file':bpy.data.filepath,'frame':S.frame_current,'selected':root.name,'review_lock':bool(bpy.app.driver_namespace.get('_mask_asset_review_active')),'objects':len(S.objects),'saved':True}))
