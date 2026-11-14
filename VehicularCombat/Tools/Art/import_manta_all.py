import unreal,json
from pathlib import Path
P=Path(unreal.Paths.project_dir()).resolve();MANTA_KEEP_EDITOR=True
# Run with -run=pythonscript. The commandlet owns shutdown; quit_editor would
# tear down Slate while Python's editor-asset notifications are still queued.
exec(compile((P/'Tools/Art/import_manta.py').read_text(encoding='utf-8-sig'),'<manta-import-adapter>','exec'))
if not json.loads((P/'Saved/Art/manta-import.json').read_text())['passed']:raise RuntimeError('Manta asset import failed; see report')
exec(compile((P/'Tools/Art/import_vanessa_motion.py').read_text(encoding='utf-8-sig'),'<vanessa-import-adapter>','exec'))

exec(compile((P/'Tools/Art/finalize_manta.py').read_text(encoding='utf-8-sig'),'<manta-contract>','exec'))
