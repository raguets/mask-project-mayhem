import unreal,json
from pathlib import Path
P=Path(unreal.Paths.project_dir()).resolve();RAVEN_KEEP_EDITOR=True
# Run with -run=pythonscript. The commandlet owns shutdown; quit_editor would
# tear down Slate while Python's editor-asset notifications are still queued.
exec(compile((P/'Tools/Art/import_raven.py').read_text(encoding='utf-8-sig'),'<raven-import-adapter>','exec'))
if not json.loads((P/'Saved/Art/raven-import.json').read_text())['passed']:raise RuntimeError('Raven asset import failed; see report')
exec(compile((P/'Tools/Art/import_calhoun_motion.py').read_text(encoding='utf-8-sig'),'<calhoun-import-adapter>','exec'))
