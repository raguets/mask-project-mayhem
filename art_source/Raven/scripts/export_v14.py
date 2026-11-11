from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Raven';C=P/'art_source/Calhoun_Burns'
text=(A/'scripts/export_v5.py').read_text(encoding='utf-8')
prefix=text.split("exec(compile((P/'art_source/shared_tools")[0]
exec(prefix)
EXPORT_JOB['source_blend']=str(A/'Raven_V14_Assembly.blend');EXPORT_JOB['manifest']=str(A/'component_exports_v14.json')
EXPORT_JOB['components']=EXPORT_JOB['components'][:2]
v,c=EXPORT_JOB['components']
v['output']=str(A/'Raven_V14_Vehicle.blend');v['scene_name']='Raven_V14_Vehicle'
v['help_text']='Raven V14 editable vehicle. Frame1/31 road;31-91 complete front roll including front tires;91-121 secondary front wheel tilt;151 deployed. Raven_Control: transform, hover_height presentation only, disc_launch. Roof thirds: center fixed, outer thirds integral to curved door wings. Curved trapezoidal windshield and extended very dark rear hatch; black rear door posts. Entire four-reactor cassette lifts197mm, horizontal rounded black top and side shell. Four persistent tires,90mm recessed wheel cannons with45deg deployment. Hidden kinematics/dimensions interpreted, not final game topology or flight/water physics. See validation and inspected renders.'
c['output']=str(C/'CalhounBurns_V2.blend');c['scene_name']='CalhounBurns_V2'
c['help_text']='Calhoun Burns V2: same editable body/head/rig, standing and seated via driving_pose0/1; mask_on false/true. in_vehicle0 for independent asset. Revised leg pose for shortened Raven fixed footwell. Mask V1 geometry unchanged; independent source retained. Face/anatomy from supplied illustration are authorized realistic interpretation. Hand/pedal contact and artistic fidelity remain to improve.'
assert not Path(v['output']).exists() and not Path(c['output']).exists()
exec(compile((P/'art_source/shared_tools/export_components.py').read_text(encoding='utf-8'),'<exports>','exec'))
