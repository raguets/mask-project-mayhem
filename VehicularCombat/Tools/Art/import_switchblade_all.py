import unreal,json
from pathlib import Path
P=Path(unreal.Paths.project_dir()).resolve()
exec(compile((P/'Tools/Art/import_switchblade.py').read_text(encoding='utf-8-sig'),'<switchblade-assets>','exec'))
if not json.loads((P/'Saved/Art/switchblade-import.json').read_text())['passed']:raise RuntimeError('Condor import failed; see Saved/Art/switchblade-import.json')
exec(compile((P/'Tools/Art/import_miles_motion.py').read_text(encoding='utf-8-sig'),'<miles-motion>','exec'))
exec(compile((P/'Tools/Art/finalize_switchblade.py').read_text(encoding='utf-8-sig'),'<switchblade-contract>','exec'))
