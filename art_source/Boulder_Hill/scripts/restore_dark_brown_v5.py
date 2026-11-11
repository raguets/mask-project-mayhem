"""Palette-only correction requested by user; preserve geometry and mechanisms."""
import bpy,json,hashlib,struct,datetime
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Boulder_Hill'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
opened=bpy.data.filepath
backup=A/('Session_before_color_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.blend')
bpy.ops.wm.save_as_mainfile(filepath=str(backup),copy=True,compress=True)
# The active editor had an earlier session open. Work on the latest validated source,
# keeping that editor session intact in the backup above.
bpy.ops.wm.open_mainfile(filepath=str(A/'BoulderHill_V4_Assembly.blend'))
S=bpy.context.scene
def geometry_digest():
    result={}
    for o in S.objects:
        if o.type!='MESH':continue
        h=hashlib.sha256()
        for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
        for f in o.data.polygons:h.update(struct.pack('<'+'I'*len(f.vertices),*f.vertices))
        result[o.name]=h.hexdigest()
    return result
before=geometry_digest();mat=bpy.data.materials['BH_Sandstone'];old=[]
for node in mat.node_tree.nodes:
    if node.type=='VALTORGB':
        old.append([list(e.color) for e in node.color_ramp.elements])
        dark=(.055,.016,.008,1);light=(.180,.060,.027,1)
        for e in node.color_ramp.elements:e.color=tuple(dark[i]*(1-e.position)+light[i]*e.position for i in range(4))
mat.diffuse_color=(.1175,.038,.0175,1)
mat['palette_note']='User-requested dark brown, matched visually to supplied toy photograph. V5 changes palette only; same light, geometry, roughness, bump and mechanisms.'
after=geometry_digest();assert before==after
S['BoulderVersion']='V5';S['color_correction']='Dark brown rock restored from supplied photograph. Palette only; V4 geometry and animation retained.';S.name='BoulderHill_V5_Assembly'
bpy.context.view_layer.update();S.frame_set(211)
bpy.ops.wm.save_as_mainfile(filepath=str(A/'BoulderHill_V5_Assembly.blend'),compress=True)
report={'opened_session':opened,'session_backup':str(backup),'source':'BoulderHill_V4_Assembly.blend','output':'BoulderHill_V5_Assembly.blend','mesh_geometry_unchanged':before==after,'meshes_checked':len(before),'old_ramp':old,'new_ramp':[[list(e.color) for e in n.color_ramp.elements] for n in mat.node_tree.nodes if n.type=='VALTORGB'],'diffuse':list(mat.diffuse_color)}
(A/'color_correction_v5.json').write_text(json.dumps(report,indent=2))
print('DARK_BROWN_V5_SAVED GEOMETRY_UNCHANGED',len(before))
