from pathlib import Path
import unreal
P=Path(unreal.Paths.project_dir()).resolve()
code=(P/'Tools/Art/import_calhoun_motion.py').read_text(encoding='utf-8-sig').replace('Calhoun','Brad').replace('calhoun','brad').replace('Raven','Condor').replace('raven','condor')
exec(compile(code,'<brad-import>','exec'))
