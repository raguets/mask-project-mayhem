"""Read-only geometric inspection. No scene/frame changes, save, or mesh writes.
Run in Blender via MCP execute_code, or against the saved file in a separate process.
All bmesh instances are independent memory copies.
"""
import bpy, bmesh, json, math, hashlib
from collections import Counter
from mathutils import Vector

scene = bpy.context.scene
def digest():
    h=hashlib.sha256()
    for ob in sorted(scene.objects, key=lambda o:o.name):
        h.update(ob.name.encode())
        h.update(str([list(row) for row in ob.matrix_world]).encode())
        if ob.type=='MESH':
            for v in ob.data.vertices: h.update(str(tuple(v.co)).encode())
            for p in ob.data.polygons: h.update(str(tuple(p.vertices)).encode())
    return h.hexdigest()
before = digest()
report={'filepath':bpy.data.filepath,'is_dirty_before':bpy.data.is_dirty,
        'frame':scene.frame_current,'blender':bpy.app.version_string,
        'units':scene.unit_settings.system,'scale_length':scene.unit_settings.scale_length,
        'object_types':dict(Counter(o.type for o in scene.objects)),
        'objects':[],'hash_before':before}
dg=bpy.context.evaluated_depsgraph_get()
for ob in sorted(scene.objects,key=lambda o:o.name):
    if ob.type!='MESH' or not ob.name.startswith('THK_'): continue
    me=ob.data
    bm=bmesh.new(); bm.from_mesh(me)
    r={'name':ob.name,'parent':ob.parent.name if ob.parent else None,
       'vertices':len(me.vertices),'edges':len(me.edges),'faces':len(me.polygons),
       'triangles':sum(len(p.vertices)==3 for p in me.polygons),
       'quads':sum(len(p.vertices)==4 for p in me.polygons),
       'ngons':sum(len(p.vertices)>4 for p in me.polygons),
       'max_polygon_sides':max((len(p.vertices) for p in me.polygons),default=0),
       'boundary_edges':sum(e.is_boundary for e in bm.edges),
       'wire_edges':sum(e.is_wire for e in bm.edges),
       'edges_over_two_faces':sum(len(e.link_faces)>2 for e in bm.edges),
       'inconsistent_manifold_edges':sum(e.is_manifold and not e.is_contiguous for e in bm.edges),
       'isolated_vertices':sum(not v.link_edges for v in bm.verts),
       'zero_length_edges':sum(e.calc_length()<1e-7 for e in bm.edges),
       'zero_area_faces':sum(f.calc_area()<1e-12 for f in bm.faces),
       'modifiers':[{'name':m.name,'type':m.type,**({'width':m.width,'segments':m.segments} if m.type=='BEVEL' else {}),**({'thickness':m.thickness} if m.type=='SOLIDIFY' else {})} for m in ob.modifiers],
       'subdivision':any(m.type=='SUBSURF' for m in ob.modifiers),
       'scale':list(ob.scale),'dimensions':list(ob.dimensions),'world_origin':list(ob.matrix_world.translation),
       'smooth_faces':sum(p.use_smooth for p in me.polygons),'uv_layers':len(me.uv_layers)}
    # Planarity deviation, relevant to uncontrolled boolean n-gons.
    deviations=[]
    for f in bm.faces:
        if len(f.verts)>4:
            c=f.calc_center_median(); deviations.append(max(abs((v.co-c).dot(f.normal)) for v in f.verts))
    r['max_ngon_nonplanarity_m']=max(deviations,default=0)
    bm.free()
    eo=ob.evaluated_get(dg); em=eo.to_mesh()
    eb=bmesh.new(); eb.from_mesh(em)
    em.calc_loop_triangles()
    r['evaluated']={'vertices':len(em.vertices),'faces':len(em.polygons),
        'triangles':len(em.loop_triangles),'boundary_edges':sum(e.is_boundary for e in eb.edges),
        'edges_over_two_faces':sum(len(e.link_faces)>2 for e in eb.edges),
        'zero_area_faces':sum(f.calc_area()<1e-12 for f in eb.faces)}
    eb.free();eo.to_mesh_clear()
    report['objects'].append(r)
report['totals']={k:sum(o[k] for o in report['objects']) for k in ('vertices','edges','faces','triangles','quads','ngons','boundary_edges','edges_over_two_faces','isolated_vertices','zero_area_faces')}
report['evaluated_totals']={k:sum(o['evaluated'][k] for o in report['objects']) for k in ('vertices','faces','triangles','boundary_edges','edges_over_two_faces','zero_area_faces')}
report['hash_after']=digest()
report['geometry_and_transforms_unchanged']=before==report['hash_after']
report['is_dirty_after']=bpy.data.is_dirty
print('THK_READONLY_AUDIT_JSON='+json.dumps(report))
