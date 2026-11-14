import bpy,json
R=bpy.data.objects['VanessaWarfield_Rig'];A=R.animation_data
print('ACTION',A.action.name if A and A.action else None)
print('CUSTOM_DRIVERS',[(f.data_path,f.driver.expression,[(v.name,v.targets[0].id.name if v.targets[0].id else '',v.targets[0].data_path) for v in f.driver.variables]) for f in A.drivers if f.data_path.startswith('[')])
print('NLA',len(A.nla_tracks))
A.action=None
exec(compile(open('G:/DEV/mask-project-mayhem/art_source/Manta/diagnose_character.py').read(),'<diag>','exec'))
