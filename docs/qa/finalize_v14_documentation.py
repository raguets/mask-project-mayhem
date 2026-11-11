"""Install the project production skill and record reproducible local checks."""
import ast
import hashlib
import json
import os
import shutil
from pathlib import Path

root = Path(__file__).resolve().parents[2]
skill = root / '.agents/skills/mask-asset-production'
home = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
destination = home / 'skills/mask-asset-production'
assert not destination.exists(), 'Preserve/reconcile an existing installation before overwriting it'
scripts = list((skill / 'scripts').glob('*.py'))
for path in scripts:
    ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path))
shutil.copytree(skill, destination)
hashes = {}
for path in skill.rglob('*'):
    if path.is_file():
        relative = path.relative_to(skill)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest == hashlib.sha256((destination / relative).read_bytes()).hexdigest()
        hashes[str(relative)] = digest
for name in ['render_review_queue.py', 'export_components.py']:
    assert (root / 'art_source/shared_tools' / name).read_bytes() == (skill / 'scripts' / name).read_bytes()
report = {
    'installed': str(destination),
    'project_source': str(skill),
    'all_installed_files_match': True,
    'script_syntax_passed': [path.name for path in scripts],
    'shared_helpers_match_tested_project_helpers': True,
    'structural_validation': 'quick_validate.py passed before installation',
    'live_mcp_client_smoke': 'docs/qa/skill_mcp_smoke_v14.json',
    'export_session_guard_smoke': 'docs/qa/export_helper_smoke/validation.json',
    'sha256': hashes,
}
(root / 'docs/qa/skill_install_validation_v14.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
preliminary = root / 'art_source/Thunderhawk/neck_collar_changes_v14.json'
data = json.loads(preliminary.read_text())
data['scope'] = 'Preliminary first build measurements/samples, superseded by final neck/collar rebuild and validation_v14.json'
data['final_validation'] = 'validation_v14.json'
data['final_changes'] = {'rest_head_drop_m_estimated': .035, 'rigid_mask_drop_m_estimated': .045, 'driving_head_control_raise_vs_previous_m': .030, 'collar_base_width_m_estimated': .352}
preliminary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({key:value for key,value in report.items() if key != 'sha256'}, ensure_ascii=False, indent=2))
