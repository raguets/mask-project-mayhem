import bpy,json
from pathlib import Path
from mathutils import Vector
S=bpy.context.scene;out=[]
for code,person in [('AS','AlexSector_Rig'),('BS','BruceSato_Rig')]:
 r=bpy.data.objects[person];saved=(r['driving_pose'],r['mask_on'],r.location.copy());r['driving_pose']=1;r['mask_on']=True;r.location=(0,0,0);r.update_tag();bpy.context.view_layer.update()
 for ob in bpy.data.collections[code+'_Character'].all_objects:
  if ob.type!='MESH' or ob.hide_render:continue
  ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();pts=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear();bounds=[[min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]]
  out.append({'name':ob.name,'bounds':bounds,'materials':[m.name for m in ob.data.materials if m],'modifiers':[(m.name,m.type) for m in ob.modifiers]})
 r['driving_pose'],r['mask_on'],r.location=saved;r.update_tag()
Path('G:/DEV/mask-project-mayhem/docs/qa/rhino_character_extents.json').write_text(json.dumps(out,indent=2));print('CHARACTER_EXTENTS_RECORDED')
