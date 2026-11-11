import json,hashlib,datetime
from pathlib import Path
P=Path(__file__).resolve().parents[3];A=P/'art_source/Boulder_Hill'
correction=json.loads((A/'color_light_v6.json').read_text());reopen=json.loads((P/'docs/qa/boulder_standalone_v6.json').read_text());renders=json.loads((A/'renders/v6/manifest.json').read_text())
assert correction['geometry_unchanged'] and renders['status']=='complete' and len(renders['renders'])==2
assert reopen['independent']['demo_objects']==0
assert all(not s['invalid_drivers'] for item in reopen.values() for s in item['states'])
result={'version':'V6','date_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Warm intermediate brown and brighter daylight, following user rejection of V4 beige and V5 excessive darkness.','geometry_unchanged_from_v4':True,'geometry_validation':'validation_v4.json','render_views_inspected':2,'appearance_report':'color_light_v6.json','reopen_report':'../../docs/qa/boulder_standalone_v6.json','sources':{name:{'bytes':(A/name).stat().st_size,'sha256':hashlib.sha256((A/name).read_bytes()).hexdigest()} for name in ['BoulderHill_V6_Assembly.blend','BoulderHill_V6_Base.blend']}}
(A/'validation_v6.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
(P/'docs/progress/2026-11-05-Boulder-Hill-V6-couleur-lumiere.md').write_text('''# Boulder Hill V6 — couleur et lumière

L’utilisateur a signalé le passage involontaire du marron foncé à un beige clair. La reprise V5 était ensuite trop sombre, et la scène manquait de lumière. V6 adopte un marron chaud intermédiaire, renforce le monde lumineux et l’éclairage principal, ajoute un grand éclairage frontal doux et relève légèrement l’exposition. Le viewport utilise les lumières et le monde de la scène.

La géométrie et les mécanismes V4 sont conservés, vérifiés par empreintes des meshes avant/après. Les contrôles géométriques V4 restent applicables ; ils ne sont pas présentés comme de nouveaux tests. Deux rendus de couleur et d’éclairage, station et défense, ont été inspectés. Assemblage V6 et base indépendante V6 sauvegardés puis rouverts : drivers valides, éclairage présent dans les deux, aucun véhicule de démonstration dans la base indépendante. L’assemblage est laissé ouvert à l’image 211.

Fichiers actifs, commandes, références et limites : `art_source/Boulder_Hill/README.md`. Rapports : `color_light_v6.json`, `validation_v6.json` et `docs/qa/boulder_standalone_v6.json`. Les sources V4, V5 et la session précédemment ouverte ont été préservées.
''',encoding='utf-8')
print('V6 appearance and reopened sources verified')
