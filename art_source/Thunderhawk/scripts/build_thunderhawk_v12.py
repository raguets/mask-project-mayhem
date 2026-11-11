"""V12: continuous shaped footwear from inspected toy reference, and pedal fit.

Run through the installed Blender MCP execute_code endpoint on the live V11.
Boot dimensions and interpreted cockpit geometry remain estimates.
"""
import bpy, bmesh, json, math
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem'); T=P/'art_source/Thunderhawk'
s=bpy.context.scene; r=bpy.data.objects['MattTrakker_Rig']
char=bpy.data.collections['MT11_Character']; cab=bpy.data.collections['THK11_Interior']
assert bpy.data.objects.get('MT_ContinuousFlightSuit')
backup=T/'Thunderhawk_V12_before_work.blend'
if not backup.exists():
    bpy.ops.wm.save_as_mainfile(filepath=str(backup),copy=True,compress=True)
for ob in list(char.objects):
    if ob.name.startswith(('MT_BootUpper_','MT_BootAnkle_','MT_BootSole_','MT_Tread_','MT_ToeSeam_')):
        bpy.data.objects.remove(ob,do_unlink=True)

def material(name,color,rough):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True; m.diffuse_color=(*color,1)
    bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough
    return m
leather=material('MT3_BootBlackLeather',(.014,.018,.022),.52)
rubber=bpy.data.materials['Spectrum2_Rubber']; red=bpy.data.materials['MT2_RedLeather']
for mat in [leather]:
    nodes=mat.node_tree.nodes; links=mat.node_tree.links
    if not any(n.name=='BootLeatherGrain' for n in nodes):
        n=nodes.new('ShaderNodeTexNoise'); n.name='BootLeatherGrain'; n.inputs['Scale'].default_value=310
        b=nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value=.15; b.inputs['Distance'].default_value=.0003
        links.new(n.outputs['Fac'],b.inputs['Height']); links.new(b.outputs['Normal'],next(n for n in nodes if n.type=='BSDF_PRINCIPLED').inputs['Normal'])

def boot_mesh(name,sd,sg,profile,mat,cuff=False):
    N=64; vv=[]; ff=[]
    for z,cx,rx,ry in profile:
        for i in range(N):
            a=math.tau*i/N; c=math.cos(a); q=math.sin(a)
            vv.append((cx+rx*math.copysign(abs(c)**.78,c),sg*.11+ry*q,z))
    for j in range(len(profile)-1):
        for i in range(N):ff.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
    ff.append(tuple(range(N-1,-1,-1))); ff.append(tuple((len(profile)-1)*N+i for i in range(N)))
    me=bpy.data.meshes.new(name+'_Editable'); me.from_pydata(vv,[],ff); me.update()
    bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free()
    ob=bpy.data.objects.new(name,me); char.objects.link(ob); me.materials.append(mat)
    if cuff:me.materials.append(red)
    for f in me.polygons:
        f.use_smooth=len(f.vertices)==4
        if cuff and f.center.z>.126:f.material_index=1
    foot=ob.vertex_groups.new(name='foot.'+sd); shin=ob.vertex_groups.new(name='shin.'+sd)
    for v in me.vertices:
        t=max(0,min(1,(v.co.z-.105)/.065)) if cuff else 0
        t=t*t*(3-2*t)
        if t<1:foot.add([v.index],1-t,'REPLACE')
        if t>0:shin.add([v.index],t,'REPLACE')
    mod=ob.modifiers.new('SameCharacterFootSkin','ARMATURE'); mod.object=r; mod.use_deform_preserve_volume=True
    ob.parent=r
    ob['reference']='Supplied photograph images (3).jpg: black footwear and red ankle cuff; geometry and dimensions estimated.'
    return ob

for sg,sd in [(1,'L'),(-1,'R')]:
    boot_mesh('MT_BootSole_'+sd,sd,sg,[
        (.006,.055,.119,.053),(.010,.055,.123,.056),(.031,.055,.123,.056),(.037,.055,.120,.054)],rubber)
    boot_mesh('MT_BootUpper_'+sd,sd,sg,[
        (.034,.055,.118,.053),(.042,.055,.119,.054),(.055,.050,.116,.053),
        (.071,.039,.106,.052),(.088,.020,.084,.051),(.108,.003,.062,.051),
        (.125,-.001,.053,.051),(.140,-.002,.051,.052),(.170,-.002,.050,.052),
        (.195,-.001,.052,.053),(.201,-.001,.051,.052)],leather,cuff=True)
    # Attached upper welt and seam follow the same deforming boot, with no floating toe arcs.
    boot_mesh('MT_BootWelt_'+sd,sd,sg,[
        (.032,.055,.121,.055),(.036,.055,.121,.055),(.039,.055,.119,.054)],leather)

r['asset_version']='Matt Trakker V3 / Spectrum V2'
r['driving_pose']=1; r['mask_on']=False; r.location=(0,.4,0); r.update_tag(); s.frame_set(97)
bpy.context.view_layer.update()

def geometry(ob):
    ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get()); me=ev.to_mesh()
    pts=[ev.matrix_world@v.co for v in me.vertices]; ev.to_mesh_clear(); return pts

# Match clutch and accelerator to the evaluated toe surfaces. These positions are
# an explicitly authorized interior interpretation, not a photographed mechanism.
pedal_report=[]
for idx,sd in [(0,'R'),(2,'L')]:
    points=geometry(bpy.data.objects['MT_BootUpper_'+sd])
    toe=max(v.x for v in points)
    zone=[v for v in points if v.x>toe-.008]
    target=Vector((toe+.0115,sum(v.y for v in zone)/len(zone),sum(v.z for v in zone)/len(zone)))
    ob=bpy.data.objects['THK_Pedal'+str(idx)]
    # Existing pedal has its origin centered. Move its related stem/grips with it.
    shift=target-ob.matrix_world.translation
    for obj in cab.objects:
        if obj.name in ('THK_Pedal'+str(idx),'THK_PedalStem'+str(idx)) or obj.name.startswith('THK_PedalGrip'+str(idx)):
            obj.location+=shift
    pedal_report.append({'pedal':ob.name,'boot':sd,'toe_estimate':list(target),'shift':list(shift)})
s.name='THK_V12_Footwear_and_DrivingFit'; s['THK_Version']='V12'
s['V12_Changes']='Continuous fitted black/red footwear; evaluated toe/pedal alignment. Estimated toy-based geometry; same skinned character.'
s['V12_Source']='Live V11 scene preserved in Thunderhawk_V12_before_work.blend'
# Keep armature editable without covering the character in normal inspection.
r.show_in_front=False
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.overlay.show_extras=False; area.spaces.active.overlay.show_relationship_lines=False
bpy.ops.object.select_all(action='DESELECT')
s.render.filepath=str(T/'renders/v12/preview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(T/'Thunderhawk_V12.blend'),compress=True)
(T/'footwear_changes_v12.json').write_text(json.dumps({'pedals':pedal_report,'reference_category':'toy photograph; estimated geometry'},indent=2))
print('V12_FOOTWEAR_AND_PEDAL_ALIGNMENT_SAVED',json.dumps(pedal_report))
