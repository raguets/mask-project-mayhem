"""Generate the refined native paint build from the preserved V2 construction."""
from pathlib import Path
P=Path(__file__).resolve().parents[3];A=P/'art_source/Hurricane';code=(A/'scripts/paint_flames_v2.py').read_text(encoding='utf-8')
start=code.index('def tint(t):');end=code.index('def project_decal',start)
code=code[:start]+'''def tint(t):
    t=max(0,min(1,t));a=(.95,.62,.010);b=(.98,.15,.006);c=(.65,.018,.006)
    if t<.35:return a+(1,)
    if t<.85:u=(t-.35)/.50;return tuple(x*(1-u)+y*u for x,y in zip(a,b))+(1,)
    u=(t-.85)/.15;return tuple(x*(1-u)+y*u for x,y in zip(b,c))+(1,)
def rounded(poly):
    pts=[Vector(p) for p in poly];out=[]
    def tangent(i):
        a=pts[(i-1)%len(pts)]-pts[i];b=pts[(i+1)%len(pts)]-pts[i]
        if a.normalized().dot(b.normalized())>.62:return Vector((0,0))
        return (pts[(i+1)%len(pts)]-pts[(i-1)%len(pts)])*.16
    for i,a in enumerate(pts):
        b=pts[(i+1)%len(pts)];c=a+tangent(i);d=b-tangent((i+1)%len(pts))
        for k in range(6):
            t=k/6;p=a*(1-t)**3+3*c*(1-t)**2*t+3*d*(1-t)*t*t+b*t**3;out.append(tuple(p))
    return out
''' +code[end:]
code=code.replace("def project_decal(name,source,poly,side,root,flowrange):", "def project_decal(name,source,poly,side,root,flowrange):\n    poly=rounded(poly)")
needle="    ob['paint_note']='Editable conformed paint geometry"
index=code.index(needle)
code=code[:index]+'''    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.000005);bm.to_mesh(ob.data);bm.free()
    sub=ob.modifiers.new('FinePaintTessellation','SUBSURF');sub.subdivision_type='SIMPLE';sub.levels=1;sub.render_levels=2
    sw=ob.modifiers.new('ConformedPaint','SHRINKWRAP');sw.target=o;sw.wrap_method='NEAREST_SURFACEPOINT';sw.offset=.0018
''' +code[index:]
code=code.replace("S.frame_set(1);bpy.context.view_layer.update()", "S.frame_set(1);bpy.context.view_layer.update()\nfor o in list(S.objects):\n    if str(o.get('HU_group','')).startswith('paint_'):bpy.data.objects.remove(o,do_unlink=True)")
code=code.replace("Hurricane_V2_Assembly.blend","Hurricane_V4_Assembly.blend")
(A/'scripts/paint_flames_v4.py').write_text(code,encoding='utf-8')
print('Refined paint build prepared')
