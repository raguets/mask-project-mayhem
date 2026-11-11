"""Verify vehicle provenance and expose existing single-character pose controls.

Execute in Blender through the installed MCP. No character meshes are created.
"""
import bpy,json,hashlib,array
from pathlib import Path
from datetime import datetime
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Matt_Trakker';T=P/'art_source/Thunderhawk'
if bpy.data.is_dirty:
    backup=A/('Matt_controls_prior_session_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.blend')
    bpy.ops.wm.save_as_mainfile(filepath=str(backup),copy=True,compress=True)
if not bpy.data.objects.get('THK_Hood'):
    bpy.ops.wm.open_mainfile(filepath=str(T/'Thunderhawk_V12.blend'))
source_file=bpy.data.filepath
def fingerprints():
    result={}
    for collection in ['MT11_Character','Spectrum11_Asset']:
        for ob in bpy.data.collections[collection].all_objects:
            if ob.type!='MESH':continue
            xyz=array.array('f',[0.0])*(len(ob.data.vertices)*3);ob.data.vertices.foreach_get('co',xyz)
            indices=array.array('i',[0])*len(ob.data.loops);ob.data.loops.foreach_get('vertex_index',indices)
            result[ob.name]=hashlib.sha256(xyz.tobytes()+indices.tobytes()).hexdigest()
    return result
source=fingerprints()
bpy.ops.wm.open_mainfile(filepath=str(A/'MattTrakker_V3.blend'))
standalone=fingerprints()
assert source==standalone,'Standalone meshes differ from the live vehicle; stop rather than replace Matt.'
backup=A/'MattTrakker_V3_before_control_presentation.blend'
if not backup.exists():bpy.ops.wm.save_as_mainfile(filepath=str(backup),copy=True,compress=True)
s=bpy.context.scene;r=bpy.data.objects['MattTrakker_Rig'];mask=bpy.data.collections['Spectrum11_Asset']
assert sum(o.type=='ARMATURE' for o in s.objects)==1
assert sum(o.name=='MT_Head_AnatomicalSurface' for o in s.objects)==1
r.id_properties_ui('driving_pose').update(min=0,max=1,soft_min=0,soft_max=1,description='Position de Matt : 0 = debout ; 1 = assis au volant. Même personnage et mêmes maillages.')
r.id_properties_ui('mask_on').update(description='Afficher Spectrum sur la même tête : coché = casque visible ; décoché = visage visible.')
pointer={o.name:o.data.as_pointer() for o in bpy.data.collections['MT11_Character'].all_objects if o.type=='MESH'}
states=[]
for drive in [0,1]:
    for masked in [False,True]:
        r['driving_pose']=drive;r['mask_on']=masked;r.update_tag();s.frame_set(1+drive);bpy.context.view_layer.update()
        visible=sum(not o.hide_render for o in mask.objects)
        assert (visible>0)==masked
        assert not bpy.data.objects['MT_Head_AnatomicalSurface'].hide_render
        assert all(ob.data.as_pointer()==pointer[ob.name] for ob in bpy.data.collections['MT11_Character'].all_objects if ob.type=='MESH')
        dg=bpy.context.evaluated_depsgraph_get();head=bpy.data.objects['MT_Head_AnatomicalSurface'].evaluated_get(dg)
        states.append({'driving_pose':drive,'mask_on':masked,'mask_visible_parts':visible,
                       'same_character_meshes':True,'face_retained_under_helmet':True,
                       'head_world':list(head.matrix_world@Vector(head.bound_box[0]))})
helptext='''MATT TRAKKER — UN SEUL PERSONNAGE\n\nCe fichier reprend les maillages du Matt de Thunderhawk V12, sans reconstruction.\nUne seule armature, un seul corps et une seule tête conservée sous Spectrum.\n\nSélectionner MattTrakker_Rig. Propriétés de l'objet > Propriétés personnalisées :\n\n  driving_pose = 0 : DEBOUT\n  driving_pose = 1 : ASSIS / CONDUITE\n  mask_on décoché : VISAGE VISIBLE\n  mask_on coché   : CASQUE SPECTRUM VISIBLE\n\nLes deux commandes sont indépendantes : les quatre combinaisons sont possibles.\nLe casque reste attaché à l'os de tête ; les cheveux s'effacent sous le casque.\nPour revenir à l'état de présentation : driving_pose=0, mask_on=False.\n\nLa pose assise correspond aux dimensions du véhicule source ; elle ne crée pas\nune seconde instance de Matt. Les cages de vêtements masquées sont des sources\ntechniques conservées, pas des personnages de remplacement.\n\nRéférences : portrait dessiné et photos de figurines/répliques fournis.\nFinition artistique, déformations et contacts siège/combinaison restent à affiner.\n'''
txt=bpy.data.texts.get('LIRE_MOI_Matt_Trakker') or bpy.data.texts.new('LIRE_MOI_Matt_Trakker');txt.clear();txt.write(helptext)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='PROPERTIES':
            area.spaces.active.context='OBJECT';area.spaces.active.pin_id=r
        elif area.type=='TEXT_EDITOR':area.spaces.active.text=txt
        elif area.type=='VIEW_3D':
            area.spaces.active.overlay.show_extras=False
            area.spaces.active.shading.color_type='MATERIAL'
            view=area.spaces.active.region_3d;view.view_location=(0,0,.94);view.view_distance=3.0
            view.view_rotation=(Vector((3,4,2))-view.view_location).to_track_quat('Z','Y');view.view_perspective='PERSP'
r.location=(0,0,0);r['driving_pose']=0;r['mask_on']=False;r.update_tag();s.frame_set(1);bpy.context.view_layer.update()
bpy.ops.object.select_all(action='DESELECT');r.hide_set(False);r.select_set(True);bpy.context.view_layer.objects.active=r
bpy.ops.wm.save_as_mainfile(filepath=str(A/'MattTrakker_V3.blend'),compress=True)
report={'source_vehicle':source_file,'identical_mesh_fingerprints':True,'mesh_count_compared':len(source),
        'one_armature_one_head':True,'four_states':states,'default':'standing, no helmet','controls':{'driving_pose':'0 debout / 1 assis','mask_on':'False visage / True casque'},
        'geometry_changed':False,'character_duplicates_created':0}
(A/'pose_controls_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
(A/'COMMANDES_MATT.txt').write_text(helptext,encoding='utf-8')
print('MATT_SAME_VEHICLE_MESHES_CONTROLS_READY',json.dumps(report))
