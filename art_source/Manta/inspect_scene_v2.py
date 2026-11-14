import bpy,json
print('COLLECTIONS',[(c.name,len(c.objects)) for c in bpy.data.collections])
for n in ['MA_MainBody','MA_Windshield','MA_Key','VW_ContinuousBodyAndFace','VW_Eyeball_0','VanessaWarfield_Rig']:
 o=bpy.data.objects[n];print(n,'collections',[c.name for c in o.users_collection],'loc',list(o.location),'world',list(o.matrix_world.translation),'materials',[m.name if m else None for m in o.data.materials] if o.type=='MESH' else [])
 if o.type=='MESH':print('vertices',[(list(o.data.vertices[i].co),[(g.group,g.weight) for g in o.data.vertices[i].groups]) for i in [0,len(o.data.vertices)//2]])

