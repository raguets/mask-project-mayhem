"""Import Manta using Raven's fixed-wing material and dynamics contract."""
from pathlib import Path
import unreal
P=Path(unreal.Paths.project_dir()).resolve()
code=(P/'Tools/Art/import_raven.py').read_text(encoding='utf-8-sig')
code=code.replace('Raven','Manta').replace('raven','manta').replace('RAVEN','MANTA').replace('Calhoun','Vanessa').replace('RV_','MA_')
code=code.replace("driver_name='Vanessa Burns',mask_name='Gulliver'", "driver_name='Vanessa Warfield',mask_name='Whip',faction=unreal.MaskFaction.VENOM")
code=code.replace('clearance_extent=unreal.Vector(245,185,125)','clearance_extent=unreal.Vector(250,360,125)')
code=code.replace('exec(compile(code,', '''code=code.replace("options.set_editor_property('reduction_settings',lods);editor.set_lods(mesh,options)", "options.set_editor_property('reduction_settings',lods)\\n        if editor:editor.set_lods(mesh,options)\\n        else:report['static_lod_note']='Commandlet: reduced source LOD0 retained.'")
exec(compile(code,''')
# The adapter's inner template must replace Hondo with Vanessa, not Calhoun.
code=code.replace(".replace('Hondo','Vanessa')", ".replace('Hondo','Vanessa')")
exec(compile(code,'<manta-import>','exec'))
