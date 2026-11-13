import unreal,json
from pathlib import Path
P=Path(unreal.Paths.project_dir()).resolve()
exec(compile((P/'Tools/Art/import_condor.py').read_text(encoding='utf-8-sig'),'<condor-assets>','exec'))
if not json.loads((P/'Saved/Art/condor-import.json').read_text())['passed']:raise RuntimeError('Condor import failed; see Saved/Art/condor-import.json')
exec(compile((P/'Tools/Art/import_brad_motion.py').read_text(encoding='utf-8-sig'),'<brad-motion>','exec'))
exec(compile((P/'Tools/Art/finalize_condor.py').read_text(encoding='utf-8-sig'),'<condor-contract>','exec'))
