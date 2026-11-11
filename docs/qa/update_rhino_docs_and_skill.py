"""Mirror tested helpers into the reusable skill and retain the pre-update copies."""
import ast,hashlib,json,shutil,os
from pathlib import Path
P=Path(__file__).resolve().parents[2];skill=P/'.agents/skills/mask-asset-production';installed=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'skills/mask-asset-production'
backup=P/'docs/qa/skill_before_rhino_helpers'
if not backup.exists():shutil.copytree(skill,backup)
for name in ['render_review_queue.py','export_components.py']:shutil.copy2(P/'art_source/shared_tools'/name,skill/'scripts'/name)
for path in (skill/'scripts').glob('*.py'):ast.parse(path.read_text(encoding='utf-8-sig'),filename=str(path))
for path in skill.rglob('*'):
 if path.is_file():
  target=installed/path.relative_to(skill);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
checks={str(path.relative_to(skill)):hashlib.sha256(path.read_bytes()).hexdigest() for path in skill.rglob('*') if path.is_file()}
assert all(hashlib.sha256((installed/name).read_bytes()).hexdigest()==digest for name,digest in checks.items())
(P/'docs/qa/skill_update_rhino_v2.json').write_text(json.dumps({'project_source':str(skill),'installed':str(installed),'hashes_match':True,'sha256':checks,'behavioral_evidence':['art_source/Rhino/renders/v2_final/manifest.json','art_source/Rhino/standalone_validation_v2.json','docs/qa/rhino_active_review_guard.json'],'syntax_passed':True},indent=2),encoding='utf-8')
readme=P/'README.md';text=readme.read_text(encoding='utf-8-sig')
if '## Rhino V2' not in text:
 lines=text.splitlines();lines[0]='# M.A.S.K. Project Mayhem';text='\n'.join(lines)+'\n'
 intro='''
## Rhino V2 — Alex Sector et Bruce Sato

Assemblage : `art_source/Rhino/Rhino_V2.blend`. Véhicule indépendant : `art_source/Rhino/Rhino_V2_Vehicle.blend`. Module arrière autonome : `art_source/Rhino/Rhino_RearVehicle_V1.blend`. Alex et Bruce ont chacun une source articulée et un masque indépendant dans `art_source/Alex_Sector/` et `art_source/Bruce_Sato/`.

V2 : capot abaissé, vitres supérieures abaissées et évasées en plan, petit radar tournant, grand coffre reculant avant la sortie d’un missile noir unique. Pare-buffle avancé, échappements rabattus en canons et module détachable ; roues centrales extérieures conservées au camion, intérieures au module. Timeline 1–241 : route à l’image 1, transformé à l’image 151.

Commandes et limites : `art_source/Rhino/README.md`. Références : `docs/art/Rhino_reference_review_v1.md`. Compte rendu : `docs/progress/2026-11-03-Rhino-V2.md`. Rendus : `art_source/Rhino/renders/v2_final/` ; rapports `validation_v2.json`, `cabin_fit_v2.json` et `standalone_validation_v2.json` dans le même dossier source. Versions antérieures conservées.

## Thunderhawk V14 — Matt Trakker et Spectrum

'''
 text=text.replace('# M.A.S.K. Project Mayhem\n','# M.A.S.K. Project Mayhem\n'+intro,1)
text=text.replace('art_source/Rhino/renders/v2/','art_source/Rhino/renders/v2_final/');readme.write_text(text,encoding='utf-8')
print('RHINO_DOCUMENTATION_AND_SKILL_COPIES_UPDATED')
